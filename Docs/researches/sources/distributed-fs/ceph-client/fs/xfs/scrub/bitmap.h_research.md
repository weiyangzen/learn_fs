# sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.h

## Purpose
This header declares sparse bitmap APIs for 64-bit and 32-bit range sets used by XFS scrub and repair. It defines the storage wrapper types and the callback contracts for iterating set intervals.

## Important APIs, types, and functions
`struct xbitmap64` and `struct xbitmap32` both contain an `rb_root_cached`. The declared operations initialize, destroy, set, clear, subtract (`disunion`), count set bits (`hweight`), walk intervals, test a range prefix, and check emptiness. `xbitmap32_count_set_regions` additionally counts intervals. `xbitmap64_walk_fn` and `xbitmap32_walk_fn` define the callback signatures.

## Control flow and state
The header documents that walk callbacks return zero to continue and nonzero to stop, and reserves `-ECANCELED` as a caller-directed early-stop value. Callers must not modify the bitmap while walking it. The actual tree state and interval coalescing are private to `bitmap.c`.

## Persistence and integration
The API is purely in-memory. It is used directly and through typed wrappers for AG blocks, filesystem blocks, and AG inode numbers. Repair code relies on stable interval semantics to subtract live metadata from broad ownership scans before reaping suspected stale blocks.

## Risks and test signals
Risks are mostly API misuse: forgetting `destroy`, using nonpositive lengths, assuming callbacks can mutate the tree, and treating `hweight` as interval count. Tests should validate callback early-stop propagation, empty bitmap behavior, 32-bit and 64-bit boundary ranges, and wrapper-specific type conversions.
