# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.h

Declares checksum/encryption APIs and inline policy helpers for data, metadata, and extent nonce construction.

Key contents:
- Mergeability predicate for `none`, `crc32c`, and `crc64`.
- Nonce domain constants for extents, btree, journal, prio, and Poly1305.
- Option-to-checksum mapping helpers for metadata/data checksum choices.
- `extent_nonce()` constructs per-extent nonces from bversion, compression state, size, and CRC nonce.

Important invariants:
- Encryption checksum types require `c->chacha20_key_set`.
- `bch2_crc_cmp()` returns true on mismatch and is intended to avoid early-exit comparison.
- `nonce_add()` advances by ChaCha blocks and asserts block alignment.
- NOCOW data returns checksum type `0`, while encrypted filesystems force ChaCha20-Poly1305 data MACs.

Dependencies and interactions:
- Used by compression, extents, EC IO, and read/write paths for checksum selection, formatting, and nonce handling.
