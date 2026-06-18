# sources/distributed-fs/ceph-client/fs/hpfs/buffer.c

Purpose: this file centralizes HPFS sector mapping, read-ahead, hotfix remapping, and four-sector dnode buffer handling.

Important APIs and functions: `hpfs_search_hotfix_map()` maps a bad original sector to its spare replacement. `hpfs_search_hotfix_map_for_range()` clips contiguous ranges before a hotfix. `hpfs_prefetch_sectors()` performs safe read-ahead. `hpfs_map_sector()` and `hpfs_get_sector()` read or allocate single-sector buffers. `hpfs_map_4sectors()` and `hpfs_get_4sectors()` produce a contiguous 2048-byte view over four sectors. `hpfs_brelse4()` and `hpfs_mark_4buffers_dirty()` release/dirty quad buffers.

Control flow: single-sector mapping asserts the global HPFS lock, optionally prefetches, maps through the hotfix table, and reads or gets a buffer. Quad mapping maps four aligned sectors; if their `b_data` pointers are contiguous it returns the first buffer directly, otherwise it allocates a 2048-byte bounce buffer and copies data in/out on dirtying.

State and persistence: read paths populate buffer cache. Write paths mark buffer heads dirty, and for non-contiguous quad buffers copy the synthetic view back to the four underlying sectors before dirtying. Hotfix tables are read-only in-memory mount state loaded elsewhere.

Dependencies and integration: every HPFS metadata mapper uses these functions. Dnodes are exactly four 512-byte sectors, so directory-tree code depends heavily on quad-buffer behavior. File I/O and allocation code also use range clipping to avoid merging across hotfixed sectors.

Risks: all functions require `hpfs_lock()` except prefetch helpers; misuse can trigger lock assertions or races. Quad buffers must always be released with `hpfs_brelse4()` and dirtied with `hpfs_mark_4buffers_dirty()` before release when modified. Hotfix range clipping is necessary for correct contiguous I/O mapping.

Test signals: map/read/write dnodes on devices where four sector buffers are contiguous and non-contiguous, simulate hotfix entries and range clipping, test read errors, verify dirty copy-back from bounce buffers, and run lockdep-style checks for callers missing the HPFS mutex.
