# sources/distributed-fs/ceph-client/fs/xfs/scrub/dab_bitmap.h

Purpose: Provides a tiny type-checked wrapper around `xbitmap32` for directory/attribute block numbers (`xfs_dablk_t`).

Important APIs, types, and functions: Defines `struct xdab_bitmap` containing an `xbitmap32`, plus inline wrappers `xdab_bitmap_init()`, `xdab_bitmap_destroy()`, `xdab_bitmap_set()`, and `xdab_bitmap_test()`.

Control flow: Users initialize the bitmap, set directory/attribute block-number ranges with lengths, test whether a block is present and optionally retrieve the contiguous length, then destroy the bitmap.

State and persistence: All state is transient in-memory bitmap state. No filesystem metadata is persisted.

Dependencies and integration points: Used by scrub or repair code that needs to track DA block ranges without mixing them with fsblocks or file offsets. It depends on `xbitmap32` and XFS DA block typedefs.

Risks and test signals: The main risk is unit confusion: callers must pass DA block numbers and extents, not fsblocks or byte offsets. Test with boundary DA block values, overlapping ranges, empty ranges, and callers that convert between directory data pointers and DA blocks.
