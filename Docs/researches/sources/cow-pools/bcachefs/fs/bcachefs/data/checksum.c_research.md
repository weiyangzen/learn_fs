# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/checksum.c

Implements checksum, MAC, encryption, and encryption-key setup for bcachefs data and metadata paths. It abstracts checksum state across CRC32C, CRC64, xxhash, and ChaCha20-Poly1305 MAC modes, with bio variants that walk `bio_vec`s safely under highmem.

Key entry points:
- `bch2_checksum()` and `bch2_checksum_bio()` compute checksums/MACs over memory or bios.
- `bch2_encrypt()` and `__bch2_encrypt_bio()` apply ChaCha20 encryption when the checksum type is encryption-backed.
- `bch2_rechecksum_bio()` recomputes split extent CRCs after extent splitting, verifying the old checksum first.
- `bch2_fs_encryption_init()` decrypts/stores the filesystem ChaCha20 key from the superblock crypt field.

Important details:
- Poly1305 keys are derived with ChaCha20 from the fs key and nonce, with `BCH_NONCE_POLY` separation.
- Bio encryption requires segment lengths aligned to `CHACHA_BLOCK_SIZE` except final-call semantics are avoided by rejecting unaligned segments.
- Mergeable checksums are recomputed over zero pages then XORed with the second checksum, used only for selected non-encryption checksum types.
- Userspace builds include keyutils/passphrase paths; kernel builds request `user` keys from the kernel keyring.

Dependencies and interactions:
- Uses nonce helpers and checksum type policy from `checksum.h`.
- Consumes extent CRC metadata and `extent_nonce()`.
- Writes superblock crypt field text/validation through `bch_sb_field_ops_crypt`.
