<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/string.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/lib/string.S

## Purpose
Implements OpenRISC bulk usercopy and clear-user assembly helpers with exception-table recovery.

## Important APIs, Types, And Functions
`__copy_tofrom_user(void *to, const void *from, unsigned long size)` copies byte-by-byte and returns bytes not copied. `__clear_user(void *addr, unsigned long size)` zeros user memory and returns bytes not cleared.

## Control Flow
Both routines save argument registers, loop one byte at a time, and use `__ex_table` entries for faulting load/store labels. Fixup jumps to the common exit, returning the remaining byte count.

## State And Persistence
Mutates destination memory and returns partial-copy counts. No persistent state.

## Dependencies And Integration Points
Called from `uaccess.h` raw copy/clear wrappers and exported in `or32_ksyms.c`. Depends on page-fault exception-table fixup handling.

## Risks
Byte-at-a-time implementation is simple but slow. Correct remaining-byte count on fault is ABI-visible. Exception table entries must match faulting labels.

## Test Signals
Usercopy fault injection, partial-copy return values, clear_user tests, and module usercopy helper use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/lib/string.S -->
