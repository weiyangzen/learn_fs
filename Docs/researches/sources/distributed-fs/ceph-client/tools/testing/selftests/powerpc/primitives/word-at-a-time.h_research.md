# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/word-at-a-time.h

## Purpose
`word-at-a-time.h` is a copied kernel helper for detecting zero bytes in machine words and for safely loading unaligned words with zero padding across a fault boundary.

## Important APIs, Types, and Functions
It defines architecture-specific `struct word_at_a_time`, `WORD_AT_A_TIME_CONSTANTS`, `has_zero()`, `prep_zero_mask()`, `create_zero_mask()`, `find_zero()`, `zero_bytemask()`, and `load_unaligned_zeropad()`. The load helper uses exception-table annotations through `EX_TABLE`.

## Control Flow and State
The zero-byte helpers are inline arithmetic/bit operations that produce masks and byte indexes. `load_unaligned_zeropad()` performs an unaligned load and, if a protected following page faults, uses the exception-table fixup to mask unavailable bytes to zero. State is only local registers plus exception-table metadata consumed by the test's signal handler.

## Dependencies and Integration Points
It depends on `linux/wordpart.h`, `asm/extable.h`, powerpc bit operations such as count-leading/trailing-zero helpers provided by the including test, and the primitives harness.

## Risks and Test Signals
Risks include endian-specific mask errors, bad exception-table annotations, and undefined behavior around page boundaries. Test signals are exact agreement between protected zero-padded loads and normal loads from a temporarily unprotected zero-filled second page.
