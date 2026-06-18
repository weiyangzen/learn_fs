# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/cluster-syncop.h

## Purpose
`cluster-syncop.h` declares synchronous helper operations for issuing FOPs across a list of cluster subvolumes and collecting per-subvolume replies. It supports lookup, metadata ops, xattrs, locks, entry ops, fd ops, and success-mask helpers.

## Important APIs, Types, and Functions
- `PARALLEL_FOP_ONLIST(...)`: macro that runs a helper function on selected subvolumes, waits on a `syncbarrier_t`, and restores frame state.
- `cluster_local_t`: frame-local wrapper containing reply array and barrier.
- `cluster_*` functions: synchronous multi-subvolume variants for lookup, setattr, get/setxattr, locks, rmdir/unlink/mkdir/readlink/symlink/link/mknod, xattrop, fstat/ftruncate/open/fsetattr/put, and tiebreaker locks.
- `cluster_replies_wipe()`, `cluster_fop_success_fill()`: reply cleanup and success-mask utilities.
- `cluster_xattrop_cbk()`: common callback for xattrop aggregation.

## Control Flow
`PARALLEL_FOP_ONLIST` initializes a stack `cluster_local_t`, wipes reply slots, initializes each reply dirent list, sets up a sync barrier, replaces `frame->local`, counts selected subvolumes from the `on` bitmap, calls the helper for each selected subvolume, waits for callbacks, destroys the barrier, restores the old frame local, and resets the stack root.

## State and Persistence
State is temporary per operation: reply arrays, output/success bitmaps, lock-acquired bitmaps, frame-local barrier state, and callback-filled `default_args_cbk_t` entries. There is no persistence here.

## Dependencies and Integration Points
Depends on `defaults.h`, `default-args.h`, `syncop.h`, `call_frame_t`, `xlator_t`, `loc_t`, `fd_t`, `dict_t`, inode and lock types. Cluster translators use this API to send the same operation to many children and make decisions from collected replies.

## Risks and Edge Cases
- The macro uses a stack local as `frame->local`; callbacks must complete before the macro returns.
- `waitfor` is the selected subvolume count; zero-count behavior depends on syncbarrier implementation.
- Reply entries require initialized list heads before callbacks append dirents.
- Frame local/root state restoration is critical for nested or repeated cluster operations.

## Test Signals
Test selected-subvolume bitmaps, zero and partial selections, callback aggregation, reply wipe/list initialization, lock/unlock rollback masks, success-mask filling, and operations where one subvolume fails or times out.
