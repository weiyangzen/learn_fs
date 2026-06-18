# sources/distributed-fs/ceph-client/arch/s390/lib/mem.S

## Purpose
Provides optimized s390 assembly implementations of core memory operations: `memmove`, `memset`, `memcpy`, and typed memset variants.

## Important APIs, Types, And Functions
Defines and exports `__memmove`/`memmove`, `__memset`/`memset`, `__memcpy`/`memcpy`, `__memset16`, `__memset32`, and `__memset64`. It also emits a branch-return thunk for `%r14` via nospec macros.

## Control Flow And State
`__memmove` chooses forward copy unless destination overlaps the source from above, in which case it copies bytewise in reverse. Forward copy uses 256-byte `mvc` chunks plus an `exrl`-driven remainder. `__memset` specializes zero fill using `xc`, nonzero fill by seeding the first byte then expanding with `mvc`, and handles single-byte cases. `__memcpy` performs forward 256-byte chunks and a remainder. The typed memset macro stores a 16/32/64-bit seed, copies it across 256-byte blocks, and handles remainders.

## Dependencies And Integration
Depends on s390 assembler, `linux/linkage.h`, export macros, and nospec branch macros. These symbols back generic kernel memory APIs on s390.

## Risks And Test Signals
Risks include overlap handling regressions, `exrl` length calculation mistakes, clobber/ABI mismatches, zero-length corner cases, and speculation-thunk changes. Signals include lib/string tests, boot-time memory operations, KASAN/KMSAN reports, compiler built-in replacement tests, and objtool/assembler validation.
