# sources/distributed-fs/ceph-client/fs/ubifs/crypto.c

## Purpose
`crypto.c` connects UBIFS to fscrypt. It stores encryption contexts as UBIFS xattrs, enforces fscrypt directory-empty checks, and encrypts/decrypts UBIFS data-node payloads in place after compression and before decompression.

## Important APIs, Types, and Functions
- `ubifs_crypt_get_context()` and `ubifs_crypt_set_context()` read/write `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT` through UBIFS xattr helpers.
- `ubifs_crypt_empty_dir()` delegates to `ubifs_check_dir_empty()` for fscrypt policy changes.
- `ubifs_encrypt()` records the pre-encryption compressed length in `dn->compr_size`, pads to `UBIFS_CIPHER_BLOCK_SIZE`, and calls `fscrypt_encrypt_block_inplace()`.
- `ubifs_decrypt()` validates `dn->compr_size`, decrypts a full padded extent using `fscrypt_decrypt_block_inplace()`, then returns the original compressed length.
- `ubifs_crypt_operations` is the fscrypt operations table exported to the superblock/inode setup code.

## Control Flow
On encryption, the caller supplies a data node whose `data` field already contains compressed or raw data. The function rounds the data length up to the UBIFS cipher block size, zero-pads any added bytes, stores the unpadded length in little-endian `compr_size`, and asks fscrypt to encrypt the page containing `dn->data` at the logical block number. The returned output length becomes the padded encrypted length that should be journaled.

On decryption, UBIFS reads `compr_size` first, rejects zero, over-block, or larger-than-buffer values, decrypts the padded data in place, and changes `*out_len` back to the original compressed length so the decompressor sees exactly the bytes it expects.

## State and Persistence Behavior
Encryption context is persistent metadata stored as an xattr. `compr_size` is persistent per data node and is critical because encryption padding changes the stored payload length. The code mutates the data node in memory in place; persistence is handled later by journal writes and earlier by TNC reads.

## Dependencies and Integration Points
This file depends on UBIFS xattr operations, directory emptiness checks in `dir.c`, and fscrypt block helpers. It integrates with inode allocation and lookup through fscrypt operations, with `dir.c` for context setup and inherited encryption policy, and with `file.c` read paths that decrypt before decompression.

## Risks and Edge Cases
- `ubifs_decrypt()` trusts the caller's padded `*out_len` to match the encrypted data payload size; it validates only that `compr_size` is sane relative to it.
- The encryption context is set without inode locking for new inodes because the inode is not visible yet; callers must preserve that creation ordering.
- Incorrect `block` numbers would break fscrypt IV derivation and data recovery.
- Padding bytes are zeroed before encryption, which avoids leaking stale memory but requires `*out_len` to reflect allocated data-node capacity.

## Test Signals
Exercise encrypted regular-file writes and reads across partial-block compressed sizes, invalid `compr_size` values, policy setting on non-empty directories, xattr persistence of encryption contexts, and power-cut scenarios around encrypted inode creation before dentry linking.
