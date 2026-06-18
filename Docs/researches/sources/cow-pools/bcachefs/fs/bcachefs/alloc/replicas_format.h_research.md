# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_format.h

On-disk replica superblock field formats.

Defines:
- `struct bch_replicas_entry_v0`: data type, device count, flexible device list.
- `struct bch_sb_field_replicas_v0`: variable-length v0 entries.
- `struct bch_replicas_entry_v1`: data type, device count, required count, flexible device list.
- `struct bch_sb_field_replicas`: variable-length v1 entries.
- `replicas_entry_bytes()` for variable entry sizing.
- `replicas_entry_add_dev()` for appending device IDs.

Purpose:
- v1 adds `nr_required`, which is needed for erasure coding and other layouts where “devices listed” is not the same as “devices required to read.”
