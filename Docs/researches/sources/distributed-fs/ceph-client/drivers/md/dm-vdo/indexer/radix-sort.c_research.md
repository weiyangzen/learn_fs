# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/radix-sort.c

## Purpose
Implements a reusable in-place American Flag radix sorter for arrays of pointers to fixed-length byte keys. It is used where deterministic bytewise ordering of record names or index keys is needed without moving the key storage itself.

## Important APIs, Types, And Functions
Public functions are `uds_make_radix_sorter()`, `uds_free_radix_sorter()`, and `uds_radix_sort()`. Private types are `sort_key_t`, `histogram`, `task`, and `radix_sorter`. Important helpers are `measure_bins()`, `push_bins()`, `insertion_sort()`, `insert_key()`, `swap_keys()`, and `push_task()`.

## Control Flow
`uds_make_radix_sorter(count, ...)` allocates one object with a task stack sized roughly by `count / INSERTION_SORT_THRESHOLD`. `uds_radix_sort()` handles empty/zero-length/small cases, then manually processes tasks from a stack. For each task it counts byte frequencies at the current offset, computes pile endpoints, pushes large piles back onto the stack and small piles onto an insertion-sort list, performs in-place pile swaps until all bins are positioned, clears reused histogram state as it goes, and insertion-sorts small piles.

## State And Persistence
There is no persistent state. The sorter holds reusable scratch state (`histogram`, pile pointers, insertion task list, and stack) sized for a maximum count. Input keys are immutable byte arrays; the array of key pointers is reordered. The algorithm is unstable.

## Dependencies And Integration Points
Depends on allocation and string/memcmp utilities. It is a general helper for indexer components that need sorted key pointers, likely chapter-index or volume code outside this subset.

## Risks
The implementation relies on the histogram being zeroed by prior processing rather than clearing it before every bin measurement. Any early exit path must clear it, and any modification to bin loops must preserve that invariant. The sorter rejects counts greater than its configured capacity but only after small-count fast path. Stack sizing is algorithm-specific; unexpected push growth returns `UDS_BAD_STATE`.

## Test Signals
Test zero count, zero length, small insertion-sort paths, already sorted/reverse/random keys, duplicate keys, keys with long shared prefixes, all 256 byte values, count greater than sorter capacity, and reuse of a sorter across multiple sorts after an error.
