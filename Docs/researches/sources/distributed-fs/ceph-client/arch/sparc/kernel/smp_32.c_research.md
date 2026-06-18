# sources/distributed-fs/ceph-client/arch/sparc/kernel/smp_32.c

Purpose: provides the generic 32-bit SPARC SMP orchestration layer, delegating platform-specific boot and IPI mechanics to sun4m, sun4d, and LEON backends.

Important APIs/types/functions: shared globals include `cpu_callin_map`, `smp_commenced_mask`, `sparc32_ipi_ops`, and `smp_penguin_ctable`. Entry points include `smp_prepare_cpus()`, `smp_setup_cpu_possible_map()`, `smp_prepare_boot_cpu()`, `__cpu_up()`, `smp_callin()`, `arch_smp_send_reschedule()`, `arch_send_call_function_*_ipi()`, `smp_resched_interrupt()`, `smp_call_function*_interrupt()`, `smp_store_cpu_info()`, and `/proc` helpers `smp_bogo()`/`smp_info()`.

Control flow: boot enumerates PROM CPU instances into possible/present masks, stores boot CPU PROM/MID/frequency data, then calls the platform boot routine. `__cpu_up()` invokes the selected platform `boot_one_cpu()` and waits for `cpu_online()`, while secondary CPUs enter `smp_callin()` and run `sparc_start_secondary()`: cache/TLB flush, platform pre-start, CPU hotplug notify, timer registration, delay calibration, CPU info setup, platform pre-online, set online, enable IRQs, and enter idle.

State and persistence: runtime state is CPU masks, per-CPU `cpu_data`, `current_thread_info()->cpu`, and call-in flags; no persistence.

Dependencies and integration points: integrates with PROM CPU start, SRMMU context-table handoff, clockevents via `register_percpu_ce()`, scheduler IPIs, generic SMP call-function handling, and platform files.

Risks: boot waits rely on cache-coherent visibility of `cpu_callin_map` and `smp_commenced_mask`. Unsupported CPU models deliberately `BUG()`. Wrong PROM MID or platform operation selection breaks IPI routing.

Test signals: boot with multiple sun4m/sun4d/LEON CPUs, CPU possible/present masks, `smp_call_function*`, reschedule IPIs, per-CPU timers, `/proc/cpuinfo` BogoMIPS, and stuck-secondary timeout paths.
