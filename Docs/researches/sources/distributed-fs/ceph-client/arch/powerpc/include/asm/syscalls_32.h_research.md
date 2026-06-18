<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls_32.h

Purpose: Defines 32-bit PowerPC signal/ucontext compatibility structures used by syscall prototypes.

Important APIs/types/functions: `pt_regs32`, `sigcontext32`, `mcontext32`, and `ucontext32`. Source-visible declarations include: #define _ASM_POWERPC_SYSCALLS_32_H; struct pt_regs32 {; struct sigcontext32 {; struct mcontext32 {; struct ucontext32 {; struct mcontext32 uc_mcontext;.

Control flow: compat syscall and signal code copy these layouts to and from 32-bit user memory. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: user signal/ucontext frames persist across signal delivery and sigreturn. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/compat.h>, #include <asm/siginfo.h>, #include <asm/signal.h>. Integrated with 32-bit PowerPC ABI, compat signal handling, and ptrace/syscall code.

Risks: field order and sizes are user ABI and must match libc/kernel signal expectations. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 60 lines, 1618 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscalls_32.h -->
