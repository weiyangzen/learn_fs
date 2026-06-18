# File Research: sources/cow-pools/bcachefs-tools/fs/util/varint.h

Purpose: Public declarations for varint encode/decode helpers.

Key APIs and behavior:
- Declares safe encode/decode and fast encode/decode variants.
- All functions operate on `u8 *`/`const u8 *` buffers and `u64` values.

Integration:
- Implemented by `varint.c`.

Risks and invariants:
- Header does not document the fast-path padding assumptions; callers need to know them from implementation or surrounding conventions.
