# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/ras.c

Purpose: Implements pSeries RAS interrupt handling, EPOW/power event parsing, hotplug event dispatch, RTAS hardware error logging, and FWNMI machine-check recovery.

Important APIs/types/functions: Defines RTAS log buffer/lock, `struct pseries_mc_errorlog`, RAS IRQ init functions, `ras_hotplug_interrupt()`, `ras_epow_interrupt()`, `ras_error_interrupt()`, FWNMI helpers, `pSeries_system_reset_exception()`, `mce_handle_error()`, `pSeries_machine_check_log_err()`, `pSeries_machine_check_exception()`, and `pseries_machine_check_realmode()`.

Control flow: Init registers event-source IRQs for hotplug, internal errors, and EPOW. IRQ handlers call RTAS `check-exception` into a shared buffer under spinlock, log or queue events, and power off for fatal cases. FWNMI paths validate firmware save pointers, copy RTAS logs into per-CPU PACA buffers, translate RTAS MCE sections into generic machine-check events, perform limited real-mode recovery for ERAT/SLB, and later decide whether to recover, signal, die, or panic.

State and persistence: Global state includes the shared RTAS log buffer, `ras_check_exception_token`, EPOW event count, FWNMI token globals from setup, and per-CPU PACA MCE buffers allocated elsewhere.

Dependencies and integration points: Integrates with RTAS, pseries error log parsing, DLPAR workqueues, poweroff/reboot paths, machine-check core, SLB/ERAT flushing, SMP NMI IPI handling, and `setup.c` machine callbacks.

Risks: The shared log buffer is interrupt-context state guarded by a spinlock; hotplug handler assumes a hotplug section exists before dereferencing. FWNMI recovery must release `ibm,nmi-interlock` promptly without losing logs. Machine-check recovery decisions are architecture-critical.

Test signals: Inject RTAS hotplug/EPOW/internal-error events, fatal versus recoverable hardware errors, FWNMI system reset and MCE paths, user/kernel synchronous UE handling, SLB/ERAT recovery, malformed/corrupt save areas, and panic/poweroff behavior.

Source read size: 882 lines, 24802 bytes.
