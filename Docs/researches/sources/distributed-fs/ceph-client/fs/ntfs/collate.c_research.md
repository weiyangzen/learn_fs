# sources/distributed-fs/ceph-client/fs/ntfs/collate.c

## Purpose

`collate.c` implements NTFS index collation rules used to order keys in NTFS indexes. It supports binary comparisons, filename collation, single little-endian ULONG comparison, and arrays of little-endian ULONGs.

## Important APIs, Types, And Functions

- `ntfs_collate_binary()` compares byte strings lexicographically and then by length.
- `ntfs_collate_ntofs_ulong()` compares two 4-byte little-endian integers and rejects non-4-byte inputs.
- `ntfs_collate_ntofs_ulongs()` compares arrays of little-endian 32-bit integers and expects equal lengths aligned to 4 bytes.
- `ntfs_collate_file_name()` compares filename attributes first case-insensitively using the volume upcase table and then case-sensitively as a tiebreaker.
- `ntfs_collate()` dispatches based on the on-disk collation rule and returns ordering or `-EINVAL` for unknown/invalid rules.

## Control Flow And Algorithms

The public dispatcher switches on the CPU-converted collation rule. Binary collation is a `memcmp()` over the shorter input plus length comparison. Filename collation delegates to `ntfs_file_compare_values()` twice. ULONG-array collation loops element by element until a difference is found and then returns `cmp_int()`.

## State And Persistence Behavior

The file is pure comparison logic and does not persist state. It reads the volume upcase table for filename ordering and logs errors for unsupported or invalid rules.

## Dependencies And Integration Points

It includes `collate.h`, `debug.h`, `ntfs.h`, and Linux `sort.h` for `cmp_int()`. It integrates with index and directory code that needs to compare NTFS index keys according to the rule stored in an index root.

## Risks And Edge Cases

- `ntfs_collate_ntofs_ulongs()` returns `-1` on invalid length after logging, which is also a valid less-than ordering. That can conflate malformed input with ordering unless callers validate lengths earlier.
- `ntfs_collate_ntofs_ulong()` uses `-EINVAL`, whereas the array variant uses `-1`, so error signaling is inconsistent.
- The switch cases call `le32_to_cpu()` on constants, which assumes the collation constants are typed as little-endian values; this is consistent with the surrounding NTFS style but should stay aligned with definitions.

## Test Signals

Tests should cover binary prefix ordering, filename case-insensitive equality with case-sensitive tiebreak, invalid ULONG lengths, ULONG-array ordering and malformed lengths, and dispatcher behavior for unsupported collation rules.
