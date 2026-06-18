# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/check.h

This header declares allocator checking and freespace initialization APIs.

It exposes:
- `bch2_need_discard_or_freespace_err()` plus wrapper macros for fsck-style error handling.
- `__bch2_check_freespace_key()` for validating a freespace key, with fsck flags and optional write-buffer flush tracking.
- `bch2_check_freespace_key_async()` as a no-log async repair-oriented wrapper.
- `bch2_check_alloc_info()` for the full alloc/freespace/need-discard/bucket-gens consistency pass.
- `bch2_check_alloc_to_lru_refs()` for alloc-to-LRU and stripe reference checking.
- `bch2_dev_freespace_init()` and `bch2_fs_freespace_init()` for populating freespace indexes for devices or the whole filesystem.

The header is the public interface for the consistency machinery implemented in `alloc/check.c`.
