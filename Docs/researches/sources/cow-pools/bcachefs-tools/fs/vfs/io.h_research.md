# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/io.h

Purpose: public declarations and small helpers for the VFS I/O layer.

Key contents:
- `struct nocow_flush` embeds a bio used for block-device preflushes after nocow writes.
- `struct folio_vec` plus `bio_for_each_folio()` adapters iterate bios at folio granularity.
- `struct quota_res` tracks reserved sectors for quota preallocation.
- Inline quota reservation add/put helpers update `inode->ei_quota_reserved` under quota locking when quota is enabled; stubbed to no-ops otherwise.
- Declares fsync, truncate, fallocate, remap, llseek, nocow flush, i_size update, and fault-disabled mapping helpers.

Important interactions:
- Included by `io.c`, `pagecache.c`, and other VFS I/O implementation files.
- Bridges disk reservation, quota reservation, folio state, and inode accounting.
