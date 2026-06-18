# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/members_format.h

This header defines the persistent/on-disk superblock member format and member-related constants/enums.

Key definitions:
- `BCH_SB_MEMBERS_MAX` is 64, due to current use of device bitmasks.
- `BCH_SB_MEMBER_INVALID` is 255, a sentinel for no device.
- `BCH_SB_MEMBER_DELETED_UUID` marks a deleted member slot.
- `BCH_MIN_NR_NBUCKETS` sets the minimum bucket count.
- IOPS measurement enum:
  - sequential read/write
  - random read/write
- Member error enum:
  - read
  - write
  - checksum
- `struct bch_member` is the on-disk member record, including:
  - UUID
  - bucket geometry
  - flags
  - IOPS estimates
  - persistent error counters
  - sequence number
  - btree allocation bitmap
  - journal restart hints
  - fixed-width device name/model/serial fields
  - flush error counter
- `BCH_MEMBER_V1_BYTES` preserves older fixed member size compatibility.
- `struct bch_sb_field_members_v1` stores fixed-size member records.
- `struct bch_sb_field_members_v2` adds `member_bytes` for extensible member records.

Important bitfields:
- State, discard, data-allowed mask, group, durability.
- Freespace initialized, resize-on-mount, rotational, rotational-set.
- Member states: `rw`, `ro`, `evacuating`, `spare`.

Important invariants:
- New fields can be appended to `struct bch_member` because v2 stores per-record byte size.
- `BCH_MEMBER_NBUCKETS_MAX` is constrained by large kernel allocation limits for bucket-generation arrays.
- `BCH_MI_BTREE_BITMAP_SHIFT_MAX` derives from 64 bitmap entries and u64 sector addressability.

Research notes:
- This file is pure format ABI. Changes here affect compatibility and recovery.
- The v1/v2 split explains the padded copy logic in `members.h`.
