# sources/distributed-fs/ceph-client/fs/crypto/inline_crypt.c

## Purpose
`inline_crypt.c` implements fscrypt support for blk-crypto inline encryption, where encryption/decryption is handled by the block layer or hardware as part of bio processing rather than by filesystem-layer Crypto API transforms.

## Important APIs and Functions
- `fscrypt_select_encryption_impl()` decides whether an inode can use inline crypto based on file type, mode support, mount flag, IV method constraints, data-unit size, DUN byte width, and block-device support.
- `fscrypt_prepare_inline_crypt_key()` initializes a `blk_crypto_key`, starts using it on all filesystem block devices, and publishes it through `prep_key->blk_key`.
- `fscrypt_destroy_inline_crypt_key()` evicts a blk-crypto key from all devices and frees it.
- `fscrypt_derive_sw_secret()` asks inline-crypto hardware to derive a software secret from a hardware-wrapped key.
- `__fscrypt_inode_uses_inline_crypto()`, `fscrypt_set_bio_crypt_ctx()`, `fscrypt_mergeable_bio()`, `fscrypt_dio_supported()`, and `fscrypt_limit_io_blocks()` are the filesystem-facing I/O helpers.

## Control Flow
Key setup calls `fscrypt_select_encryption_impl()` before preparing the file key. If accepted, later preparation calls `fscrypt_prepare_inline_crypt_key()` instead of creating a skcipher transform. I/O submission calls `fscrypt_set_bio_crypt_ctx()` to generate a blk-crypto DUN from the fscrypt IV and attach the key to the bio. Filesystems call `fscrypt_mergeable_bio()` and `fscrypt_limit_io_blocks()` to avoid mixing keys or discontiguous DUN ranges.

## State and Persistence
Inline-crypto selection is cached in `ci->ci_inlinecrypt`. Prepared blk-crypto keys live in `fscrypt_prepared_key.blk_key`, either per-file or in per-mode arrays embedded in a master key. No new on-disk state is created here; DUNs are derived from policy flags, inode state, nonce, hashed inode number, and logical positions.

## Dependencies and Integration
The file depends on blk-crypto, block devices, superblock `s_cop->get_devices`, filesystem mount flag `SB_INLINECRYPT`, fscrypt IV generation, and fscrypt policy flags. It integrates with `keysetup.c` for key preparation and with filesystem bio/direct-I/O submission paths.

## Risks and Edge Cases
- Inline crypto is only selected for regular-file contents, never filename encryption.
- IV_INO_LBLK_32 with blocksize smaller than page size is excluded because some filesystems only check mergeability once per page.
- Hardware-wrapped contents keys require inline crypto; fallback to filesystem-layer crypto would expose an unusable wrapped key.
- Multi-device filesystems must support the selected blk-crypto configuration on every device returned by `get_devices()`.
- DIO support returns false on missing keys and requires inline crypto for encrypted files.
- `fscrypt_limit_io_blocks()` prevents 32-bit DUN wrap inside a bio for IV_INO_LBLK_32.

## Test Signals
Exercise mount with and without `inlinecrypt`, unsupported blk-crypto modes, multi-device rejection, IV_INO_LBLK_32 block-size restrictions, bio merge refusal across different keys/DUN discontinuities, hardware-wrapped-key support and rejection, DIO eligibility, and DUN wrap limiting near `U32_MAX`.
