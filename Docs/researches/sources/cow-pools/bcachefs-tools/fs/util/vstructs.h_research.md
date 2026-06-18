# File Research: sources/cow-pools/bcachefs-tools/fs/util/vstructs.h

Purpose: Macros for variable-length on-disk structures whose payload length is measured in u64s.

Key APIs and behavior:
- Reads `_s->u64s` with endian conversion depending on field type.
- Computes total u64s, bytes, block count, sector count, next/end pointers, and indexed entries.
- Provides iteration macros over variable-length embedded records.

Integration:
- Depends on `util.h` for type inspection and common helpers.
- Intended for structures with `_data`, `start`, and `u64s` conventions.

Risks and invariants:
- Assumes `_data` offset is u64-aligned.
- Notes inability to distinguish `__le64` from `u64` with `type_is`, assuming little-endian semantics for u64 fields.
