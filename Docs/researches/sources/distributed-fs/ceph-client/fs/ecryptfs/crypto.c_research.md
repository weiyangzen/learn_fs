# sources/distributed-fs/ceph-client/fs/ecryptfs/crypto.c

## Purpose

`crypto.c` implements eCryptfs' core file-content and filename cryptography. It initializes per-inode `struct ecryptfs_crypt_stat`, encrypts and decrypts page extents, reads and writes the persistent eCryptfs metadata header or `user.ecryptfs` xattr, maps cipher codes to Linux Crypto API names, caches key transform objects, and encodes encrypted filenames into lower-filesystem-safe names. It is the main bridge between VFS-facing code in `file.c`/`inode.c`, key packet handling in `keystore.c`, and lower-file I/O helpers in the rest of the eCryptfs stack.

## Important APIs, types, and functions

The file exports `ecryptfs_init_crypt_stat()`, `ecryptfs_destroy_crypt_stat()`, `ecryptfs_destroy_mount_crypt_stat()`, `ecryptfs_new_file_context()`, `ecryptfs_read_metadata()`, `ecryptfs_write_metadata()`, `ecryptfs_encrypt_page()`, `ecryptfs_decrypt_page()`, `ecryptfs_init_crypt_ctx()`, `ecryptfs_compute_root_iv()`, `ecryptfs_get_tfm_and_mutex_for_cipher_name()`, `ecryptfs_encrypt_and_encode_filename()`, `ecryptfs_decode_and_decrypt_filename()`, and `ecryptfs_set_f_namelen()`. Internal helpers include `crypt_scatterlist()`, `crypt_extent()`, `ecryptfs_read_headers_virt()`, `ecryptfs_write_headers_virt()`, marker/flag conversion helpers, packet length and cipher-code mapping helpers, and filename base64-like encoder/decoder tables.

`struct ecryptfs_flag_map_elem` maps on-disk header flags to in-memory `crypt_stat->flags`. `struct ecryptfs_cipher_code_str_map_elem` maps OpenPGP/RFC2440 cipher codes to Linux cipher names, with special AES key-size handling. Module-global state includes `ecryptfs_key_tfm_cache`, `key_tfm_list`, and `key_tfm_list_mutex`, which cache persistent key encryption TFMs by cipher name.

## Control flow

New encrypted files enter through `ecryptfs_new_file_context()`: mount flags and signatures are copied to the inode, defaults are set, a random FEK is generated, a root IV is computed as MD5(FEK), and a CBC skcipher transform is allocated for the file cipher. `ecryptfs_write_metadata()` allocates a zeroed metadata region, writes the marker, flags, header extent metadata, and key packet set, then persists it either at lower file offset 0 or in `user.ecryptfs` when xattr metadata is enabled.

Existing files enter through `ecryptfs_read_metadata()`: the first lower extent is read, `ecryptfs_read_headers_virt()` validates the marker, initializes upper `i_size`, parses flags/header sizing, then delegates key packet parsing to `ecryptfs_parse_packet_set()`. If the header path fails, the code retries the xattr region and only accepts xattr metadata when the mount enabled xattr support.

Page I/O uses `ecryptfs_encrypt_page()` and `ecryptfs_decrypt_page()`. They translate an upper folio index to a lower byte offset by adding `metadata_size` unless metadata is stored in xattr. Each page is split into `crypt_stat->extent_size` chunks; `crypt_extent()` derives an IV from the root IV plus extent number and runs CBC encrypt/decrypt through `crypt_scatterlist()`.

Filename encryption flows through `ecryptfs_encrypt_and_encode_filename()`. With global filename encryption enabled, it creates a tag 70 packet via `ecryptfs_write_tag_70_packet()`, then encodes the binary packet with portable filename characters and the `ECRYPTFS_FNEK_ENCRYPTED.` prefix. Decode reverses that path, rejecting non-prefixed names except dot entries and encrypted-view/passthrough cases.

## State and persistence

Persistent file state is the unencrypted upper file size, eCryptfs marker, file flags, header extent size/count, and key packet set stored in the lower file header or `user.ecryptfs`. Runtime state lives in each inode's `crypt_stat`: cipher name, FEK, key size, root IV, metadata size, extent masks, flags, key signatures, and crypto transform. Module-wide cached key TFMs persist until `ecryptfs_destroy_crypto()` at unload.

The persistent lower layout changes with `ECRYPTFS_METADATA_IN_XATTR`: when unset, encrypted data starts after the metadata header; when set, lower data starts at offset 0 and metadata is externalized to the xattr. `ECRYPTFS_VIEW_AS_ENCRYPTED` changes size reporting so users see the lower encrypted payload rather than decrypted logical size.

## Dependencies and integration points

This file depends on Linux Crypto API `skcipher`, MD5 helpers, key/xattr APIs, scatterlists, folios/pages, unaligned big-endian accessors, and lower I/O helpers declared in `ecryptfs_kernel.h`. It calls into `keystore.c` for key packet generation/parsing and tag 70 filename packets. It is called by `file.c` during open metadata initialization, by `inode.c` during lookup, create, truncate, symlink, and name translation, and by mmap/read-write paths for encrypted page traffic.

## Risks

The file contains several security-sensitive legacy choices: MD5-derived IVs, CBC mode without modern authenticated encryption, and verbose debug paths that can dump keys when `ecryptfs_verbosity > 0`. Metadata parsing must reject malformed header sizes and packet boundaries; mistakes can mis-size lower offsets or treat plaintext as encrypted. Filename decoding silently masks some `-EINVAL` cases in readdir via callers, so mixed plaintext/encrypted lower directories need careful behavior tests. Crypto transform caching is protected by mutexes, but every caller must respect `key_tfm_list_mutex` and per-TFM mutex ownership.

## Test signals

Useful tests include mounting with header metadata and xattr metadata, creating files and validating lower offsets/sizes, reading files across page and extent boundaries, truncate growth/shrink with metadata size rewrites, encrypted-view size reporting, filename encryption round trips including dot entries and malformed prefixes, unsupported cipher/key-size rejection, missing key behavior, and module unload cleanup of cached TFMs.
