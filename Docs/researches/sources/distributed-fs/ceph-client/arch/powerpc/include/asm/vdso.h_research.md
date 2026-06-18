<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso.h

Purpose: Defines PowerPC vDSO layout constants, symbol-offset helpers, and assembly symbol macros.

Important APIs/types/functions: `VDSO_VERSION_STRING`, page count, `VDSO64_SYMBOL`, `VDSO32_SYMBOL`, and local/global vDSO function symbol macros. Source-visible declarations include: #define _ASM_POWERPC_VDSO_H; #define VDSO_VERSION_STRING LINUX_2.6.15; #define __VDSO_PAGES 4; #define VDSO64_SYMBOL(base, name) ((unsigned long)(base) + (vdso64_offset_##name)); #define VDSO32_SYMBOL(base, name) ((unsigned long)(base) + (vdso32_offset_##name)); #define V_FUNCTION_BEGIN(name) \; #define V_FUNCTION_END(name) \; #define V_LOCAL_FUNC(name) (name).

Control flow: kernel maps vDSO pages and resolves exported helper addresses from generated offsets. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: vDSO image pages and symbol offsets persist as user-mapped ABI. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <generated/vdso64-offsets.h>, #include <generated/vdso32-offsets.h>. Integrated with time/getcpu/getrandom vDSO, signal trampolines, generated offsets, and userspace libc.

Risks: page count and symbol names are ABI-sensitive and must match generated vDSO offset headers. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 54 lines, 1049 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso.h -->
