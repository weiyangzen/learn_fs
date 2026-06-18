# File Research: sources/cow-pools/bcachefs-tools/fs/data/checksum.h

Declares checksum/encryption interfaces and defines checksum option, nonce, and checksum utility helpers.

Key responsibilities:
- Defines mergeable checksum types: `none`, `crc32c`, and `crc64`.
- Defines nonce domain constants for extents, btree, journal, priority data, and Poly1305.
- Declares checksum, encryption, key request/revoke, bio checksum/encryption, rechecksum, and encryption init/exit APIs.
- Provides `bch2_csum_opt_to_type()`, `bch2_data_checksum_type()`, `bch2_data_checksum_type_rb()`, and `bch2_meta_checksum_type()`.
- Validates checksum type/key availability with `bch2_checksum_type_valid()`.
- Provides nonce helpers: `nonce_add()`, `null_nonce()`, `extent_nonce()`, `__bch2_sb_key_nonce()`, and `bch2_sb_key_nonce()`.
- Provides text formatting helpers for checksums and checksum errors.
- Provides `bch2_key_is_encrypted()` for encrypted superblock-key detection.

Important interactions:
- Data checksum selection is disabled for `nocow`; encryption overrides configured checksum with Chacha20-Poly1305 MACs.
- Metadata under encryption always uses 128-bit Chacha20-Poly1305.
- `extent_nonce()` encodes version, compressed size/type, extent domain, and sector offset into the nonce.

Notable concerns:
- `nonce_add()` asserts Chacha block-size alignment.
- `bch2_crc_cmp()` is logically “not equal” and is intentionally simple, with a comment noting constant-time concerns.
