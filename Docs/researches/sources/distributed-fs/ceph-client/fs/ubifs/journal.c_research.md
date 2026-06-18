# sources/distributed-fs/ceph-client/fs/ubifs/journal.c

## Purpose

`journal.c` implements UBIFS journal mutation operations. UBIFS journals updates by writing grouped nodes into multi-headed bud LEBs and then updating the in-memory TNC to point at the newest nodes. The log records bud references, while this file writes inode, data, dent, xent, truncate, rename, orphan-related, and xattr updates into journal heads with ordering that is atomic with respect to unclean reboot recovery.

## Important APIs, Types, And Functions

Public mutation APIs include `ubifs_jnl_update()`, `ubifs_jnl_write_data()`, `ubifs_jnl_write_inode()`, `ubifs_jnl_delete_inode()`, `ubifs_jnl_xrename()`, `ubifs_jnl_rename()`, `ubifs_jnl_truncate()`, `ubifs_jnl_delete_xattr()`, and `ubifs_jnl_change_xattr()`. Reservation helpers are `reserve_space()`, `make_reservation()`, `release_head()`, and `finish_reservation()`. Packing helpers include `pack_inode()`, `get_dent_type()`, `set_dent_cookie()`, and zeroing functions for unused on-flash fields. Authentication grouping is handled by `ubifs_hash_nodes()` and `write_head()`.

The file writes `struct ubifs_ino_node`, `struct ubifs_dent_node`, `struct ubifs_data_node`, and `struct ubifs_trun_node`, uses `union ubifs_key` helpers from `key.h`, and updates TNC entries with node hashes for authenticated or hash-checked lookup paths.

## Control Flow

All journal write operations follow a similar pattern: compute exact aligned write size, allocate a single buffer for the atomic node group, call `make_reservation()` before assigning sequence numbers, pack nodes with group markers, calculate hashes, write the group via `write_head()`, release the journal head mutex, update TNC and dirty/orphan accounting, then call `finish_reservation()` to release `commit_sem`.

`make_reservation()` takes a read lock on `c->commit_sem` and calls `reserve_space()`. If the current head lacks room, `reserve_space()` finds a free-space LEB or runs GC after dropping the write-buffer mutex. `-EAGAIN` triggers commit and retry. After many retries, tasks are serialized through `reserve_space_wq` so concurrent writers stop stealing space from one another. More than 128 commit retries is treated as a budgeting or journal-limit failure.

Directory and xattr updates write dent/xent, child inode, and parent/host inode in one base-head group. Data writes use `DATAHD`, compress and optionally encrypt folio data, append an auth node when authenticated, then add the data key to the TNC. Rename and exchange operations write both new and deletion/whiteout dent nodes plus affected parent and victim inodes. Truncation writes an inode node, a truncation node, and optionally a recompressed/reencrypted final data node, then removes the old data-key range from the TNC.

## State And Persistence Behavior

The journal write is made durable before the in-memory TNC is changed. If the media write succeeds but TNC or accounting updates fail, the filesystem is switched read-only because media and memory state may diverge. Node grouping is used for recovery atomicity: after an unclean reboot, recovery can drop incomplete groups. Synchronous and dirsync inodes force write-buffer synchronization through the `sync` argument to `write_head()`.

Orphan handling is integrated into unlink, rename-over, and delete-inode paths. When the last reference is removed, the inode may be added to the orphan list before the journal group is written and `del_cmtno` records the commit number. `ubifs_jnl_delete_inode()` can skip writing a second deletion inode if no commit occurred between unlink and final iput; otherwise it writes an inode deletion to preserve clean-unmount recovery semantics.

## Dependencies And Integration Points

This file depends on the log layer for adding buds, the GC/lprops allocator for free LEBs, the I/O write-buffer layer, commit orchestration, TNC add/remove/range-remove operations, orphan management, compression, encryption, authentication hashing, fscrypt names, Linux folios, inode locking, and UBIFS budgeting. It is the main integration point between VFS-level filesystem changes and UBIFS's persisted tree representation.

## Risks And Edge Cases

The most sensitive invariants are reservation-before-sequence-number allocation, group ordering, journal-head lock lifetime, and TNC updates after write success. Rename and xattr paths have many optional nodes, aligned offsets, and orphan cleanup branches; an error must delete newly added orphan entries when the group does not complete. Data writes must handle low-memory fallback to `c->write_reserve_buf`, compression expansion, encryption block padding, and authenticated write lengths. Truncation must correctly handle holes, short final blocks, compressed/encrypted recompression, and data-key range deletion.

## Test Signals

Strong signals include fsstress-style create/unlink/rename/xattr/truncate workloads, power-cut recovery around multi-node groups, authenticated and encrypted mounts, low-memory data write fallback, synchronous/dirsync operations, rename with whiteout and cross-directory exchange, orphan cleanup across commits, repeated `-EAGAIN` reservation retries, and debug TNC/lprops checks after journal updates.
