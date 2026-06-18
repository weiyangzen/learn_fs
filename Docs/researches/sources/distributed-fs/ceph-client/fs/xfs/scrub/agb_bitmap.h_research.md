# sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.h

Purpose: Defines a type-checked AG-block bitmap wrapper around `xbitmap32` for online scrub code.

Important APIs, types, and functions: Defines `struct xagb_bitmap` and inline wrappers `xagb_bitmap_init`, `xagb_bitmap_destroy`, `xagb_bitmap_clear`, `xagb_bitmap_set`, `xagb_bitmap_test`, `xagb_bitmap_disunion`, `xagb_bitmap_hweight`, `xagb_bitmap_empty`, `xagb_bitmap_walk`, and `xagb_bitmap_count_set_regions`. Declares btree block marking helpers.

Control flow: Scrub callers initialize a bitmap, add or remove AG-block ranges, test/walk/count regions, optionally subtract another bitmap, and destroy it after checks. The C file extends this with btree cursor collection.

State and persistence: The wrapper stores only an incore `xbitmap32`; no filesystem metadata is changed. Type-specific function signatures reduce accidental use of filesystem block or realtime block units.

Dependencies and integration points: Integrates with scrub bitmap utilities, per-AG btree scans, and xbitmap32 range operations.

Risks and test signals: Risks include unit confusion despite the wrapper, forgotten destroy calls, large fragmented bitmaps under corrupt metadata, and propagation of xbitmap32 allocation errors. Test bitmap set/clear/disunion/walk behavior, large AGs, fragmented ranges, and btree scrub call sites.
