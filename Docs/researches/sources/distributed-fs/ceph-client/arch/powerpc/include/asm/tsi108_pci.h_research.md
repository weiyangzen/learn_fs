<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_pci.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_pci.h

Purpose: Defines TSI108 PCI inbound/outbound translation register offsets.

Important APIs/types/functions: P2O BAR/page-size registers and PFAB IO/MEM/PFM register offsets. Source-visible declarations include: #define _ASM_POWERPC_TSI108_PCI_H; #define TSI108_PCI_P2O_BAR0 (TSI108_PCI_OFFSET + 0x10); #define TSI108_PCI_P2O_BAR0_UPPER (TSI108_PCI_OFFSET + 0x14); #define TSI108_PCI_P2O_BAR2 (TSI108_PCI_OFFSET + 0x18); #define TSI108_PCI_P2O_BAR2_UPPER (TSI108_PCI_OFFSET + 0x1c); #define TSI108_PCI_P2O_PAGE_SIZES (TSI108_PCI_OFFSET + 0x4c); #define TSI108_PCI_PFAB_BAR0 (TSI108_PCI_OFFSET + 0x204); #define TSI108_PCI_PFAB_BAR0_UPPER (TSI108_PCI_OFFSET + 0x208).

Control flow: PCI host bridge setup programs address windows for CPU-to-PCI and PCI-to-memory access. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: PCI translation windows persist in bridge registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/tsi108.h>. Integrated with TSI108 PCI host bridge setup, DMA, and resource assignment.

Risks: incorrect window programming can expose memory or make PCI config/DMA unreachable. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 1191 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tsi108_pci.h -->
