# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.h

## Purpose
Declares the reusable radix sorter API for byte-array key pointers.

## Important APIs, Types, And Functions
Forward-declares `struct radix_sorter` and exposes `uds_make_radix_sorter()`, `uds_free_radix_sorter()`, and `uds_radix_sort()`. The sort takes `const unsigned char *keys[]`, a count, and fixed key length.

## Control Flow
Callers allocate a sorter for a maximum count, call `uds_radix_sort()` for one or more arrays within that capacity, then free the sorter. The implementation chooses insertion sort for small piles.

## State And Persistence
The sorter is scratch memory only and has no persistent format. Sorting mutates only the pointer array, not the key bytes.

## Dependencies And Integration Points
No indexer-specific includes beyond the API itself; it is a utility module available to other indexer code.

## Risks
The algorithm is explicitly unstable, so callers must not rely on relative ordering of equal keys. The sorter capacity must be at least the largest count passed to sort.

## Test Signals
Compile coverage plus sorting tests for fixed-length names, duplicate keys, and sorter reuse are the primary signals.
