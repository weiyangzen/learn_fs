<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/machine_kexec.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/machine_kexec.c

### Purpose
`machine_kexec.c` implements MIPS machine-specific kexec and crash-kexec handoff. It prepares new-kernel arguments, shuts down other CPUs, copies relocation code to the control page, rewrites indirection entries to virtual addresses, flushes caches, and jumps to the new kernel.

### Important APIs, Types, And Functions
Public entry points include `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, `kexec_reboot()`, and `machine_kexec()`. Platform hooks are `_machine_kexec_prepare`, `_machine_kexec_shutdown`, `_machine_crash_shutdown`, and `_crash_smp_send_stop`. SMP helpers include `kexec_shutdown_secondary()` and `kexec_nonboot_cpu_jump()`.

### Control Flow
Preparation checks SMP nonboot CPU support and invokes an optional platform prepare hook. UHI boot prepare scans image segments for an FDT and sets `kexec_args`. Shutdown invokes platform shutdown, sends secondaries into a wait loop, and waits until only one CPU remains online. `machine_kexec()` installs relocation code into `image->control_code_page`, sets `kexec_start_address` and `kexec_indirection_page`, converts page-list physical addresses to virtual, marks the boot CPU offline, disables IRQs, flushes caches, releases secondary CPUs, and calls `kexec_reboot()`.

### State, Persistence, And Dependencies
State includes `reboot_code_buffer`, relocation globals, atomic `kexec_ready_to_reboot`, relocated SMP wait function pointer, CPU online masks, `kexec_args`, and the kimage page list. Dependencies include kexec core, cache flushing, FDT helpers, SMP support, and platform-specific hooks.

### Integration Points
This code integrates Linux kexec/kdump, MIPS relocation assembly, platform shutdown code, firmware boot argument conventions, and CPU hotplug visibility for crash analysis tools.

### Risks
Cache coherency and address translation are critical. If indirection entries are not converted correctly or relocation code is not visible in icache, the handoff fails after interrupts are disabled. SMP shutdown depends on all secondaries reaching the wait loop.

### Test Signals
Run normal kexec, crash kexec/kdump, UHI FDT handoff, SMP kexec with secondary CPUs, and failure injection for missing nonboot CPU support. Verify crash dumps see expected online CPU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/machine_kexec.c -->
