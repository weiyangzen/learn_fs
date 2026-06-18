# sources/distributed-fs/ceph-client/fs/xfs/scrub/off_bitmap.h

## Purpose
`off_bitmap.h` provides a small type-safe wrapper around `xbitmap64` for file-offset ranges expressed as `xfs_fileoff_t` and `xfs_filblks_t`.

## Important APIs, Types, And Functions
`struct xoff_bitmap` contains a single `xbitmap64`. Inline helpers are `xoff_bitmap_init`, `xoff_bitmap_destroy`, `xoff_bitmap_set`, and `xoff_bitmap_walk`.

## Control Flow
Callers initialize the wrapper, add file-offset ranges, walk the bitmap with an `xbitmap64_walk_fn`, and destroy it. All real range coalescing and iteration behavior is delegated to `xbitmap64`.

## State And Persistence Behavior
The state is entirely in memory and exists only for scrub or repair bookkeeping. No filesystem metadata is changed directly.

## Dependencies And Integration Points
It depends on `xbitmap64` and XFS file offset types. It is intended for scrub code that wants stronger type signaling than raw 64-bit bitmap helpers.

## Risks And Edge Cases
The wrapper does not add validation beyond the underlying bitmap. Incorrect unit conversion by callers remains possible if callers pass byte offsets instead of file block offsets.

## Test Signals
Tests should exercise empty bitmaps, adjacent range coalescing, large offsets, and callback ordering through `xoff_bitmap_walk`.
