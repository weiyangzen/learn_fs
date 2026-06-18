# sources/distributed-fs/ceph-client/fs/ext4/symlink.c

## Purpose
`symlink.c` provides ext4 symlink inode operations. Most symlink behavior is delegated to generic VFS helpers; this file handles ext4-specific fast symlinks, leftover inline-data symlinks, encrypted symlinks, and block-backed symlink reads.

## Important APIs, Types, And Functions
The exported operation tables are `ext4_encrypted_symlink_inode_operations`, `ext4_symlink_inode_operations`, and `ext4_fast_symlink_inode_operations`. The main callbacks are `ext4_encrypted_get_link()`, `ext4_encrypted_symlink_getattr()`, `ext4_get_link()`, and `ext4_free_link()`.

`ext4_encrypted_get_link()` chooses the ciphertext source from either `EXT4_I(inode)->i_data` for fast symlinks or block zero via `ext4_bread()`, then delegates plaintext decoding and delayed cleanup to `fscrypt_get_symlink()`. `ext4_get_link()` handles non-encrypted regular symlinks, including old inline-data symlink leftovers via `ext4_read_inline_link()`, RCU-walk safe cached lookup through `ext4_getblk(... EXT4_GET_BLOCKS_CACHED_NOWAIT)`, and normal blocking reads through `ext4_bread()`.

## Control Flow
For encrypted symlinks, VFS `.get_link` enters `ext4_encrypted_get_link()`. A missing dentry indicates RCU-walk context and returns `-ECHILD` because fscrypt/block IO may need blocking work. Fast symlinks use in-inode data; slow symlinks read logical block zero. The resulting bytes are passed to fscrypt, then any buffer head is released.

For normal symlinks, inline-data inodes are read through ext4 inline-data support and freed with `kfree_link`. Non-inline RCU-walk attempts only a cached, uptodate buffer and otherwise returns `-ECHILD`. Blocking lookup reads block zero, validates that a block exists, installs a delayed `brelse()` callback, NUL-terminates within `inode->i_size` and block-size bounds using `nd_terminate_link()`, and returns the buffer data.

## State And Persistence Behavior
Fast symlink payloads are stored in the ext4 inode's `i_data` array. Block-backed symlinks store the target in file block zero. Inline-data symlink support here is read-only compatibility for old inodes; the comment states creating new inline symlinks is not supported. Encrypted symlink bytes persist encrypted and are interpreted through fscrypt on each lookup.

## Dependencies And Integration Points
The file integrates VFS `inode_operations`, path walk delayed calls, buffer-head lifetime management, ext4 block mapping/read helpers, ext4 inline-data helpers, xattr listing, generic `ext4_setattr()`/`ext4_getattr()`, and fscrypt symlink decoding/stat adjustment.

## Risks And Edge Cases
The important correctness boundaries are RCU-walk behavior, buffer lifetime, corrupt symlink blocks, and correct target termination. Missing dentry returns `-ECHILD` when blocking or allocation might be required. `ext4_bread()` errors propagate with `ERR_CAST`; absent block zero is reported as filesystem corruption. Encrypted symlink size and validation are delegated to fscrypt, while non-encrypted block-backed symlinks rely on `nd_terminate_link()` to avoid overrun.

## Test Signals
Tests should cover fast, slow block-backed, encrypted, and old inline-data symlinks; RCU path walk fallback; corrupt symlink inode with missing block zero; xattr listing on symlink inodes; symlink getattr size adjustment under encryption; and symlink targets at block-size and `i_size` boundaries. fscrypt test vectors are important because encrypted fast symlinks source data from the inode body rather than a buffer head.
