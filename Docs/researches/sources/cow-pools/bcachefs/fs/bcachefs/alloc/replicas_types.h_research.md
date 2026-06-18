# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas_types.h

In-memory replicas type declarations.

Defines:
- `struct bch_replicas_entry_cpu`, wrapping a variable-length v1 entry with an atomic refcount.
- `struct bch_replicas_cpu`, containing entry count, fixed padded CPU entry size, and entry storage pointer.
- `union bch_replicas_padded`, stack-friendly storage large enough for max pointer count.

Purpose:
- Supports sorted fixed-stride in-memory lookup even though on-disk replica entries are variable length.
