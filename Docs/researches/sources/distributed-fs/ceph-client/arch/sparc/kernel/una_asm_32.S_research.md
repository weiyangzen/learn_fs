<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_32.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_32.S

## Purpose
Provides SPARC32 byte-wise integer load/store helpers used by C unaligned-access trap handling when the kernel must emulate unaligned halfword, word, or doubleword memory accesses.

## Important APIs, Types, And Functions
Exports `__do_int_store` and `do_int_load`; local `retl_efault` returns `-EFAULT`. The helper contract is shared with `unaligned_32.c`.

## Control Flow
`__do_int_store` reads one or two source words, decomposes them into bytes, and stores 2, 4, or 8 bytes to the destination. `do_int_load` reads bytes from the unaligned source and assembles 2, 4, or 8 byte values into the destination register storage, sign-extending halfword loads when requested. Each faultable byte access has an exception-table entry that redirects to `retl_efault`.

## State And Persistence
No persistent state is maintained. The only mutation is the requested memory store or destination-register memory write, plus exception-table metadata emitted into `__ex_table`.

## Dependencies And Integration Points
Called from `kernel_unaligned_trap` in `unaligned_32.c`; relies on the generic exception-table fixup mechanism and the SPARC register calling convention.

## Risks And Edge Cases
Byte order and sign extension must match SPARC load/store semantics. Partial stores can occur before a later byte faults, so callers must treat `-EFAULT` as a trap-fixup condition. The C caller must only pass supported sizes.

## Test Signals
Signals include kernel unaligned load/store tests for 2-, 4-, and 8-byte accesses, injected faulting addresses that exercise `__ex_table`, and comparison against naturally aligned SPARC load/store results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/una_asm_32.S -->
