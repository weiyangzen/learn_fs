# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/discard.c

Implements bcachefs discard/TRIM processing and cached-bucket invalidation for the bcachefs-tools source tree. The file operates over `BTREE_ID_need_discard`, alloc keys, per-device discard work, the btree write buffer, journal rewind state, LRU entries, and backpointers.

Key responsibilities:
- Track discard bios in `c->discards.in_flight`, with global and per-device in-flight reference counters.
- Submit `REQ_OP_DISCARD` bios for buckets whose alloc key is `BCH_DATA_need_discard`.
- Convert discarded alloc keys from `BCH_DATA_need_discard` to `BCH_DATA_free` after IO completion.
- Enforce reuse safety with `journal_seq_empty`, `journal.flushed_seq_ondisk`, and `journal.rewind_seq_ondisk`.
- Compute per-device discard release pressure, advancing journal rewind sequence when pending discard buckets are blocking free space.
- Flush the journal and btree write buffer when discard progress requires them.
- Provide normal async discard work and a fast per-device discard queue for recently closed open buckets.
- Invalidate cached buckets by walking LRU entries, resolving bucket backpointers, dropping the removed/invalidated device from referenced keys, and converting unreadable keys to `KEY_TYPE_ERROR_device_removed`.

Important control flow:
- `bch2_do_discards()` scans `BTREE_ID_need_discard` ordered by journal sequence, calls `bch2_discard_one_bucket()`, drains completed discards, then handles journal rewind/write-buffer flush policy.
- `bch2_discard_one_bucket()` checks nouse buckets, duplicate in-flight entries, fastpath eligibility, journal flush state, rewind state, alloc data type, open-bucket state, device write refs, discard hardware support, and `opts.nochanges`.
- `__discard_mark_free()` is the committed alloc-btree state transition. It clears the compatibility discard flag, sets `data_type = BCH_DATA_free`, clears journal sequence fields, updates with `BTREE_TRIGGER_is_discard`, and commits at reclaim watermark.
- `discard_endio()` only marks an in-flight entry complete and drops the IO counters. Alloc-btree updates and device write-ref release are completed later by `bch2_discards_complete()`.
- `calculate_discard_sectors_to_release()` computes discard pressure per device so one device’s need-discard backlog cannot be hidden by filesystem-wide free space.
- `__bch2_do_invalidates()` starts from the cached-bucket LRU, validates alloc-key/LRU consistency, then invalidates buckets by their backpointers.

Concurrency and lifetime:
- `c->discards.lock` protects `in_flight`, `ref`, and `refs[]`.
- Device write refs are held until the alloc-btree mark-free update has committed, preventing device removal from deleting the same alloc-btree range concurrently.
- Work is queued on `c->write_ref_wq` and guarded by filesystem/device enumerated write refs.
- Fast discard queues are per-device darrays guarded by `discard_fast_lock`.

Failure behavior:
- If a post-discard alloc key is no longer `BCH_DATA_need_discard` in `__discard_mark_free()`, the filesystem is forced emergency read-only.
- Expected write-buffer races where an alloc key no longer has need-discard state are counted as `bad_data_type`.
- Worker exits suppress `EROFS`-style errors but log other failures.
