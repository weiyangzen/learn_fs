# sources/distributed-fs/ceph-client/fs/f2fs/segment.h

## Purpose
`segment.h` defines the core constants, address-conversion macros, policy enums, state structures, and inline helpers used by F2FS segment management. It is the contract between allocation, GC, checkpoint, discard, and writeback code for translating block addresses into segments/sections/zones and for maintaining SIT, free-map, dirty-map, curseg, summary, and IPU policy state.

## Important APIs, types, and functions
Important constants include `NULL_SEGNO`, `NULL_SECNO`, `F2FS_MIN_SEGMENTS`, `F2FS_MIN_META_SEGMENTS`, `INVALID_MTIME`, `DEF_RECLAIM_PREFREE_SEGMENTS`, and `DEF_MAX_RECLAIM_PREFREE_SEGMENTS`. Address macros include `MAIN_BLKADDR`, `SEG0_BLKADDR`, `MAIN_SEGS`, `TOTAL_SEGS`, `MAX_BLKADDR`, `START_BLOCK`, `NEXT_FREE_BLKADDR`, `GET_SEGNO`, `GET_SEC_FROM_SEG`, `GET_SEG_FROM_SEC`, `GET_ZONE_FROM_SEC`, `GET_SUM_BLOCK`, and `SIT_BLOCK_OFFSET`.

Policy enums define allocation mode (`LFS`, `SSR`, `AT_SSR`), GC mode (`GC_CB`, `GC_GREEDY`, `GC_AT`, `ALLOC_NEXT`, `FLUSH_DEVICE`), foreground/background GC, and dirty-segment classes. IPU policy bits include force, SSR-triggered, utilization-triggered, fsync, async, no-cache, honor-OPU, and disabled modes.

The key structures are `struct victim_sel_policy`, `struct seg_entry`, `struct sec_entry`, `struct revoke_entry`, `struct sit_info`, `struct free_segmap_info`, `struct dirty_seglist_info`, `struct curseg_info`, and `struct sit_entry_set`. These structures hold GC-victim search parameters, per-segment validity maps and mtimes, section aggregates, atomic revoke entries, SIT cache and checkpoint bitmaps, free segment/section bitmaps, dirty/prefree/victim/pinned bitmaps, active log state, and grouped SIT flush accounting.

Important inline helpers include `CURSEG_I`, `is_curseg`, `is_cursec`, `get_seg_entry`, `get_sec_entry`, `get_valid_blocks`, `get_ckpt_valid_blocks`, `set_ckpt_valid_blocks`, `seg_info_from_raw_sit`, `seg_info_to_sit_folio`, `seg_info_to_raw_sit`, `find_next_inuse`, `__set_free`, `__set_inuse`, `__set_test_and_free`, `__set_test_and_inuse`, `get_sit_bitmap`, `free_segments`, `free_sections`, `prefree_segments`, `dirty_segments`, `__get_secs_required`, `has_not_enough_free_secs`, `f2fs_is_checkpoint_ready`, `utilization`, `curseg_segno`, `curseg_alloc_type`, `valid_main_segno`, `verify_fio_blkaddr`, `check_block_count`, `current_sit_addr`, `next_sit_addr`, `set_to_next_sit`, `get_mtime`, `set_summary`, `start_sum_block`, `sum_blk_addr`, `sec_usage_check`, `nr_pages_to_skip`, `nr_pages_to_write`, and `wake_up_discard_thread`.

## Control flow
Most functions in this header are small invariants used by `segment.c` and neighboring F2FS code. Address conversion starts from superblock or segment-manager fields, maps block addresses relative to `segment0_blkaddr`, then converts through logical-relative segment numbering using `FREE_I(sbi)->start_segno`. Section and zone helpers derive larger allocation/GC units from segment numbers.

Free-map updates use a set-bit means in-use convention for `free_segmap` and `free_secmap`. `__set_free` clears a segment bit, increments free segment count, and may clear the section bit if every usable segment in the section is free. `__set_inuse` sets segment and section bits and decrements counters. The test-and variants are used when state may already be in the desired condition and also reset cached next-victim hints when a whole section becomes free.

SIT conversion helpers load raw little-endian `f2fs_sit_entry` values into `seg_entry` caches and serialize them back during checkpoint. `check_block_count` walks the raw valid-map and verifies the encoded valid block count, segment boundary, and zoned usable-block limit. `current_sit_addr`, `next_sit_addr`, and `set_to_next_sit` implement the double-buffered SIT block selection protocol.

Space-reservation helpers compute whether checkpoints and foreground allocation have enough sections. `__get_secs_required` estimates additional sections needed for dirty node, dentry, imeta, and, in LFS checkpoint-disabled mode, data pages after subtracting room left in current logs. `has_not_enough_free_secs` combines that demand with reserved sections and caller-provided needs.

Writeback helpers tune batching: `nr_pages_to_skip` delays writeout to gather larger BIOs unless the backing device is already dirty-throttled, and `nr_pages_to_write` aligns asynchronous writeback toward BIO-sized or node-sized batches. `wake_up_discard_thread` wakes the discard thread only when pending commands meet granularity and idle conditions, unless forced.

## State and persistence behavior
The structures here distinguish durable checkpoint/SIT state from volatile caches. `seg_entry.cur_valid_map`, `valid_blocks`, and `mtime` are current runtime state that will be flushed to SIT. `seg_entry.ckpt_valid_map` and `ckpt_valid_blocks` preserve last-checkpoint state for SSR and checkpoint-disabled accounting. `sit_info.sit_bitmap` is a checkpoint-persisted selector for active SIT blocks, while `dirty_sentries_bitmap` and `sit_entry_set` are transient checkpoint-flush worklists.

`curseg_info` contains active-log state persisted through checkpoint summaries: segment number, allocation type, segment type, next block offset, summary entries, and journal contents. Its mutex and journal rwsem protect runtime mutation. In-memory-only active logs such as pinned and ATGC segments can be saved/restored around special operations.

Free and dirty maps are derived at mount from SIT and checkpoint summaries rather than directly stored as separate persistent objects. Dirty, prefree, victim, and pinned section maps guide GC and discard decisions until the next rebuild. `sec_entry` aggregates segment counts for large-section mode so GC and free-space decisions do not have to scan every segment repeatedly.

## Dependencies and integration points
The header depends on Linux block and backing-device interfaces and on F2FS global types from including translation units. It is included by segment management, GC, checkpoint, writeback, and node/data paths. It assumes definitions for `struct f2fs_sb_info`, `SM_I`, `SIT_I`, `FREE_I`, `DIRTY_I`, `F2FS_CKPT`, `F2FS_RAW_SUPER`, curseg constants, checkpoint flags, page counters, zoned-device helpers, and bitmap helpers.

It also integrates with block-layer write hints through IPU and temperature decisions, F2FS sysfs options (`active_logs`, discard unit, allocation mode), checkpoint-disabled state, large-section and zoned-volume layouts, and `CONFIG_F2FS_CHECK_FS` mirror/invalid-segment diagnostics.

## Risks
The macros in this header encode foundational address arithmetic. A wrong `start_segno`, segment0/main-area conversion, section rounding, or zoned capacity calculation can redirect allocation, discard, or SIT writes to the wrong area. This is especially sensitive for multi-device and zoned configurations where logical and device-local block addresses differ.

Free-map semantics are easy to misread because set bits mean in-use, not free. Counter updates must stay exactly paired with bitmap transitions, and section counters must account for unusable zoned tail segments. Current segments are deliberately excluded from some free/dirty transitions, so callers must know whether they are operating on current logs or closed segments.

SIT consistency risk is high. `valid_blocks`, `ckpt_valid_blocks`, section aggregates, raw SIT vblocks, current and checkpoint maps, and optional check-fs mirrors must agree. `check_block_count` and `sanity_check_valid_blocks` catch many problems, but only when those paths run.

Space-estimation helpers directly affect checkpoint readiness and foreground GC pressure. Underestimating required sections can lead to ENOSPC or checkpoint failure; overestimating can trigger unnecessary GC or writeback. The estimates depend on active log count and checkpoint-disabled/LFS modes.

## Test signals
Good coverage includes address conversion around `MAIN_BLKADDR`, last main segment, section and zone boundaries, large-section aggregation, zoned `CAP_BLKS_PER_SEC` and partial-capacity segments, and `current_sit_addr`/`next_sit_addr` toggling across both SIT halves. Free-map tests should verify segment and section counters for repeated set/free operations, current-section exclusions, unusable tail segments, and victim hint clearing.

SIT tests should inject raw valid-map/count mismatches, invalid segment numbers, invalid segment types, and check-fs mirror mismatches. Space tests should vary active log counts, dirty dentry/node/data pages, checkpoint-disabled mode, reserved sections, and LFS versus non-LFS allocation. Writeback signals include dirty-throttle behavior for `nr_pages_to_skip`, `nr_pages_to_write` changes in async writeback, and discard-thread wake decisions under idle and non-idle conditions.
