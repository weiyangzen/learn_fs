<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/irqflags.h

## Purpose
Implements local interrupt save/restore/enable/disable helpers using status CSR bits.

## Important APIs, Types, And Functions
functions/prototypes `arch_local_save_flags`, `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_irq_save`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_restore`; macros/constants `_ASM_RISCV_IRQFLAGS_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/csr.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 54 lines, 1148 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irqflags.h -->
