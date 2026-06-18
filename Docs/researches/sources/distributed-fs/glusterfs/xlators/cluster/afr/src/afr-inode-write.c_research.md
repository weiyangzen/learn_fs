# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-write.c

## Purpose
Implements AFR inode write-side FOPs, including data writes, truncation, metadata changes, xattr mutation, allocation/discard/zerofill, xattrop/fxattrop, and fsync. It wraps each operation in AFR transaction machinery to coordinate internal locks, changelogs, readable-subvolume updates, delayed post-op behavior, and split-brain controls.

## Important APIs, types, and functions
`__afr_inode_write_fill()` and `__afr_inode_write_finalize()` are the shared reply collection/finalization path. `afr_writev()` duplicates iovecs, requests active-fd and append-write hints, repairs fd opens, and starts a data transaction; `afr_process_post_writev()` handles unstable writes, short writes, and open-fd count updates. Truncate/ftruncate/fallocate/discard/zerofill set byte-range transaction locks. Setattr/fsetattr and xattr operations use metadata transactions. `afr_handle_special_xattr()` handles split-brain choice/resolve, choice timeout, add-brick, and replace-brick commands. `afr_fsync()` clears unstable-write state and can disable delayed post-op on the last fsync.

## Control flow
Most public FOPs copy the frame, initialize `afr_local_t`, copy loc/fd/xdata, set `transaction.wind` and `transaction.unwind`, set range or metadata lock coordinates, and call `afr_transaction()`. Child callbacks feed the common finalizer. If all child operations succeeded, the original FOP can unwind before or alongside transaction resume; writev has special ordering so delayed post-op state is visible to flush before user unwind.

## State and persistence behavior
Persistent effects include child file data/metadata mutations and AFR pending changelog xattrs maintained by transaction code. In-memory state includes reply arrays, selected readable masks, inode ctx lock/open-fd counters, unstable-write flags, split-brain choice, empty-brick pending matrices, and xdata/xattr response refs. Arbiter bricks receive a one-byte write but report logical length.

## Dependencies and integration points
Depends on `afr_transaction()`, internal lock/common transaction code, self-heal helpers, split-brain helpers, fd reopen repair, protocol-common xdata keys, child write/xattr FOPs, dict utilities, syncbarrier/synctask for empty-brick operations, and AFR inode context tracking.

## Risks and test signals
Risks include short writes causing replica divergence, delayed post-op/flush races, append detection mistakes, arbiter write length translation, internal xattr bypass, split-brain command validation, empty-brick lock coverage, and an apparent `afr_zerofill_unwind()` use of `AFR_STACK_UNWIND(discard, ...)` despite the public zerofill path. Tests should cover partial child failures, append and O_SYNC writes, fsync last-fsync, internal xattr rejection, split-brain set/resolve, replace/add brick marking, range locking for writes/truncates, and zerofill unwind behavior.
