<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rheap.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rheap.h

Purpose: Declares the relocatable heap allocator interface used by old PowerPC embedded drivers to manage scarce on-chip or bus-visible memory ranges.

Important APIs/types/functions: range block/list structures `rh_block_t`, allocator state `rh_info_t`, statistics `rh_stats_t`, allocation/alignment/free/grow helpers, and flags for static allocator metadata. Source-visible declarations include: #define __ASM_PPC_RHEAP_H__; typedef struct _rh_block {; struct list_head list;; typedef struct _rh_info {; struct list_head empty_list;; struct list_head free_list;; struct list_head taken_list;; #define RHIF_STATIC_INFO 0x1.

Control flow: callers initialize an `rh_info_t`, attach one or more free regions, allocate aligned ranges for hardware users, and return ranges to the free list; the header itself only declares the list-based state machine. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: free, empty, and taken lists persist inside the allocator object supplied by the caller. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/list.h>. Integrated with embedded communication and platform drivers that need physical-range allocation.

Risks: list corruption, overlapping region insertion, and static metadata lifetime mistakes can leak scarce hardware memory. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 92 lines, 2578 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rheap.h -->
