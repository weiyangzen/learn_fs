<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/process.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/process.c

### Purpose
`process.c` implements PA-RISC process lifecycle hooks: restart, poweroff, halt, idle, CPU-dead handling, thread cloning, and blocked-task wait-channel discovery.

### Important APIs, Types, And Functions
`machine_restart()`, `machine_power_off()`, `machine_halt()`, `flush_thread()`, `arch_cpu_idle_dead()`, `arch_cpu_idle()`, `copy_thread()`, and `__get_wchan()` are the main exported architecture hooks. It exports `pm_power_off` and `running_on_qemu`.

### Control Flow
Restart asks firmware/chassis interfaces to reset, disables interrupts, and falls back to the global broadcast reset register. Poweroff returns the soft power button to firmware control, calls generic poweroff handlers, then waits for a firmware console return key to reboot. `copy_thread()` builds either a kernel-thread frame targeting `ret_from_kernel_thread` or a user-thread frame targeting `child_return`, optionally installing TLS in `cr27`. Wait-channel lookup unwinds a blocked task until it escapes scheduler functions.

### State, Persistence, And Dependencies
State is limited to boot-time QEMU detection, exported poweroff hook state, and per-task saved `pt_regs`. It depends on PDC firmware calls, chassis LEDs, cache/TLB flushes, CPU hotplug, scheduler task stacks, and the PA-RISC unwind implementation.

### Integration Points
Called by generic reboot, task cloning, CPU idle/hotplug, and `/proc` stack-wait users.

### Risks
Restart/poweroff paths are firmware-specific and may never return. `copy_thread()` handles 64-bit function descriptors manually; descriptor layout mismatches would break kernel thread startup. Dead CPU handling assumes firmware rendezvous works after local cache/TLB flush.

### Test Signals
Boot, reboot, poweroff fallback, CPU hotplug offline, kernel thread creation, `clone(CLONE_SETTLS)`, and blocked-task `wchan` reporting are the useful runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/process.c -->
