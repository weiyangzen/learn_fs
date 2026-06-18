# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_format.h

On-disk replicas format header.

Defines:
- `struct bch_replicas_entry_v0`:
  - `data_type`
  - `nr_devs`
  - flexible `devs[]`
- `struct bch_sb_field_replicas_v0`.
- `struct bch_replicas_entry_v1`:
  - `data_type`
  - `nr_devs`
  - `nr_required`
  - flexible `devs[]`
- `struct bch_sb_field_replicas`.
- `replicas_entry_bytes()` for variable-length entry sizing.
- `replicas_entry_add_dev()` append helper.

Purpose:
- Stores which devices contain each class of data and how many devices/blocks are required to read it.
- V1 adds `nr_required`, enabling degraded/erasure-coded availability checks that v0 cannot express directly.
