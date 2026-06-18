# sources/distributed-fs/openafs/src/vol/vnode_inline.h

## Purpose

`vnode_inline.h` contains inline vnode cache helper routines, especially the demand-attach vnode state machine. It centralizes reservation, lock, state transition, wait, and read-count operations used by `vnode.c`.

## Important APIs and Functions

`VnCreateReservation_r` increments a vnode refcount and removes it from LRU when it becomes active. `VnCancelReservation_r` decrements the refcount, returns the vnode to LRU when it reaches zero, and optionally removes the vnode from the volume vnode list when `TrustVnodeCacheEntry` is false.

`VnLock` and `VnUnlock` abstract vnode locking. Under DAFS, they mostly set/clear the writer field because DAFS state transitions provide synchronization; under non-DAFS they acquire/release read/write locks, dropping `VOL_LOCK` when needed to avoid deadlock.

DAFS-only helpers include `VnChangeState_r`, `VnIsExclusiveState`, `VnIsErrorState`, `VnIsValidState`, `VnWaitStateChange_r`, `VnWaitExclusiveState_r`, `VnWaitQuiescent_r`, `VnBeginRead_r`, and `VnEndRead_r`.

## Control Flow and State

The normal DAFS read path waits until the vnode is not in an exclusive state, changes `ONLINE` to `READ` when the first reader starts, increments `nReaders`, and returns. The write path waits for quiescence and changes state to `EXCLUSIVE`. Store/load/allocation/release paths use exclusive states and broadcast on every state change. Ending the last reader broadcasts and returns the vnode to `ONLINE`.

## Dependencies and Integration Points

The header depends on `vnode.h`, OpenAFS `VOL_LOCK`/condition-variable primitives, pthread or LWP writer identity, and list helpers from `vnode.c`. It is included by vnode implementation and any internal code needing the state-machine helpers.

## Risks and Test Signals

The highest risk is incorrect lock-state pairing: forgetting `VnCancelReservation_r`, beginning reads from the wrong state, or failing to broadcast on state changes can stall DAFS. Tests should cover reader transitions, writer thread identity, LRU membership across reservation creation/cancellation, error-state detection, wait behavior under concurrent exclusive operations, and non-DAFS lock acquisition with and without `VOL_LOCK`.
