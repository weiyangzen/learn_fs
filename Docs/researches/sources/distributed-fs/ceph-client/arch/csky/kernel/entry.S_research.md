# sources/distributed-fs/ceph-client/arch/csky/kernel/entry.S

## Purpose

implements C-SKY exception, syscall, trap, fork-return, work-pending, TLS, and interrupt return
assembly paths

## Important APIs, Types, and Functions

Source read size: 274 lines, 5019 bytes. Includes: `linux/linkage.h`, `abi/entry.h`, `abi/pgtable-
bits.h`, `asm/errno.h`, `asm/setup.h`, `asm/unistd.h`, `asm/asm-offsets.h`, `linux/threads.h`,
`asm/page.h`, `asm/thread_info.h`. Assembly/global entries: `csky_pagefault`, `csky_systemcall`,
`ret_from_kernel_thread`, `ret_from_fork`, `csky_trap`, `csky_get_tls`, `csky_irq`, `__switch_to`.

## Control Flow and Behavior

entries include csky_pagefault, csky_systemcall, ret_from_kernel_thread, ret_from_fork,
ret_from_exception, csky_trap, csky_get_tls, and interrupt/NMI-style save/restore flows built from
ABI SAVE_ALL/RESTORE_ALL macros

## State and Persistence

runtime state is the saved pt_regs frame on the kernel stack, thread_info flags/preempt counters,
EPC/EPSR/USP control registers, syscall return value slots, and context-tracking state

## Dependencies and Integration Points

depends on ABI entry macros, asm-offsets constants, syscall table layout, context tracking,
preemption, signal notification, page fault/trap C handlers, and thread_info flags

## Risks and Test Signals

stack-frame offsets, user/kernel mode tests, syscall argument placement for ABI v1/v2, and interrupt
enable ordering are critical; boot, syscall tracing/seccomp, signal, page-fault, and preemption
tests are the test signals
