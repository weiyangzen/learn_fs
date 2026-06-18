# sources/distributed-fs/ceph-client/fs/ceph/crypto.c

## Purpose

`crypto.c` adapts Linux fscrypt to CephFS. It stores and retrieves encryption context through MDS inode metadata, encodes encrypted filenames into Ceph-safe base64 names with hashing for long names, decodes MDS names for user presentation, prepares encrypted readdir, and encrypts/decrypts page arrays used by OSD I/O.

## Important APIs, Types, and Functions

The fscrypt operation hooks are `ceph_crypt_get_context`, `ceph_crypt_set_context`, `ceph_crypt_empty_dir`, `ceph_get_dummy_policy`, and the `ceph_fscrypt_ops` structure installed by `ceph_fscrypt_set_ops`. `ceph_fscrypt_free_dummy_policy` releases dummy-policy state.

Creation-time context flow is handled by `ceph_fscrypt_prepare_context` and `ceph_fscrypt_as_ctx_to_req`. Filename handling is implemented by `parse_longname`, `ceph_encode_encrypted_dname`, and `ceph_fname_to_usr`. Directory unlock handling is in `ceph_fscrypt_prepare_readdir`.

Data crypt helpers are `ceph_fscrypt_decrypt_block_inplace`, `ceph_fscrypt_encrypt_block_inplace`, `ceph_fscrypt_decrypt_pages`, `ceph_fscrypt_decrypt_extents`, and `ceph_fscrypt_encrypt_pages`.

## Control Flow

When fscrypt asks for an inode context, `ceph_crypt_get_context` validates `ci->fscrypt_auth`, checks the Ceph fscrypt auth version, verifies the output length, and copies the fscrypt blob. Setting a context builds a `ceph_fscrypt_auth` wrapper and sends it through `__ceph_setattr`; on success it marks the inode encrypted.

For a new inode, `ceph_fscrypt_prepare_context` calls `fscrypt_prepare_new_inode`. If encryption is required, it allocates `as->fscrypt_auth`, asks fscrypt for the new context blob, fills the Ceph auth wrapper, mirrors it into `ci->fscrypt_auth`, sets `ci->fscrypt_auth_len`, and marks the inode encrypted. `ceph_fscrypt_as_ctx_to_req` transfers that auth object into the MDS request by swapping pointers.

Filename encryption starts in `ceph_encode_encrypted_dname`. Snapshot names under the snapdir that begin with `_` are parsed by `parse_longname`, which extracts the original snapshot name and target inode number from `_<name>_<ino>`, finding or instantiating that inode so the correct directory key is used. If the directory key is available, fscrypt encrypts the cleartext name, long ciphertext tails are SHA-256 hashed after `CEPH_NOHASH_NAME_MAX`, and the result is base64 encoded with the IMAP alphabet. Snapshot longnames append the inode number again after encryption.

`ceph_fname_to_usr` performs the reverse presentation path for names received from the MDS. Non-encrypted directories pass through unchanged. Encrypted directories first call `ceph_fscrypt_prepare_readdir`; if no key is available, Ceph returns the raw MDS name rather than synthesizing a generic fscrypt nokey name. With a key, it uses either supplied ciphertext or base64-decodes the MDS name, calls `fscrypt_fname_disk_to_usr`, and reconstructs long snapshot names if needed.

For data I/O, block helpers wrap fscrypt in-place encrypt/decrypt with Ceph debug logging. `ceph_fscrypt_decrypt_pages` and `ceph_fscrypt_encrypt_pages` compute 4 KiB crypto-block counts from the file offset and length rounded down to complete blocks, then process each block at the right page index and page offset. `ceph_fscrypt_decrypt_extents` walks sparse OSD extents, validates encrypted extent offset/length alignment, maps object offsets back into the page array, and decrypts only non-hole extents.

## State and Persistence Behavior

Encryption context is stored in `ci->fscrypt_auth` and persisted to the MDS as `struct ceph_fscrypt_auth`. Encrypted cap messages also carry fscrypt auth and real encrypted-file size through `caps.c`. Filenames are persisted to the MDS as base64-encoded ciphertext, with long-name tail hashing and alternate-name support expected for full ciphertext preservation. Data sent to OSDs is encrypted in page/bounce buffers; decrypted data is placed back into page-cache pages for the VFS.

## Dependencies and Integration Points

The file depends on Linux fscrypt, base64, SHA-256, xattrs, Ceph setattr/MDS request code, Ceph inode lookup, and the striper for object mapping in sparse extent decryption. `addr.c` calls the data helpers for encrypted OSD reads/writes, and `caps.c` includes fscrypt auth and real file size in cap messages. Directory and dentry code uses filename helpers for lookup/readdir/release encoding.

## Risks and Edge Cases

Encrypted I/O must only process complete fscrypt blocks; partial tail handling is deliberately left to callers to zero or ignore. Sparse extents with unaligned encrypted offsets or lengths are rejected with `-EIO`. Long filename hashing must stay consistent with `crypto.h` limits or MDS-visible names can exceed `NAME_MAX`. Snapshot longname parsing is sensitive to underscore placement and inode lookup failures. In `ceph_fscrypt_prepare_context`, allocation of `ci->fscrypt_auth` after creating `as->fscrypt_auth` can fail and must be handled by caller cleanup.

## Test Signals

Test encrypted creates, context get/set, dummy encryption policy, readdir before and after key addition, long encrypted filenames, snapshot names in snapdir, lookup/release paths that re-encode names, sparse encrypted reads with holes, unaligned extent rejection, reads/writes across page and object boundaries, and no-key presentation. Signals include correct `S_ENCRYPTED` state, stable base64 names within Ceph limits, successful directory invalidation when a key becomes available, and clean fscrypt bounce-page handling in writeback.
