<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list.h

## Purpose
Defines alternative-instruction macros for RISC-V architectural and vendor errata, including fence, page-fault, CMO, and PMA/PBMT substitutions.

## Important APIs, Types, And Functions
macros/constants `ASM_ERRATA_LIST_H`, `ALT_INSN_FAULT(x)`, `ALT_PAGE_FAULT(x)`, `ALT_SFENCE_VMA_ASID(asid)`, `ALT_SFENCE_VMA_ADDR(addr)`, `ALT_SFENCE_VMA_ADDR_ASID(addr, asid)`, `ALT_RISCV_PAUSE()`, `ALT_SVPBMT_SHIFT`, `ALT_THEAD_MAE_SHIFT`, `ALT_SVPBMT(_val, prot)`, `ALT_THEAD_PMA(_val)`, `ALT_CMO_OP(_op, _start, _size, _cachesize)`, `THEAD_C9XX_RV_IRQ_PMU`, `THEAD_C9XX_CSR_SCOUNTEROF`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/csr.h`, `asm/insn-def.h`, `asm/hwcap.h`, `asm/vendorid_list.h`, `asm/errata_list_vendors.h`, `asm/vendor_extensions/mips.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 122 lines, 3806 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list.h -->
