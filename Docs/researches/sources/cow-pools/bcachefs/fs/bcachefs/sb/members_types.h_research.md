# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_types.h

This header defines `struct bch_member_cpu`, the in-memory CPU-endian projection of an on-disk member record.

Fields include:
- Bucket geometry:
  - `nbuckets`
  - `nbuckets_minus_first`
  - `first_bucket`
  - `bucket_size`
- Placement/availability metadata:
  - `group`
  - `state`
  - `discard`
  - `data_allowed`
  - `durability`
- Operational flags:
  - `freespace_initialized`
  - `resize_on_mount`
  - `rotational`
  - `valid`
- Btree allocation bitmap state:
  - `btree_bitmap_shift`
  - `btree_allocated_bitmap`

Research notes:
- This is intentionally compact and mirrors the decoded fields produced by `bch2_mi_to_cpu()` in `members.h`.
- The include-guard closing comment appears to name `_BCACHEFS_SB_MEMBERS_H` rather than `_BCACHEFS_SB_MEMBERS_TYPES_H`; functionally harmless but notable.
