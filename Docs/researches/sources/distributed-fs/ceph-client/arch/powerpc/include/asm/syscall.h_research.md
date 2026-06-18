<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall.h

Purpose: Implements PowerPC syscall tracing helpers over `pt_regs`.

Important APIs/types/functions: syscall function pointer type, syscall tables, get/set syscall number, rollback, return/error extraction, argument get/set, and audit architecture selection. Source-visible declarations include: #define _ASM_SYSCALL_H 1; typedef long (*syscall_fn)(const struct pt_regs *);; typedef long (*syscall_fn)(unsigned long, unsigned long, unsigned long,; extern const syscall_fn sys_call_table[];; extern const syscall_fn compat_sys_call_table[];; static inline int syscall_get_nr(struct task_struct *task, struct pt_regs *regs); static inline void syscall_set_nr(struct task_struct *task, struct pt_regs *regs, int nr); static inline void syscall_rollback(struct task_struct *task,.

Control flow: ptrace/seccomp/audit code inspects or rewrites pt_regs before/after syscall dispatch. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is task pt_regs and syscall table selection. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <uapi/linux/audit.h>, #include <linux/sched.h>, #include <linux/thread_info.h>. Integrated with syscall entry, audit, seccomp, ptrace, tracing, and compat syscall handling.

Risks: argument register order and error conventions differ across ABIs; mistakes break tracers and filters. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 142 lines, 3607 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/syscall.h -->
