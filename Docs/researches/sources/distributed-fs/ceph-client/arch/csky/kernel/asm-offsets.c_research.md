# sources/distributed-fs/ceph-client/arch/csky/kernel/asm-offsets.c

## Purpose

generates assembler-visible offsets for C-SKY task, thread, pt_regs, signal, and ABI structures

## Important APIs, Types, and Functions

Source read size: 84 lines, 3971 bytes. Includes: `linux/sched.h`, `linux/kernel_stat.h`,
`linux/kbuild.h`, `abi/regdef.h`. Functions: `main`. Key macros/defines: `COMPILE_OFFSETS`.

## Control Flow and Behavior

DEFINE/OFFSET entries are compiled by Kbuild into asm-offsets.h for assembly files such as entry.S
and context-switch code

## State and Persistence

there is no runtime state; the generated header is build output that must match compiled C layouts

## Dependencies and Integration Points

integrates with Kbuild, ABI entry macros, signal frame code, and low-level assembly save/restore
paths

## Risks and Test Signals

layout drift breaks assembly at runtime; the offsets build step and any code using
pt_regs/thread_info are the validation signals
