# sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/smp.h` Defines arm64 SMP boot status values, logical CPU mapping, IPI types, secondary entry declarations, CPU hotplug/death helpers, and crash-stop hooks. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
CPU_* status constants, raw_smp_processor_id(), __cpu_logical_map, cpu_logical_map(), set_cpu_logical_map(), smp_init_cpus(), enum ipi_msg_type, set_smp_ipi_range*(), secondary_start_kernel(), struct secondary_data, secondary_data, __early_cpu_boot_status, secondary_entry(), arch_send_call_function_*(), arch_send_wakeup_ipi(), __cpu_disable(), cpu_die(), cpu_park_loop(), update_cpu_boot_status(), cpu_panic_kernel(), cpus_are_stuck_in_kernel(), crash_smp_send_stop(). The file is 160 lines / 3924 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Boot CPU populates secondary_data and releases secondary_entry; secondaries update status with WRITE_ONCE plus DSB, then either come online, request kill, panic, or park in WFE/WFI loops. IPI helpers route scheduler/call-function/timer/irq-work/crash messages.

### State, Persistence, And Dependencies
Persistent state includes per-task thread_info->cpu, __cpu_logical_map, secondary_data, boot status, and stuck CPU tracking. Depends on threads, cpumask, thread_info, const; integrates with CPU bring-up, hotplug, GIC IPIs, ACPI parking protocol, crash/kexec, scheduler, and topology.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Boot status values are consumed by assembly/firmware paths; missing DSB can hide failures; stuck CPUs inhibit kexec/hibernate and must not run freed memory.

### Test Signals
Run SMP boot/hotplug stress, crash stop tests, ACPI parking protocol builds, feature-mismatch secondary failure tests, and IPI tracing.
