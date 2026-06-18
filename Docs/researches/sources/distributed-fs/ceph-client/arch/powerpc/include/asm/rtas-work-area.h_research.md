<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-work-area.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-work-area.h

Purpose: Declares the allocator for RTAS firmware work areas that must be physically addressable and below RTAS placement limits.

Important APIs/types/functions: `struct rtas_work_area`, compile-time bounded `rtas_work_area_alloc()`, raw/size/physical accessors, free helpers, and arena reservation. Source-visible declarations include: #define _ASM_POWERPC_RTAS_WORK_AREA_H; struct rtas_work_area {; enum {; #define rtas_work_area_alloc(size_) ({ \; struct rtas_work_area *__rtas_work_area_alloc(size_t size);; static inline char *rtas_work_area_raw_buf(const struct rtas_work_area *area); static inline size_t rtas_work_area_size(const struct rtas_work_area *area); static inline phys_addr_t rtas_work_area_phys(const struct rtas_work_area *area).

Control flow: callers reserve the arena during boot, allocate a bounded work buffer, pass its physical address to firmware, then free the buffer. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: the arena is global reserved memory; each returned area tracks virtual buffer, size, and physical address. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/build_bug.h>, #include <linux/sizes.h>, #include <linux/types.h>, #include <asm/page.h>. Integrated with RTAS syscalls and firmware functions that require temporary data buffers.

Risks: sizes above the fixed limit are compile-time bugs and physical-address constraints must be preserved for firmware. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 96 lines, 2817 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas-work-area.h -->
