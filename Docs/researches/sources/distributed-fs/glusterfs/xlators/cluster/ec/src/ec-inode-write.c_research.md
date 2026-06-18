# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-inode-write.c

## Purpose
This file implements erasure-coded inode-changing FOPs for the GlusterFS disperse translator: metadata xattr updates, `setattr`, allocation and hole punching variants, truncation, and `writev`. It converts user byte ranges into EC fragment ranges, acquires EC locks, performs quorum dispatch to child bricks, combines callback answers, updates cached inode size/version state, and encodes user data into per-brick fragments before winding to children.

## Important APIs, Types, And Functions
The public entry points are `ec_removexattr`, `ec_fremovexattr`, `ec_setattr`, `ec_fsetattr`, `ec_setxattr`, `ec_fsetxattr`, `ec_fallocate`, `ec_discard`, `ec_truncate`, `ec_ftruncate`, and `ec_writev`. Each allocates an `ec_fop_data_t`, copies or references loc/fd/dict/iovec/xdata inputs, assigns a wind function, and enters `ec_manager()`. Shared callback handling is centralized by `ec_inode_write_cbk()`, with write-like answer combination through `ec_combine_write`. The major state-machine handlers are `ec_manager_xattr`, `ec_manager_setattr`, `ec_manager_fallocate`, `ec_manager_discard`, `ec_manager_truncate`, and `ec_manager_writev`.

The write path is the most complex API surface. `ec_writev_prepare_buffers()` normalizes unaligned or multi-iovec writes into an aligned data buffer plus a per-brick output buffer. `ec_writev_start()` performs partial-stripe head/tail reads or cache merges, adjusts append offsets, and temporarily uses root credentials for internal reads. `ec_writev_encode()` calls `ec_method_encode()` to fill one output block per node, and `ec_wind_writev()` sends each node its fragment at `offset / fragments`.

## Control Flow
Most operations follow `INIT/LOCK -> DISPATCH -> PREPARE_ANSWER -> REPORT -> LOCK_REUSE -> UNLOCK -> END`. Lock preparation marks whether the operation updates data, metadata, or only needs query information. Dispatch uses `ec_dispatch_all()` unless an operation needs a delayed internal action, such as write partial-stripe reads, discard zero-fill repair writes, or truncate tail cleanup writes. Answer preparation rebuilds `iatt` with `ec_iatt_rebuild()`, clamps return values to user-visible lengths, and updates inode size through `ec_get_inode_size()` / `ec_set_inode_size()` while the EC inode lock is held.

`discard` first rounds the range to EC fragment boundaries. Whole-fragment parts are dispatched as `discard`; uncovered head/tail bytes are rewritten as zeros with `ec_update_write()`. `truncate` rounds up the on-brick truncate offset, updates the logical inode size, and if a shrink lands inside a stripe, opens an anonymous fd if needed and writes zeros for the leftover encoded fragment tail. `fallocate` rejects unsupported range-transform modes and aligns the allocated range. `setxattr` has an integration-specific path for `SQUOTA_LIMIT_KEY`, dividing the aggregate quota limit by the number of data fragments before writing the xattr to bricks.

## State And Persistence Behavior
Persistent state is stored on child bricks as file data, metadata, and EC xattrs managed by helpers in other EC files. This file updates in-memory `ec_inode_t` size and lock-good masks to make later operations observe consistent logical size. The stripe cache stored under the inode context may retain recently completed full stripes; it is updated on write tail merges and used to avoid extra backend reads for partial-stripe writes. FOP state, callback groups, answer masks, and buffers are transient per `ec_fop_data_t`.

## Dependencies And Integration Points
The file depends on `ec-common`, `ec-helpers`, `ec-combine`, `ec-method`, and `ec-fops` for state machines, locks, quorum dispatch, iatt merging, EC encoding, fd/inode contexts, and child wind wrappers. It integrates with GlusterFS frame/callback conventions (`STACK_WIND_COOKIE`, `QUORUM_CBK`), iobuf/iobref memory management, inode/fd reference management, xdata dictionaries, and POSIX range semantics.

## Risks
The main correctness risks are off-by-one or overflow mistakes while converting user offsets into fragment offsets, stale inode size under concurrent writes, failure to restore root uid/gid after internal reads, partial-stripe corruption when head/tail reads fail, and callback answer mismatches that still reach quorum. Cache invalidation is subtle: stale stripe-cache data would corrupt future partial writes, so tests should stress truncates, discards, and overlapping writes. Error paths must preserve fop references and unwind exactly once.

## Test Signals
Useful signals include disperse write/read consistency across all alignments, append writes, shrinking and extending truncates, fallocate keep-size behavior, discard over sub-stripe and multi-stripe ranges, simple-quota xattr writes, brick failures during partial-stripe repair writes, and statedump stripe-cache counters for hits, misses, evicts, and errors. Quorum tests should verify that successful `op_ret` is converted from fragment bytes back to user bytes.
