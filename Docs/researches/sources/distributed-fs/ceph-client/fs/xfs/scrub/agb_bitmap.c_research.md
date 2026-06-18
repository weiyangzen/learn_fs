# sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.c

Purpose: Provides scrub helpers to record allocation-group btree blocks into typed AG-block bitmaps.

Important APIs, types, and functions: Exports `xagb_bitmap_set_btblocks` and `xagb_bitmap_set_btcur_path`; internal visitor `xagb_bitmap_visit_btblock` converts a cursor block buffer address to AG block number and sets one bit in `struct xagb_bitmap`.

Control flow: `xagb_bitmap_set_btblocks` uses `xfs_btree_visit_blocks` with `XFS_BTREE_VISIT_ALL` to mark every block in a per-AG btree. `xagb_bitmap_set_btcur_path` is optimized for left-to-right record walks: it climbs cursor levels while each level pointer is at slot one, marking blocks newly encountered along the leaf-to-root path.

State and persistence: State is an incore `xbitmap32` wrapped by `struct xagb_bitmap`. The helpers do not modify filesystem metadata; they collect observed btree block addresses for scrub cross-checks.

Dependencies and integration points: Used by online scrub code for btree ownership/coverage checks. Depends on generic btree cursors, buffer addresses, block conversion macros, and the `xbitmap32` range bitmap implementation.

Risks and test signals: Risks include using the path optimization on non-left-to-right walks, converting non-AG btree blocks, missing root blocks when cursor pointers are not at one, and bitmap allocation failures. Test all per-AG btree scrubbers, empty/single-level/multi-level btrees, corrupted cursor buffers, and memory allocation failure in bitmap set operations.
