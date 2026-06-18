# sources/distributed-fs/ceph-client/fs/btrfs/tests/chunk-allocation-tests.c

## Purpose

`chunk-allocation-tests.c` tests pending extent helper behavior in the Btrfs chunk allocator. The target production functions search the per-device `alloc_state` extent I/O tree for pending chunk allocations and holes that are still available.

## Important APIs, Types, And Functions

- `struct pending_extent_test_case` describes a search range, minimum hole size, up to two pending extents, and expected `btrfs_find_hole_in_pending_extents()` output.
- `find_hole_tests[]` covers empty pending state, overlaps at range start/end, multiple holes, holes too small, fully allocated ranges, and zero-length search input.
- `test_find_hole_in_pending()` builds dummy `fs_info` and device state, sets `CHUNK_ALLOCATED` bits, calls `btrfs_find_hole_in_pending_extents()` under `chunk_mutex`, validates returned range/found state, and clears pending bits each iteration.
- `struct first_pending_test_case` and `first_pending_tests[]` describe expected output from `btrfs_first_pending_extent()`.
- `test_first_pending_extent()` validates first-pending lookup for absent, exact, overlapping, inside, outside, and end-overlapping ranges.
- `btrfs_test_chunk_allocation()` runs both helper test groups.

## Control Flow

Each test allocates a dummy filesystem and dummy device, then iterates a static table. For non-empty pending extents it marks `device->alloc_state` with `CHUNK_ALLOCATED`. The production helper is called while holding `fs_info->chunk_mutex`, mirroring allocator locking. On mismatch, the test logs the named case, clears the extent tree state, and exits with `-EINVAL`.

## State And Persistence Behavior

State is entirely in memory in `device->alloc_state`. The tests use byte ranges at GiB-scale boundaries but only manipulate extent-state metadata, not real storage. Cleanup clears all `CHUNK_ALLOCATED` bits and frees the dummy `fs_info`, which frees the dummy device.

## Dependencies And Integration Points

The tests depend on `btrfs_alloc_dummy_fs_info()`, `btrfs_alloc_dummy_device()`, extent I/O tree bit helpers, `fs_info->chunk_mutex`, and production chunk allocation helpers in `volumes.c`/related code.

## Risks

The table assumes at most two pending extents, enough to produce up to three holes. If production behavior changes to prefer a different “best” hole when no hole meets the minimum size, the expected start/len for `expected_found=false` cases may need updates. Locking is represented only by a mutex around the helper call, not by concurrent allocator threads.

## Test Signals

Success is zero from `btrfs_test_chunk_allocation()`. Failures name the table case and print expected versus actual found state or range. Coverage is strong for range-boundary semantics and weak for real chunk allocation side effects.
