# sources/distributed-fs/lustre-release/lustre/llite/crypto.c

## Purpose
`crypto.c` is the llite adapter for Lustre encryption on top of fscrypt/llcrypt. It handles encryption contexts, encrypted open behavior, encrypted filename setup and display, keyless long-name digests, symlink decoding, nokey dentry revalidation, and feature flags.

## Important APIs, Types, and Functions
Important functions include `ll_get_context()`, `ll_set_context()`, `ll_set_encflags()`, `ll_file_open_encrypt()`, `ll_prepare_lookup()`, `ll_setup_filename()`, `ll_digest_long_name()`, `ll_fname_disk_to_usr()`, `ll_get_symlink()`, and `llcrypt_d_revalidate()`. `lustre_cryptops` registers Lustre callbacks with llcrypt.

## Control Flow
Context get/set bypass normal VFS xattr handlers and use Lustre metadata xattr paths. Create-time context can be stored in `md_op_data`; existing inode policy set sends `md_setxattr()` and then installs encryption flags. Lookup setup detects keyless encrypted names, handles volatile names, delegates to llcrypt setup, marks nokey dentries, converts missing-key cases, and performs critical-character encoding. Disk-to-user conversion decodes critical characters and, for keyless long names, presents an encoded `ll_digest_filename` that carries FID/excerpt data Lustre can later use for lookup.

## State and Persistence Behavior
Encryption context persists as an MDS xattr. Client state includes inode encryption flags, xattr cache entries, superblock encryption/name-encryption flags, dentry nokey flags, and temporary llcrypt filename buffers.

## Dependencies and Integration Points
The file integrates with llcrypt/fscrypt APIs, Lustre metadata/xattr RPCs, llite flags, FIDs, critical encode/decode helpers, and VFS dentry revalidation. It has compatibility branches and stubs for non-crypto builds.

## Risks and Edge Cases
Keyless long-name behavior depends on digest prefixes and old-client compatibility flags. Buffer ownership in filename conversion is subtle. Critical encoding regressions can make encrypted names unreachable. RCU dentry validation must return `-ECHILD`. Non-crypto fallback behavior still needs consistency.

## Test Signals
Test encrypted lookup/create with and without keys, long names, old/new digest prefix modes, volatile names, `/.fscrypt`, symlink readlink without keys, `O_CIPHERTEXT` open rules, key insertion dentry invalidation, and non-crypto builds.
