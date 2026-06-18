<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall_wrapper.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall_wrapper.h

Purpose: Defines PowerPC syscall wrapper macros that unpack `pt_regs` into typed syscall arguments.

Important APIs/types/functions: `SC_POWERPC_REGS_TO_ARGS`, `__SYSCALL_DEFINEx`, `SYSCALL_DEFINE0`, and `COND_SYSCALL()`. Source-visible declarations include: #define __ASM_POWERPC_SYSCALL_WRAPPER_H; struct pt_regs;; #define SC_POWERPC_REGS_TO_ARGS(x, ...) \; #define __SYSCALL_DEFINEx(x, name, ...) \; static inline long __do_sys##name(__MAP(x,__SC_DECL,__VA_ARGS__)); \; static inline long __do_sys##name(__MAP(x,__SC_DECL,__VA_ARGS__)); #define SYSCALL_DEFINE0(sname) \; #define COND_SYSCALL(name) \.

Control flow: macro expansion emits wrapper, alias, metadata, and inline typed implementation for syscall table entries. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no runtime state beyond generated functions. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with generic syscall definition machinery and PowerPC pt_regs ABI.

Risks: macro signature changes can break syscall metadata, tracing, or compat builds. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 49 lines, 1670 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall_wrapper.h -->
