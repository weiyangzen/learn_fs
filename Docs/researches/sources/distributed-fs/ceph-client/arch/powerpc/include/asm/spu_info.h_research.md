<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_info.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_info.h

Purpose: Includes kernel SPU definitions and the UAPI SPU info structures in one internal header.

Important APIs/types/functions: `asm/spu.h` plus `uapi/asm/spu_info.h`. Source-visible declarations include: #define _SPU_INFO_H.

Control flow: spufs and coredump paths include it when both kernel state and user-visible info records are needed. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state beyond included structures. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/spu.h>, #include <uapi/asm/spu_info.h>. Integrated with Cell spufs, proc/debug info, and UAPI reporting.

Risks: wrapper must not create conflicting definitions between kernel-only and UAPI SPU structures. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 15 lines, 272 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/spu_info.h -->
