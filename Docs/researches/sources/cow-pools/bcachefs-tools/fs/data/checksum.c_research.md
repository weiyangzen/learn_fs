# File Research: sources/cow-pools/bcachefs-tools/fs/data/checksum.c

Implements checksum, authenticated checksum, encryption, and filesystem encryption-key setup for bcachefs data paths.

Key responsibilities:
- Maintains `bch2_checksum_state`, abstracting mergeable CRC-style checksums and stateful `xxhash`.
- Implements `bch2_checksum()` for `none`, `crc32c`, `crc64`, `xxhash`, and Chacha20-Poly1305 MAC variants.
- Implements `bch2_checksum_bio()` and `__bch2_checksum_bio()` over bio segments, including highmem-safe mapping.
- Implements `bch2_encrypt()` and `__bch2_encrypt_bio()` using Chacha20, with explicit checks that the fs encryption key is loaded.
- Implements `bch2_checksum_merge()` for mergeable checksum types by advancing the left checksum over zero bytes and XORing with the right checksum.
- Implements `bch2_rechecksum_bio()` for splitting/recomputing extent CRC metadata while verifying against the old checksum.
- Defines superblock crypt-field validation/text output via `bch_sb_field_ops_crypt`.
- Handles kernel/user key lookup, passphrase fallback in userspace, key revocation in userspace, and superblock-key decryption.
- Initializes and clears `c->chacha20_key`.

Important interactions:
- Uses nonce helpers from `checksum.h`, extent CRC metadata, bio iteration, kernel keyring or userspace keyutils, and superblock crypt fields.
- Encryption checksum types are both encryption and authentication-sensitive; missing keys become filesystem inconsistency/error paths.
- `bch2_rechecksum_bio()` depends on consistent encrypted-vs-unencrypted checksum type transitions.

Notable concerns:
- `bch2_crc_cmp()` is used through the header as non-equality; comments note constant-time comparison is not guaranteed.
- Bio encryption requires every non-final segment length to be Chacha block aligned; misalignment returns `-EIO`.
- Disabled `#if 0` code documents planned runtime encryption enable/disable paths but is not active.
