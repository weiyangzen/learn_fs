<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls.h

Purpose: Declares PowerPC-specific syscall entry points and builds syscall table declarations.

Important APIs/types/functions: compat/native syscall prototypes, `merge_64()`, PowerPC special syscalls, conditional table declarations, and syscall table includes. Source-visible declarations include: #define __ASM_POWERPC_SYSCALLS_H; struct rtas_args;; #define merge_64(low, high) (((u64)high << 32) | low); #define merge_64(high, low) (((u64)high << 32) | low); struct ucontext __user *new_ctx, long ctx_size);; struct sig_dbg_op __user *dbg);; struct ucontext32 __user *new_ctx,; struct compat_rlimit __user *rlim);.

Control flow: generated syscall-table macros expand to external declarations or table entries depending on config. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: syscall tables are immutable dispatch state after build/link. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compiler.h>, #include <linux/linkage.h>, #include <linux/types.h>, #include <linux/compat.h>, #include <asm/syscall.h>, #include <asm/syscalls_32.h>, #include <asm/unistd.h>, #include <asm/ucontext.h>. Integrated with syscall dispatch, compat layer, signal/ucontext, RTAS, ppc64/personality, and generated syscall tables.

Risks: prototype and argument-order mismatches are ABI-breaking, especially 32-bit split 64-bit arguments. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 161 lines, 5171 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls.h -->
