<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tce.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tce.h

Purpose: Defines Translation Control Entry constants for PowerPC IOMMU tables.

Important APIs/types/functions: TCE types, entry size, valid/all-LPAR/read/write bits for PCI and virtual bus. Source-visible declarations include: #define _ASM_POWERPC_TCE_H; #define TCE_VB 0; #define TCE_PCI 1; #define TCE_ENTRY_SIZE 8 /* each TCE is 64 bits */; #define TCE_VALID 0x800 /* TCE valid */; #define TCE_ALLIO 0x400 /* TCE valid for all lpars */; #define TCE_PCI_WRITE 0x2 /* write from PCI allowed */; #define TCE_PCI_READ 0x1 /* read from PCI allowed */.

Control flow: IOMMU code composes TCE words to map DMA addresses for devices or virtual buses. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: TCE tables persist as hardware DMA translation state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/iommu.h>. Integrated with pSeries IOMMU, PCI DMA mapping, virtual bus DMA, and hypervisor TCE calls.

Risks: wrong permission bits can expose memory to devices or break DMA. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 30 lines, 892 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/tce.h -->
