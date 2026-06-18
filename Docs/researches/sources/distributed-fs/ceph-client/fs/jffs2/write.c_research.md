# sources/distributed-fs/ceph-client/fs/jffs2/write.c

## Purpose

`write.c` constructs and persists JFFS2 raw inode and dirent nodes for file data, metadata, creation, unlink, and hard-link operations. It handles compression, CRC generation, inode and directory versioning, node-ref linking, retry after flash write failure, and integration with security/ACL initialization.

## Important APIs, Types, And Functions

Exported functions include `jffs2_do_new_inode()`, `jffs2_write_dnode()`, `jffs2_write_dirent()`, `jffs2_write_inode_range()`, `jffs2_do_create()`, `jffs2_do_unlink()`, and `jffs2_do_link()`.

The main raw on-medium structures are `struct jffs2_raw_inode` and `struct jffs2_raw_dirent`; their in-core counterparts include `struct jffs2_full_dnode`, `struct jffs2_full_dirent`, inode caches, and fragment trees.

## Control Flow

`jffs2_do_new_inode()` allocates and initializes an inode cache, assigns an inode number, fills immutable raw inode header fields, sets mode and version 1, and leaves the caller to complete metadata fields.

`jffs2_write_dnode()` writes one raw inode node plus optional data. It validates header CRC under debug, allocates a full dnode, chooses current `write_ofs(c)`, updates stale versions after retry if necessary, writes through `jffs2_flash_writev()`, and on failure marks any partially written space obsolete/dirty, optionally reserves new space and retries. On success it chooses `REF_PRISTINE` for whole-page/end-of-file style nodes and `REF_NORMAL` otherwise, links a raw ref through `jffs2_add_physical_node_ref()`, and fills the full dnode.

`jffs2_write_inode_range()` loops over the caller's data range. Each iteration reserves enough space, locks the inode, limits writes to page boundaries and allocation size, compresses data, fills raw inode metadata/CRCs/version/isize/offset/compression fields, calls `jffs2_write_dnode()` with no internal retry, inserts the returned full dnode into the inode fragment tree, obsoletes old metadata, completes the reservation, and advances the logical range.

`jffs2_write_dirent()` mirrors dnode writing for directory entries, including embedded-zero name detection, version retry, name hash setup, flash write, and raw-ref linking. `jffs2_do_create()` writes the new inode metadata node, initializes security labels and ACLs, then writes the parent directory entry. `jffs2_do_unlink()` either writes a deletion dirent for media that cannot mark obsolete or directly marks the old dirent obsolete on mark-capable media. `jffs2_do_link()` writes a positive dirent pointing to an existing inode.

## State And Persistence Behavior

This file is responsible for constructing persisted node bytes and CRCs. It increments inode or directory `highest_version` for every logical mutation, updates `isize` for data writes, and uses dirent `ino=0` as a persistent deletion record when needed. Successful writes create raw-node refs that become part of eraseblock and inode accounting. Failed partial writes are recorded as obsolete space so later scans do not reuse the corrupted span incorrectly.

Create is two-phase: the inode metadata node is persisted before security/ACL initialization and parent dirent creation. If later steps fail, callers must handle cleanup through normal unlink/eviction semantics.

## Dependencies And Integration Points

Dependencies include nodemgmt reservation/completion and obsolescence, flash IO/write-buffer wrappers, compression, CRC32, fragment-tree insertion, security and ACL initialization, dirent list insertion, and Linux inode mode helpers. It is used by higher-level VFS file and directory operations.

## Risks And Edge Cases

Write retry logic must avoid reusing stale version numbers after another write advanced `highest_version`; both dnode and dirent retry paths update node CRCs after version changes. Partial writes deliberately mark the intended padded node span obsolete rather than the short retlen to avoid future scans seeing a truncated-but-header-valid node. The create sequence can leave an inode node without a dirent if security/ACL/dirent steps fail. Direct obsolete marking during unlink requires holding `alloc_sem` even though no new space is reserved.

## Test Signals

Tests should cover compressed and uncompressed writes, page-boundary splitting, write failures with retry and no-retry paths, partial retlen handling, stale-version retries, create failures after inode node write, security/ACL initialization failures, unlink on mark-capable and no-mark media, hard links, directory entry replacement, embedded-NUL name rejection, and low-space behavior for normal versus deletion allocations.
