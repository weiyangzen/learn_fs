# sources/distributed-fs/glusterfs/libglusterfs/src/cluster-syncop.c

## Purpose
`cluster-syncop.c` provides synchronous cluster-wide FOP helpers for translators that need to issue the same operation to selected subvolumes and wait for callbacks from all of them. It bridges asynchronous GlusterFS stack winds with `syncbarrier_t` so callers receive arrays of `default_args_cbk_t` replies and success masks.

## Important APIs, Types, And Functions
The main macros are `FOP_ONLIST`, `FOP_SEQ`, and `FOP_CBK`. `FOP_ONLIST` initializes a `cluster_local_t`, wipes replies, counts enabled subvolumes, winds the FOP to each selected child using `STACK_WIND_COOKIE`, waits on the barrier, restores frame local state, and resets the stack. `FOP_SEQ` performs the same pattern one selected subvolume at a time. `FOP_CBK` stores callback arguments into the indexed reply slot and wakes the barrier.

`cluster_replies_wipe()` cleans previous reply ownership with `args_cbk_wipe`. `cluster_fop_success_fill()` builds a success bitmap and returns the count of valid nonnegative replies. The file defines callback shims for all supported FOPs, then wrapper functions such as `cluster_lookup`, `cluster_stat`, `cluster_create`, `cluster_writev`, `cluster_xattrop`, and many others. Lock-specific helpers include `cluster_tryinodelk`, `cluster_inodelk`, `cluster_uninodelk`, `cluster_tryentrylk`, `cluster_entrylk`, tiebreaker variants, and unlock helpers.

## Control Flow
A caller provides `subvols`, an `on` bitmap, `numsubvols`, reply storage, an output bitmap, and a call frame. The wrapper macro wipes previous replies, initializes per-reply entry lists, installs a stack-local `cluster_local_t` into `frame->local`, winds selected operations with the subvolume index encoded as the callback cookie, waits for callbacks, restores `frame->local`, and computes the success bitmap. Callback shims copy all callback values into the proper reply slot through `args_*_cbk_store`.

Lock helpers first try nonblocking locks across selected subvolumes. If any selected reply returns `EAGAIN`, they fill the locked bitmap, unlock already acquired subvolumes, then retry sequential blocking locks to avoid deadlocks. Tiebreaker variants return zero immediately if the first contention occurs before any successful lock.

## State And Persistence Behavior
State is transient and stack-scoped. Replies are caller-owned arrays of `default_args_cbk_t`; the code wipes and reinitializes them before use. `frame->local` is temporarily overwritten and restored. Lock helpers create temporary `loc_t` values with inode refs and GFIDs and wipe them before returning. No persistent storage is modified directly, though the FOPs sent to subvolumes may perform persistent filesystem changes.

## Dependencies And Integration Points
This file depends on `glusterfs/cluster-syncop.h`, stack wind macros, `syncbarrier_t`, `default-args` callback storage, `loc_t`, inode refs, locks, and xlator FOP vectors. It is used by cluster translators that coordinate replicate/disperse/distribute behavior and need synchronous fan-out without manually writing callback aggregation each time.

## Risks And Edge Cases
The file explicitly warns that these helpers block the executing thread when not running inside a synctask, so they should not run on epoll worker threads. If `syncbarrier_init()` fails inside the macros, the wrappers break out and then report success based on wiped replies, generally zero, with little detail. `memset(output, 0, numsubvols)` assumes the output mask has at least `numsubvols` bytes. `frame->local` is reused for aggregation, so nested or concurrent use on the same frame would be unsafe. The callback and wrapper families must stay in lockstep with FOP signatures. Lock retry paths rely on correct reply validity and cleanup to avoid leaving partial locks behind.

## Test Signals
Tests should cover fan-out to selected subvolumes, zero selected subvolumes, partial failures, reply ownership wipe between calls, barrier wake count correctness, sequential lock retry after `EAGAIN`, unlock of partially acquired locks, tiebreaker semantics, and detection of accidental use from event-loop threads.
