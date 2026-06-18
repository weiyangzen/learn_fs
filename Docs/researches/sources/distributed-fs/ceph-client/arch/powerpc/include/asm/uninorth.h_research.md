<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uninorth.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uninorth.h

Purpose: Defines Apple UniNorth/U3/U4 bridge, AGP/GART, clock, power, and HyperTransport register constants.

Important APIs/types/functions: config-space offsets, GART control bits, AGP status/control fields, clock stop/reset bits, address select masks, and HT bridge registers. Source-visible declarations include: #define __ASM_UNINORTH_H__; #define UNI_N_ADDR_SELECT 0x48; #define UNI_N_ADDR_COARSE_MASK 0xffff0000 /* 256Mb regions at *0000000 */; #define UNI_N_ADDR_FINE_MASK 0x0000ffff /* 16Mb regions at f*000000 */; #define UNI_N_CFG_GART_BASE 0x8c; #define UNI_N_CFG_AGP_BASE 0x90; #define UNI_N_CFG_GART_CTRL 0x94; #define UNI_N_CFG_INTERNAL_STATUS 0x98.

Control flow: PowerMac platform and AGP/IOMMU code programs bridge registers using these masks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: bridge register settings persist in host bridge hardware. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerMac PCI/AGP, UniNorth IOMMU/GART, clock/power management, and platform setup.

Risks: register bits are chipset-specific; wrong values can break PCI/AGP DMA or platform power state. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 230 lines, 8409 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uninorth.h -->
