<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uaccess.h

Purpose: Implements PowerPC user-memory access, copy, clear, and nofault primitives.

Important APIs/types/functions: `get_user/put_user`, unchecked forms, exception-table assembly, KUAP allow/prevent windows, raw copy helpers, `copy_{to,from}_user`, string helpers, and VMX copy threshold. Source-visible declarations include: #define _ARCH_POWERPC_UACCESS_H; #define TASK_SIZE_MAX TASK_SIZE_USER64; #define VMX_COPY_THRESHOLD 3328; #define __put_user(x, ptr) \; #define put_user(x, ptr) \; #define __put_user_asm_goto(x, addr, label, op) \; #define __put_user_asm_goto(x, addr, label, op) \; #define __put_user_asm2_goto(x, ptr, label) \.

Control flow: callers validate or rely on prevalidated user ranges, temporarily allow user access, perform asm loads/stores/copies, and fix up faults through exception tables. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is task address space, KUAP access state, and destination buffers; no persistent header-owned state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/sizes.h>, #include <asm/processor.h>, #include <asm/page.h>, #include <asm/extable.h>, #include <asm/kup.h>, #include <asm/asm-compat.h>, #include <asm-generic/access_ok.h>. Integrated with syscalls, filesystems, networking, signal handling, BPF, ptrace, and generic usercopy hardening.

Risks: exception fixups, access_ok/KUAP ordering, 32/64-bit constraints, and partial-copy semantics are security-critical. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 599 lines, 17598 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/uaccess.h -->
