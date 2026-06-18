# File Research: sources/cow-pools/bcachefs-tools/fs/util/varint.c

Purpose: Encodes and decodes bcachefs variable-length unsigned integers.

Key APIs and behavior:
- `bch2_varint_encode()` emits 1 to 9 bytes using low-bit prefix markers.
- `bch2_varint_decode()` determines width with `ffz()` and checks the buffer end.
- Fast variants assume it is safe to read/write up to 8 bytes beyond the logical varint footprint, while still reporting bounds errors.
- Values needing 9 bytes use marker byte `255` followed by raw little-endian u64.

Integration:
- Implements `varint.h`.
- Uses `BCH_ERR_varint_decode_error` from `errcode.h`.

Risks and invariants:
- Fast decode requires padded readable memory; Valgrind memory is marked defined when configured.
- Decode comments say "encode" in one docblock, but behavior is decode.
