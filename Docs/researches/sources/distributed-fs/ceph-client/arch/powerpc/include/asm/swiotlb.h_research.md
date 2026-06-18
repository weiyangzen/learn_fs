<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swiotlb.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swiotlb.h

Purpose: Declares PowerPC SWIOTLB enable flags and 4G detection hook.

Important APIs/types/functions: `ppc_swiotlb_enable`, `ppc_swiotlb_flags`, and optional `swiotlb_detect_4g()`. Source-visible declarations include: #define __ASM_SWIOTLB_H; extern unsigned int ppc_swiotlb_enable;; extern unsigned int ppc_swiotlb_flags;; static inline void swiotlb_detect_4g(void) {}.

Control flow: DMA setup decides whether to force bounce buffering and sets SWIOTLB flags before devices probe. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global SWIOTLB enable/flag state persists after boot. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/swiotlb.h>. Integrated with DMA mapping, memory encryption/secure guest paths, and generic SWIOTLB.

Risks: incorrect detection causes devices to DMA above their addressing limits or needlessly bounce all DMA. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 20 lines, 413 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/swiotlb.h -->
