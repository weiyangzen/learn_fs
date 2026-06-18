# sources/distributed-fs/ceph-client/arch/microblaze/kernel/asm-offsets.c

## Purpose

generates assembler-visible offsets for MicroBlaze task, thread, pt_regs, CPU, and irq structures

## Important APIs, Types, and Functions

Source read size: 132 lines, 5299 bytes. Includes: `linux/init.h`, `linux/stddef.h`,
`linux/sched.h`, `linux/kernel_stat.h`, `linux/ptrace.h`, `linux/hardirq.h`, `linux/thread_info.h`,
`linux/kbuild.h`, `asm/cpuinfo.h`. Defined functions: `Copyright`. Declared functions: `DEFINE`. Key
macros/defines: `COMPILE_OFFSETS`.

## Control Flow and Behavior

main() emits DEFINE/OFFSET values through linux/kbuild.h so entry.S, exception handlers, and context
switch assembly can address C structures correctly

## State and Persistence

there is no runtime state; persistent output is generated asm-offsets.h in the build tree

## Dependencies and Integration Points

integrates with Kbuild generated headers, low-level entry/exception/context-switch assembly, and CPU
info structures

## Risks and Test Signals

layout drift causes subtle register save/restore corruption; the generated offsets build step, boot,
syscall, interrupt, and signal tests are signals
