<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq.h

## Purpose
Declares RISC-V interrupt-controller discovery, ACPI GSI mapping, hart-index lookup, and backtrace IPI hooks.

## Important APIs, Types, And Functions
types `fwnode_handle`, `riscv_irqchip_type`, `resource`; functions/prototypes `arch_trigger_cpumask_backtrace`, `riscv_set_intc_hwnode_fn`, `riscv_get_intc_hwnode`, `riscv_get_hart_index`, `riscv_acpi_get_gsi_info`, `riscv_acpi_get_gsi_domain_id`, `acpi_rintc_index_to_hartid`, `acpi_rintc_ext_parent_to_hartid`, `acpi_rintc_get_plic_nr_contexts`, `acpi_rintc_get_plic_context`, `riscv_acpi_update_gsi_range`; macros/constants `_ASM_RISCV_IRQ_H`, `INVALID_CONTEXT`, `arch_trigger_cpumask_backtrace`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/interrupt.h`, `linux/linkage.h`, `asm-generic/irq.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 87 lines, 2428 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq.h -->
