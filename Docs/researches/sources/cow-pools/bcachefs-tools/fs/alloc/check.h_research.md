# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/check.h

This header declares allocation consistency-check and freespace initialization APIs.

Exports:
- `bch2_need_discard_or_freespace_err()` reports incorrect freespace or need-discard derived-index state.
- `need_discard_or_freespace_err()` and `need_discard_or_freespace_err_on()` wrap that helper in fsck error handling macros.
- `__bch2_check_freespace_key()` validates one freespace btree position against alloc state, returning both bucket generation and optional `journal_seq_empty`.
- `bch2_check_freespace_key_async()` is the allocator-path wrapper that uses `FSCK_ERR_NO_LOG` and no write-buffer flush tracker.
- `bch2_check_alloc_info()` runs the alloc/freespace/need-discard/bucket-gens consistency pass.
- `bch2_check_alloc_to_lru_refs()` verifies alloc-to-LRU and stripe references.
- `bch2_dev_freespace_init()` initializes freespace state for one device range.
- `bch2_fs_freespace_init()` initializes freespace state for all devices that need it.

Role:
- This is the public interface for allocation-derived-index verification, runtime freespace validation, and mount/device-add freespace initialization.
