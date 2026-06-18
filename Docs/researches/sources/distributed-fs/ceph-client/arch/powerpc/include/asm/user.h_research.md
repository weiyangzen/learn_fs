<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/user.h

Purpose: Defines the legacy PowerPC `struct user` core-dump/ptrace layout.

Important APIs/types/functions: `struct user` with pt_regs, u-area sizing, start addresses, signal, and register offset fields. Source-visible declarations include: #define _ASM_POWERPC_USER_H; struct user {; struct user_pt_regs regs; /* entire machine state */.

Control flow: old ptrace and core dump tooling can interpret saved task register and memory metadata through this layout. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: serialized process state persists in core files or ptrace-visible structures. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <asm/ptrace.h>, #include <asm/page.h>. Integrated with ptrace, core dumps, debuggers, and legacy user ABI.

Risks: field layout is external ABI and tied to `asm/ptrace.h` register structures. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 47 lines, 1997 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/user.h -->
