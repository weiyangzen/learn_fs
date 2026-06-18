# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.c

## Purpose
Implements AFR entry-changing directory FOPs: create, mknod, mkdir, link, symlink, rename, unlink, and rmdir. Each operation is wrapped in AFR transaction machinery so parent entry locks, changelog pre/post operations, quorum, and read-subvolume state stay consistent across replicas.

## Important APIs, types, and functions
`afr_build_parent_loc()` derives parent `loc_t` values for entry locks. `__afr_dir_write_fill()` records child replies and fd open state for create. `__afr_dir_write_finalize()` chooses final errno, authoritative inode/parent stats, and response xdata using current readable subvolumes. `__afr_dir_write_cbk()` is the common child callback. `afr_mark_entry_pending_changelog()` and `afr_mark_new_entry_changelog()` mark partial successful creates/mknods/mkdirs so heal can repair new entries. Public FOPs set `local->transaction.wind`, `unwind`, basename fields, parent locs, and call `afr_transaction()`.

## Control flow
The exported FOP copies the caller frame, initializes `afr_local_t`, copies locs and xdata, sets operation-specific continuation fields, then starts an `AFR_ENTRY_TRANSACTION` or `AFR_ENTRY_RENAME_TRANSACTION`. Transaction code obtains internal locks and winds the per-child operation. Once all child callbacks arrive, the common callback finalizes output, optionally unwinds early if nothing failed, updates pending changelogs for partial new-entry success, and resumes the transaction for post-op/unlock.

## State and persistence behavior
Persistent effects are the requested namespace mutations on child bricks and AFR pending changelog xattrs for inconsistent results. In-memory effects include reply arrays, selected readable parent masks, fd context open marks for create, inode refresh flags after failed child replies, and transaction parent/basename lock state.

## Dependencies and integration points
Integrates with `afr_transaction()`, AFR changelog encoding, read-subvolume interpretation, self-heal through pending xattrs, Gluster child entry FOPs, `AFR_STACK_UNWIND`, dict/xdata helpers, inode refresh marking, and quorum/error-selection helpers.

## Risks and test signals
Risks include parent loc construction errors, rename with two parent locks, partial success without pending xattr marking, `ENOTEMPTY` handling not marking failure, missing `gfid-req` on mkdir, stale stat selection after failures, and fd state divergence after create. Tests should cover every entry FOP with all-success, one-child-fail, quorum-fail, rename across parents, create fd open state, new-entry heal marking, and xdata/error propagation.
