<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/stack.S -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/stack.S

## Purpose
`stack.S` reserves a small heap and stack for 16-bit real-mode C and assembly routines in the realmode blob.

## Important APIs, types, and functions
It exports `HEAP`, `heap_end`, `rm_heap`, `rm_stack`, and global `rm_stack_end`.

## Control flow
The linker places this data in `.data`/`.bss`; trampoline and wakeup code load `rm_stack_end` into ESP before calling C or verification routines.

## State and persistence behavior
Persistent state is 2 KiB heap plus 2 KiB stack storage inside the low-memory real-mode blob. It is reused by AP startup and wakeup paths, with 64-bit trampoline serialization via a lock.

## Dependencies and integration points
It depends on the realmode linker script and consumers such as `trampoline_64.S` and `wakeup_asm.S` using the exported labels.

## Risks and edge cases
Stack size is fixed and small; adding deeper C calls or interrupts in real mode can overflow it. Shared stack use needs locking where multiple APs can enter concurrently.

## Test signals
Signals are successful AP startup/resume under stress and stack-label presence in `pasyms.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/stack.S -->
