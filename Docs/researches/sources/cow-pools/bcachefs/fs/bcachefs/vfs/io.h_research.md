# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/io.h

Declares VFS I/O helpers and inline quota/pagecache support used by buffered I/O, direct I/O, fsync, truncate, fallocate, remap, and seek paths.

Key declarations:
- `struct nocow_flush` wraps a flush bio with closure and device ownership metadata.
- `struct folio_vec` and bio iteration helpers convert `bio_vec` segments into folio-relative segments.
- `struct quota_res` tracks reserved quota sectors for pending write/fallocate work.
- Quota helpers reserve and release `Q_SPC` preallocations, with snapshot inodes bypassing quota reservation.
- Public functions cover sector accounting, nocow flushes, size writes, fsync, post-EOF zeroing, truncate, fallocate, remap, and bcachefs `llseek`.

Core mechanics:
- `biovec_to_foliovec()` computes folio-relative offset/length even when a `bio_vec` page is part of a larger folio.
- `bio_for_each_folio()` iterates the current bio iterator by folio-sized subsegments.
- `bch2_quota_reservation_add()` takes `ei_quota_lock`, charges quota in preallocation or nocheck mode, updates `ei_quota_reserved`, and accumulates the local reservation.
- `bch2_quota_reservation_put()` reverses outstanding quota reservations under the inode quota lock.
- Fault-disabled mapping helpers wrap the filesystem `fdm_table` used by page-fault lock-order handling.

Important invariants:
- Quota reservation release asserts that the local reservation does not exceed `inode->ei_quota_reserved`.
- `bch2_i_sectors_acct()` serializes nonzero sector accounting through `ei_quota_lock`.
- Snapshot inodes do not take quota reservations.

Filesystem relevance:
- This header is the compact contract between the VFS I/O code and lower bcachefs allocation/quota/pagecache subsystems.

Notable risks:
- The no-quota build stubs make reservation calls no-ops, so code using them must still be correct without quota side effects.
