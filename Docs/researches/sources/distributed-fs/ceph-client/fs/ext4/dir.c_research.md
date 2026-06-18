# sources/distributed-fs/ceph-client/fs/ext4/dir.c

## Purpose

`fs/ext4/dir.c` implements ext4 directory file operations, including linear directory iteration, htree-indexed directory iteration, directory entry validation, encrypted/casefolded name presentation, directory llseek semantics, per-open directory private state, and directory release cleanup.

## Important APIs, types, and functions

- `is_dx_dir()` detects htree-indexed or potentially indexed directories using feature flags, inode index flag, one-block size, or inline data.
- `is_fake_dir_entry()` treats dot entries, dot-dot entries, and checksum tail entries specially for validation sizing.
- `__ext4_check_dir_entry()` validates record length, alignment, name length fit, block overrun, checksum-tail spacing, inode bounds, and invalid final `.` entries, reporting through file or inode error helpers.
- `ext4_readdir()` is the linear/dispatcher iterate path. It prepares fscrypt, tries htree iteration, falls back on bad dx directories when safe, handles inline-data directories, maps directory blocks, performs readahead, verifies dirblock checksums, rescans after inode version changes, decrypts names, and emits entries.
- `hash2pos()`, `pos2maj_hash()`, `pos2min_hash()`, and `ext4_get_htree_eof()` translate htree hashes to `f_pos` for 32-bit and 64-bit directory APIs.
- `ext4_dir_llseek()` chooses htree hash-space seeking or normal ext4 seeking and invalidates the directory private cookie.
- `struct fname` stores htree entries in an rb-tree keyed by major/minor hash with a linked list for exact hash collisions.
- `ext4_htree_store_dirent()` allocates and inserts decrypted or raw names into the rb-tree.
- `call_filldir()` emits one hash bucket/collision chain and stores continuation state if the caller buffer fills.
- `ext4_dx_readdir()` fills and drains htree sorted names using `ext4_htree_fill_tree()`, inode version cookies, next-hash continuation, and EOF sentinels.
- `ext4_check_all_de()` validates all directory entries in a supplied buffer.
- `ext4_dir_open()` allocates `struct dir_private_info`; `ext4_release_dir()` frees it.
- `ext4_dir_operations` exports open, llseek, generic read, iterate_shared, ioctl, fsync, release, lease, and compat ioctl callbacks.

## Control flow

Every directory open gets private iteration state. Readdir first calls `fscrypt_prepare_readdir()`. If the directory is indexed, it calls `ext4_dx_readdir()`; only `ERR_BAD_DX_DIR` falls back to linear scanning, and the index flag may be cleared when metadata checksums are not enabled. Inline-data directories are handled before block iteration. Linear scanning maps logical directory blocks, skips holes, reads buffers, verifies checksums once per buffer, and validates each dirent before `dir_emit()`. Encrypted names are converted with `fscrypt_fname_disk_to_usr()`, using stored hash/minor hash for casefolded encrypted directories.

Htree iteration treats `ctx->pos` as a hash position. It rebuilds the rb-tree when position changes or inode version changes, fills it from `ext4_htree_fill_tree()`, emits names in hash order, tracks leftover collision-chain entries in `extra_fname`, advances to `next_hash`, and sets an htree EOF sentinel when exhausted.

## State and persistence behavior

This file mostly reads persistent directory blocks. It does not create/delete dirents, but it can clear the in-memory inode index flag after a bad dx fallback when metadata checksums are disabled, without marking the inode dirty. Persistent inputs include ext4 dirent records, file types, inode numbers, checksum tail entries, htree hashes, inline data, encryption/casefold metadata, and inode version changes maintained by writers. Per-open transient state lives in `dir_private_info`, rb-tree `fname` nodes, `ctx->pos`, hash cursors, and inode version cookies.

## Dependencies and integration points

The file depends on ext4 block mapping/read helpers, dirblock checksum verification, htree fill logic from namei/hash code, inline-data directory reads, fscrypt, Unicode/casefold support, VFS `dir_context`, `dir_emit()`, file readahead, inode versioning, buffer-head IO, and ext4 ioctl/fsync implementations.

## Risks and edge cases

Directory validation protects against corrupt disk records causing loops or overreads. Htree `f_pos` hash semantics differ from byte offsets and must stay compatible with 32-bit APIs and NFS-like consumers using hash modes. Encrypted and casefolded directories require correct hash propagation to fscrypt name conversion. If a directory changes during iteration, the code rescans to a valid record boundary using inode versioning. Bad checksums skip the block rather than emitting untrusted names. Large hash-collision chains can consume memory through `struct fname` allocations.

## Test signals

Test linear and indexed readdir, inline directories, encrypted directories, casefolded encrypted directories, 32-bit and 64-bit htree seek positions, telldir/seekdir stability, concurrent create/unlink/rename during readdir, corrupt rec_len/name_len/inode/checksum-tail cases, bad dx fallback with and without metadata checksums, directory block checksum failures, hash collisions, and file buffer-full continuation through `extra_fname`.
