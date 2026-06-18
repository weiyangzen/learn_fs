<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/types.h

Purpose: Extends PowerPC UAPI types with kernel vector type support.

Important APIs/types/functions: `uapi/asm/types.h` include and optional `vector128` typedef under Altivec-enabled compiler builds. Source-visible declarations include: #define _ASM_POWERPC_TYPES_H; typedef __vector128 vector128;.

Control flow: kernel code needing a 128-bit vector scalar includes this arch type wrapper. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no persistent state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/asm/types.h>. Integrated with Altivec/VSX code, ptrace/vector save areas, and generic type includes.

Risks: compiler feature guards must match available vector extensions. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 20 lines, 575 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/types.h -->
