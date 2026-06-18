# sources/distributed-fs/ceph-client/fs/gfs2/xattr.c

## Purpose
`xattr.c` implements GFS2 extended attribute listing, lookup, get, set, remove, allocation, unstuffed data handling, indirect EA block handling, ACL data retrieval, and xattr fork deallocation.

## Important APIs, Types, And Functions
The main VFS handlers are `gfs2_xattr_get` and `gfs2_xattr_set`; exported GFS2 APIs are `__gfs2_xattr_set`, `gfs2_listxattr`, `gfs2_ea_dealloc`, and `gfs2_xattr_acl_get`. Internal request and location state comes from `struct gfs2_ea_request` and `struct gfs2_ea_location` in `xattr.h`.

Key helpers include `ea_calc_size`, `ea_check_size`, `ea_foreach`, `gfs2_ea_find`, `ea_dealloc_unstuffed`, `ea_list_i`, `gfs2_iter_unstuffed`, `ea_alloc_blk`, `ea_write`, `ea_alloc_skeleton`, `ea_set_simple`, `ea_set_block`, `ea_remove_stuffed`, `gfs2_xattr_remove`, `ea_dealloc_indirect`, and `ea_dealloc_block`.

## Control Flow
All xattr enumeration walks from `ip->i_eattr`. A direct EA block is scanned as EA records; an indirect EA fork first reads an indirect block and then scans each pointed-to EA block. Every record is bounds-checked, type-checked against filesystem format, and passed to a callback.

Get operations hold the inode glock shared unless already held, find the typed name, and copy stuffed data directly or unstuffed data through metadata data blocks. Set operations acquire quota data, hold the inode glock exclusive unless already held, validate immutable/append-only and name/data sizes, then initialize a new EA fork, replace in place, split an existing free tail, allocate unstuffed data blocks, or add a new EA block through direct-to-indirect conversion. Removal treats NULL value as delete, merges stuffed records where possible, or frees unstuffed data blocks under the owning rgrp glock.

Deallocation for inode eviction first removes unstuffed EA data, then frees indirect EA block pointers if present, then frees the primary EA block and updates the dinode when initialized.

## State And Persistence
Persistent state includes the dinode `di_eattr` pointer, `GFS2_DIF_EA_INDIRECT`, EA blocks, indirect pointer blocks, unstuffed EA data blocks, inode block counts, quota/statfs deltas, and ctime. All metadata mutations run inside GFS2 transactions and use rgrp allocation/freeing for block state.

## Dependencies And Integration Points
The file integrates VFS xattr handlers, POSIX ACL support, inode glocks, metadata I/O, rgrp allocation, quota, statfs, transactions, and GFS2 format-version rules. `super.h` exports handler arrays that choose trusted-xattr support based on filesystem format.

## Risks And Test Signals
Risks include malformed EA record lengths, direct/indirect fork transition bugs, leaking unstuffed blocks on replacement failure, quota/statfs drift, append-only enforcement differences, and using stale buffer pointers after replacing/removing an EA. Signals include xfstests xattr/ACL coverage, large xattr tests crossing stuffed thresholds, format-minimum trusted-xattr rejection, crash replay after xattr replacement, and fsck verification of EA forks.
