<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list_vendors.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list_vendors.h

## Purpose
Assigns vendor errata IDs used by the alternatives and errata patching infrastructure.

## Important APIs, Types, And Functions
macros/constants `ASM_ERRATA_LIST_VENDORS_H`, `ERRATA_ANDES_NO_IOCP`, `ERRATA_ANDES_NUMBER`, `ERRATA_SIFIVE_CIP_453`, `ERRATA_SIFIVE_CIP_1200`, `ERRATA_SIFIVE_NUMBER`, `ERRATA_THEAD_MAE`, `ERRATA_THEAD_PMU`, `ERRATA_THEAD_GHOSTWRITE`, `ERRATA_THEAD_NUMBER`, `ERRATA_MIPS_P8700_PAUSE_OPCODE`, `ERRATA_MIPS_NUMBER`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 29 lines, 638 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list_vendors.h -->
