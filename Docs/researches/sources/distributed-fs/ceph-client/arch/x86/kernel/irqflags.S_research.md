# sources/distributed-fs/ceph-client/arch/x86/kernel/irqflags.S

## Purpose
Provides the noinstr assembly implementation of `native_save_fl()`, returning current x86 flags.

## Important APIs And State
Exports `native_save_fl`. The function is placed in `.noinstr.text`, begins with ENDBR, executes `pushf`, pops into the return register, and returns. It has no persistent state.

## Control Flow And Dependencies
This is a minimal helper used by low-level interrupt flag APIs. It depends on asm register-width macros and linkage/export annotations so the same source works for 32-bit and 64-bit builds.

## Risks And Test Signals
Risks are limited but important: instrumentation must not be inserted, flags width must match ABI, and ENDBR/IBT annotations must be valid. Test signals include objtool noinstr validation, native irq flag save/restore tests, and successful exports for modules or paravirt users.
