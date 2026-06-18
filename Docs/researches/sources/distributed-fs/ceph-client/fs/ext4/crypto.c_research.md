# sources/distributed-fs/ceph-client/fs/ext4/crypto.c

## Purpose

`fs/ext4/crypto.c` adapts ext4 to the Linux fscrypt framework. It prepares encrypted and casefolded filenames, manages fscrypt filename buffers, exposes the legacy encryption password salt ioctl, stores and retrieves inode encryption contexts through ext4 xattrs, enforces ext4-specific encryption constraints, and publishes `ext4_cryptops`.

## Important APIs, types, and functions

- `ext4_fname_setup_filename()` wraps `fscrypt_setup_filename()`, copies the result into `struct ext4_filename`, and prepares case-insensitive lookup data with `ext4_fname_setup_ci_filename()`.
- `ext4_fname_prepare_lookup()` wraps `fscrypt_prepare_lookup()` for dentry lookup and also prepares casefold state.
- `ext4_fname_free_filename()` frees fscrypt and ext4 casefold filename buffers.
- `ext4_ioctl_get_encryption_pwsalt()` returns `s_encrypt_pw_salt`, generating and journaling a UUID salt in the superblock if it is still zero and encryption is supported.
- `ext4_get_context()` reads `EXT4_XATTR_NAME_ENCRYPTION_CONTEXT` from the encryption xattr namespace.
- `ext4_set_context()` writes the encryption context either using an existing new-inode journal handle or by starting its own `EXT4_HT_MISC` transaction, with quota initialization, credit calculation, ENOSPC retry, inline-data conversion, DAX/root-directory rejection, inode flag updates, and inode dirtying.
- `ext4_get_dummy_policy()` returns the mounted dummy encryption policy.
- `ext4_has_stable_inodes()` reports the stable-inodes feature to fscrypt.
- `ext4_cryptops` supplies fscrypt callbacks and capability flags, including bounce pages, 32-bit inode support, subblock data units, legacy key prefix, context get/set, empty-dir check, and stable inode query.

## Control flow

Filename setup starts in VFS namei paths before lookup/create. fscrypt prepares disk/user names and optional crypto buffers, then ext4 augments the structure with casefold hashes/buffers; cleanup must release both. The salt ioctl first checks encryption feature support, obtains write access when initialization is needed, starts a journal transaction, gets write access to the superblock buffer, generates the UUID, updates the superblock checksum, dirties metadata, stops the journal, drops write access, and copies 16 bytes to user space.

Encryption context set rejects the root inode, nonempty DAX states, and DAX-flagged inodes, converts inline data away, then stores the xattr. For new inodes it uses the caller's handle and `XATTR_CREATE`; for existing inodes it starts a transaction and retries ENOSPC if a journal commit might free space.

## State and persistence behavior

Persistent state includes the superblock encryption password salt, inode encryption context xattr, inode `EXT4_INODE_ENCRYPT` flag, and possibly cleared inline-data eligibility. In-memory state includes `ext4_filename` buffers, fscrypt crypto buffers, casefold lookup data, per-inode crypt info offset, and dummy policy. Updating encryption context can also alter VFS inode flags such as `S_ENCRYPTED` and DAX-related flags.

## Dependencies and integration points

The file depends on fscrypt, ext4 xattrs, ext4 journaling, superblock checksums, quota initialization, inline-data conversion, DAX checks, namei/casefold helpers, random UUID generation, and user-copy APIs. Directory iteration and lookup code consume the prepared filename structures and fscrypt hashes.

## Risks and edge cases

Root directory encryption is prohibited because e2fsck expects unencrypted `lost+found`. DAX and encryption are incompatible in the checked states. Inline data must be converted before context persistence. Salt generation must be journaled and checksum-updated exactly once even under races. Existing-inode context writes need sufficient xattr credits and correct ENOSPC retry. Cleanup must avoid leaking fscrypt or casefold buffers after partial setup failure.

## Test signals

Test encrypted directory/file creation, lookup, casefolded encrypted names, filename buffer cleanup on failures, password salt ioctl before and after salt generation, concurrent salt requests, root-directory encryption rejection, DAX rejection, inline-data conversion, context inheritance for new inodes, existing-inode policy set with ENOSPC retry, and fscrypt empty-dir checks.
