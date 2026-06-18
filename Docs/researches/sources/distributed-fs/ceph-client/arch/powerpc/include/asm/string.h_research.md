<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/string.h

Purpose: Declares PowerPC optimized string and memory primitives.

Important APIs/types/functions: `__HAVE_ARCH_*` feature macros and prototypes for strcpy/strncpy/strcmp/memset/memcpy/memmove/memchr/memcmp plus flushcache copy. Source-visible declarations include: #define _ASM_POWERPC_STRING_H; #define __HAVE_ARCH_STRNCPY; #define __HAVE_ARCH_STRNCMP; #define __HAVE_ARCH_MEMCHR; #define __HAVE_ARCH_MEMCMP; #define __HAVE_ARCH_MEMSET16; #define __HAVE_ARCH_MEMSET; #define __HAVE_ARCH_MEMCPY.

Control flow: generic lib/string uses these arch hooks when available. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no persistent state; operations mutate caller buffers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with kernel lib/string, memcpy flushcache users, and assembly string implementations.

Risks: prototype drift or wrong arch-hook macros can select incompatible optimized routines. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 92 lines, 2870 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/string.h -->
