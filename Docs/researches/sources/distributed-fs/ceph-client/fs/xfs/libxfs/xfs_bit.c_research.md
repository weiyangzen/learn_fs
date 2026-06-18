# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_bit.c

## Purpose
`xfs_bit.c` provides small bitmap scanning helpers used by non-realtime XFS code. The routines operate on arrays of unsigned integer words and implement empty-map detection, contiguous set-bit counting, and next-set-bit lookup.

## Important APIs, types, and functions
The file implements `xfs_bitmap_empty`, `xfs_contig_bits`, and `xfs_next_bit`. The functions use word-level constants from `xfs_bit.h` and platform bit primitives such as `ffz` and `ffs`.

## Control flow
`xfs_bitmap_empty` linearly scans `size` words and returns 1 only if all words are zero. `xfs_contig_bits` starts at `start_bit`, masks off earlier bits in the first word by forcing them to one, scans full words while they are all ones, and returns the count up to the first zero bit. `xfs_next_bit` starts at `start_bit`, masks off earlier bits in the first word by forcing them to zero, scans for a nonzero word, and returns the absolute bit index of the first set bit or `-1`.

## State and persistence behavior
These helpers are pure in-memory bitmap readers. They do not allocate, log, mutate state, or persist anything. The only state assumptions are the supplied map pointer, word count, and starting bit.

## Dependencies and integration points
The code includes `xfs_platform.h`, `xfs_log_format.h`, and `xfs_bit.h`. It is a generic libxfs utility and can support allocation or metadata code that represents state as bitmaps. It relies on `NBWORD`, `BIT_TO_WORD_SHIFT`, `ASSERT`, `ffs`, and `ffz` definitions from the platform/kernel environment.

## Risks and edge cases
`size` is a word count, not a byte or bit count, which is easy to misuse. `xfs_contig_bits` asserts that `start_bit` is within the map, while `xfs_next_bit` returns `-1` if the start is beyond the map. Both scanning routines assume the bitmap is padded to a full word. Care is needed near word boundaries because the first partial word is treated specially. Return type is `int`, so callers should not use maps larger than representable bit indexes.

## Test signals
Unit-style tests should cover empty maps, all-ones maps, starts at zero, starts inside a word, starts on word boundaries, starts at the final bit, starts beyond the map for `xfs_next_bit`, contiguous runs ending in the first word and later words, and maps with padding bits set or clear according to caller expectations.
