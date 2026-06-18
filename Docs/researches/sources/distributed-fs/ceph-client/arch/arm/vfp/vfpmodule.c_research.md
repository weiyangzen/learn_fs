## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpmodule.c

### Purpose
Owns ARM VFP runtime support: detection, lazy context switching, undefined-instruction exception handling, software bounce/emulation, signal-frame save/restore, CPU hotplug/PM, and kernel NEON entry.

### Important APIs, Types, And Functions
Important functions include `vfp_state_hold/release`, `vfp_force_reload`, `vfp_thread_flush/exit/copy`, `vfp_notifier`, `vfp_raise_exceptions`, `vfp_emulate_instruction`, `VFP_bounce`, `vfp_enable`, `vfp_disable`, `vfp_sync_hwstate`, `vfp_flush_hwstate`, `vfp_preserve_user_clear_hwstate`, `vfp_restore_user_hwstate`, `vfp_support_entry`, `kernel_neon_begin/end`, `vfp_detect`, and `vfp_init`.

### Control Flow
At boot `vfp_init()` enables access, probes FPSID, discovers VFP/NEON features, registers undefined-instruction hooks, thread notifiers, CPU hotplug callbacks, and PM callbacks. At runtime an undefined VFP/NEON instruction enters `vfp_support_entry()`, lazily loads the current task state if needed, retries if no exception is pending, or calls `VFP_bounce()` to emulate the faulting FP instruction(s) and raise SIGFPE when FPSCR enables trapped exceptions.

### State, Persistence, And Dependencies
Global state includes `have_vfp`, `VFP_arch`, `vfp_current_hw_state[NR_CPUS]`, ELF hwcaps, and undefined hooks. Per-thread persistent state is `thread_info.vfpstate`. Dependencies include ARM coprocessor access control, thread notifier API, CPU PM/hotplug, perf software events, signal delivery, and `vfphw.S` save/load routines.

### Integration Points
Integrates with scheduler context switches, signal handling, kernel NEON users, CPU feature exposure to userspace, and undefined-instruction traps.

### Risks
Lazy context switching is highly concurrency-sensitive, especially SMP migration and PREEMPT_RT behavior. Kernel-mode FP misuse is fatal. Incorrect FPSCR/FPEXC bounce handling can either lose exceptions or loop on the same instruction.

### Test Signals
Run FP context-switch stress across CPUs, signal save/restore tests, CPU hotplug and suspend/resume tests, NEON kernel selftests, SIGFPE trap tests, and userspace hwcap validation.
