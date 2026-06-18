# sources/distributed-fs/ceph-client/arch/s390/lib/csum-partial.c

## Purpose
Provides s390 implementations of partial internet checksum calculation and unchecked checksum-copy. It uses vector facility instructions when available and falls back to scalar checksum/memcpy support otherwise.

## Important APIs, Types, And Functions
`csum_copy()` is the shared inline engine. It optionally copies from source to destination and accumulates checksum chunks into vector registers. `csum_partial()` computes a checksum over a buffer with an initial sum. `csum_partial_copy_nocheck()` copies while computing the checksum starting from zero. Both public functions are exported.

## Control Flow And State
If VX is unavailable, copy mode performs `memcpy()` and then calls `cksm()`; non-copy mode calls `cksm()` directly. With VX, the function enters kernel FPU context, seeds vector register 16 with the incoming sum, processes 64-, 32-, and 16-byte chunks using vector load/store/checksum operations, handles a tail with vector load/store logical length, folds partial sums into register 16, extracts the sum, and exits FPU context.

## Dependencies And Integration
Depends on s390 checksum and FPU/vector helper APIs, `cpu_has_vx()`, and exported kernel checksum interfaces used by networking and protocol stacks.

## Risks And Test Signals
Risks include FPU context misuse, odd final-fragment length handling, checksum folding mistakes, destination pointer advancement in copy mode, and mismatches between VX and scalar behavior. Signals include network checksum selftests, packet transmit/receive validation, checksum KUnit or lib tests if present, and testing on systems with and without VX.
