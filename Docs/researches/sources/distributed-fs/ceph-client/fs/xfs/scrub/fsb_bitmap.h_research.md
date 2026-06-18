<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fsb_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fsb_bitmap.h

Purpose: Provides a type-specific wrapper around `xbitmap64` for sets of filesystem block numbers (`xfs_fsblock_t`).

Important APIs, types, and functions: Defines `struct xfsb_bitmap` containing `struct xbitmap64 fsbitmap`, plus inline helpers `xfsb_bitmap_init()`, `xfsb_bitmap_destroy()`, `xfsb_bitmap_set()`, and `xfsb_bitmap_walk()`.

Control flow: Users initialize the bitmap, add fsblock ranges with a start and length, iterate merged ranges through an `xbitmap64_walk_fn`, and destroy backing state when done. The wrapper does not add policy beyond type-directed naming.

State and persistence: State is an in-memory interval bitmap. Nothing is persisted; callers use it to stage scrub or repair observations before later action.

Dependencies and integration points: Depends on the generic scrub bitmap implementation and XFS block typedefs. It is intended for repair/scrub code that wants compile-time clarity between fsblock and other address spaces.

Risks and test signals: Main risks are unit mixups at call sites and missed destruction on error paths. Test range insertion/merge, walk ordering, empty walks, allocation failures from the underlying bitmap, and users that translate between AG blocks and fsblocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fsb_bitmap.h -->
