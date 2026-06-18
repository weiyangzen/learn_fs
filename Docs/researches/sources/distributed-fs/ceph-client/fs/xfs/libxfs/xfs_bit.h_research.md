# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.h

## Purpose
`xfs_bit.h` declares XFS bit manipulation utilities and provides inline helpers for masks and high/low bit lookup on 32-bit and 64-bit integers. It also declares the bitmap scanning functions implemented in `xfs_bit.c`.

## Important APIs, types, and functions
Inline helpers are `xfs_mask64hi`, `xfs_mask32lo`, `xfs_mask64lo`, `xfs_highbit32`, `xfs_highbit64`, `xfs_lowbit32`, and `xfs_lowbit64`. External declarations are `xfs_bitmap_empty`, `xfs_contig_bits`, and `xfs_next_bit`.

## Control flow
Mask helpers build high or low bit masks through shifts. High-bit helpers wrap `fls`/`fls64` and convert from one-based results to zero-based bit indexes, returning `-1` when no bit is set. Low-bit helpers similarly use `ffs`; the 64-bit variant checks the low 32 bits first, then the high 32 bits and adds 32 to the one-based result before returning a zero-based index.

## State and persistence behavior
All inline helpers are pure computations with no side effects. They do not touch persistent filesystem state. Their correctness matters because callers often use bit positions for metadata sizing, scanning, and allocation decisions.

## Dependencies and integration points
The header relies on kernel/platform bit primitives `fls`, `fls64`, and `ffs`, along with XFS integer typedefs. It is included by `xfs_bit.c` and other libxfs code that needs portable bit utility wrappers.

## Risks and edge cases
The mask helpers assume valid shift counts; passing 0 to `xfs_mask64hi` or a full word size to low-mask helpers can produce undefined C shift behavior depending on the expression. Callers must treat high/low bit returns as zero-based indexes and handle `-1` for zero input. `xfs_lowbit64` deliberately splits the value into two 32-bit halves, so tests should cover high-only values.

## Test signals
Tests should verify zero inputs, single-bit values at low and high positions, mixed-bit values, mask generation for representative counts, and consistency with kernel bit primitive expectations. Static analysis should look for unsafe mask calls with variable counts that can be 0 or word-sized.
