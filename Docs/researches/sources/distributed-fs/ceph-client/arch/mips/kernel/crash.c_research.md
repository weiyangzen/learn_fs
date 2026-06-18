<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/crash.c

### Purpose
`crash.c` coordinates MIPS crash shutdown for kexec, saving CPU register state and stopping secondary CPUs before rebooting into a crash kernel.

### Important APIs, Types, And Functions
Key state is `crashing_cpu` and `cpus_in_crash`. Important functions are `crash_shutdown_secondary()`, `crash_kexec_prepare_cpus()`, `crash_smp_send_stop()`, and `default_machine_crash_shutdown()`.

### Control Flow
The crashing CPU disables interrupts, saves its registers, sends IPIs to online secondary CPUs, waits up to about 10 seconds for them to enter crash state, marks CPUs stopped, and proceeds to kexec. Secondary CPUs find usable registers, mark themselves offline, disable interrupts, save CPU state once, wait for `kexec_ready_to_reboot`, then call `kexec_reboot()`.

### State, Persistence, And Dependencies
State includes crash CPU id, crash CPU mask, online CPU state, saved crash notes, and kexec readiness. Dependencies include SMP calls, kexec, crash dump, IRQ state, and task stack helpers.

### Integration Points
Generic panic/kexec paths call `default_machine_crash_shutdown()` and override `crash_smp_send_stop()`. Platform-specific `_crash_smp_send_stop` may run before the generic MIPS preparation.

### Risks
Crash paths run under panic conditions with limited synchronization. If secondary CPUs do not respond before timeout, crash dump completeness is reduced. Register fallback may be approximate.

### Test Signals
Kdump tests on SMP MIPS, forced panic with busy secondary CPUs, crash note validation, timeout behavior, and platform `_crash_smp_send_stop` interaction are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/crash.c -->
