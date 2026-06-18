<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops_sbi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops_sbi.h

## Purpose
Declares the SBI-backed CPU operations and hart boot-data handoff structure.

## Important APIs, Types, And Functions
types `cpu_operations`, `sbi_hart_boot_data`; functions/prototypes `cpu_ops_sbi`; macros/constants `__ASM_CPU_OPS_SBI_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/init.h`, `linux/sched.h`, `linux/threads.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 27 lines, 610 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops_sbi.h -->
