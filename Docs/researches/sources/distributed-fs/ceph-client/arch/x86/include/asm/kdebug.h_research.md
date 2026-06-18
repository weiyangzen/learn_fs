<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kdebug.h

## Purpose
x86 die/oops/debug notification declarations and enums for exception diagnostics. The header is 45 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/notifier.h>`

Notable constants/macros: `#define _ASM_X86_KDEBUG_H`

Notable declarations and inline helpers: `#define _ASM_X86_KDEBUG_H`; `struct pt_regs;`; `enum die_val {`; `enum show_regs_mode {`; `extern void die(const char *, struct pt_regs *,long);`; `void die_addr(const char *str, struct pt_regs *regs, long err, long gp_addr);`; `extern int __must_check __die(const char *, struct pt_regs *, long);`; `extern void show_stack_regs(struct pt_regs *regs);`; `extern void __show_regs(struct pt_regs *regs, enum show_regs_mode,`; `extern void show_iret_regs(struct pt_regs *regs, const char *log_lvl);`; `extern unsigned long oops_begin(void);`; `extern void oops_end(unsigned long, struct pt_regs *, int signr);`

## Control Flow
Exception paths call die()/__die()/die_addr(), notify die chains with enum die_val reasons, print registers/stacks, and bracket oops reporting with oops_begin/end.

## State and Persistence
State includes notifier chains, oops-in-progress state, console/lock handling, and pt_regs snapshots managed elsewhere.

## Dependencies and Integration Points
Depends on linux/notifier, pt_regs, trap handlers, printk/oops infrastructure, and debug exception users.

## Risks
Risks include notifier recursion, deadlocks during oops, leaking bad register data, and wrong die reason classification.

## Test Signals
Tests should cover WARN/oops paths, die notifiers, NMI/MCE/debug exceptions, panic-on-oops, and show_regs modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kdebug.h -->
