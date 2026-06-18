## sources/distributed-fs/ceph-client/arch/arm64/kernel/debug-monitors.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/kernel/debug-monitors.c` implements ARM64 self-hosted
debug monitor control, single-step state management, and breakpoint exception dispatch. It bridges
architectural debug exceptions to ptrace, uprobes, kprobes, kgdb, BUG/KASAN/UBSAN/CFI handlers, and
user SIGTRAP delivery.

### Important APIs, Types, And Functions
`debug_monitors_arch()` reports the sanitized debug architecture level. `enable_debug_monitors()` and
`disable_debug_monitors()` maintain per-CPU `mde_ref_count` and `kde_ref_count` and update
`MDSCR_EL1`. `debug_enabled` can be disabled by the `nodebugmon` early parameter or debugfs
`debug_enabled`. CPU hotplug clears OS lock via `clear_os_lock()` and `debug_monitors_init()`.
Exception handlers include `do_el0_softstep()`, `do_el1_softstep()`, `do_el0_brk64()`,
`do_el1_brk64()`, `do_bkpt32()`, and `try_handle_aarch32_break()`. Single-step APIs include
`user_enable_single_step()`, `user_disable_single_step()`, `user_rewind_single_step()`,
`user_fastforward_single_step()`, `kernel_enable_single_step()`, `kernel_disable_single_step()`, and
`kernel_active_single_step()`.

### Control Flow
Debug monitor users enable MDE and optionally KDE through refcounted per-CPU calls, with preemption
expected disabled. MDSCR writes mask DAIF locally to avoid exception races. On boot/hotplug,
`clear_os_lock()` unlocks debug registers. EL0 single-step first offers the event to uprobes, then
sends `SIGTRAP/TRAP_TRACE` and rewinds state if the client wants continued stepping. EL1 single-step
offers the event to kgdb and otherwise warns and re-enables stepping in the saved SPSR.

EL1 BRK dispatch inspects the BRK immediate and routes to BUG, CFI, reserved-fault, KASAN software
tag, UBSAN trap, KGDB, kprobes, or kretprobes handlers. Unhandled EL1 BRK calls `die()`. EL0 BRK
routes uprobes BRK immediates to uprobes and sends `SIGTRAP/TRAP_BRKPT` otherwise. AArch32 break
handling fetches ARM or Thumb instructions from user memory and recognizes ARM, Thumb, or Thumb-2
break encodings.

### State, Persistence, And Dependencies
Persistent state is per-CPU MDSCR enable refcounts, the debugfs `debug_enabled` boolean, task
`TIF_SINGLESTEP`, and saved SPSR.SS bits in `pt_regs`. Dependencies include sysreg access, ptrace,
uprobes, kprobes, kgdb, KASAN, UBSAN, CFI, exception entry, user accessors, CPU hotplug, debugfs, and
signal delivery.

### Integration Points
`entry-common.c` calls these handlers for debug exception classes. Ptrace and syscall restart paths
use the user stepping APIs; kprobes/kgdb rely on kernel stepping and BRK dispatch. The file is also
part of external-debugger coexistence because debugfs and `nodebugmon` can suppress self-hosted
debug monitor enablement.

### Risks
Incorrect MDSCR refcounting can leave debug exceptions disabled or unexpectedly enabled. Calling
enable/disable paths while preemptible can update the wrong CPU's state. Bad BRK immediate routing
can turn diagnostics into fatal oopses or hide real traps. User instruction fetches for AArch32
break detection must tolerate faults. These paths are marked `NOKPROBE` where recursion would be
dangerous.

### Test Signals
Ptrace single-step tests, uprobes/kprobes tests, kgdb break/step tests, KASAN/UBSAN/BUG trap tests,
AArch32 compat breakpoint tests, CPU hotplug with debug register access, `nodebugmon`, debugfs
toggling, and lockdep/preemption warnings around MDSCR users are useful signals.
