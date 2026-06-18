# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/replicas_types.h

In-memory replicas type declarations.

Defines:
- `struct bch_replicas_entry_cpu`, containing an atomic refcount and an embedded variable-length `bch_replicas_entry_v1`.
- `struct bch_replicas_cpu`, containing entry count, uniform in-memory entry size, and pointer to the entries array.
- `union bch_replicas_padded`, a stack-safe padded replica entry large enough for `BCH_BKEY_PTRS_MAX` devices.

Purpose:
- Supports efficient sorted lookup and refcounting of variable-length replica entries.
- Provides padded temporary storage for constructing replica entries from bkeys and device lists.
