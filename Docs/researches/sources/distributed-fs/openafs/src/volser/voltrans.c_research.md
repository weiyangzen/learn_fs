# sources/distributed-fs/openafs/src/volser/voltrans.c

## Purpose

`voltrans.c` implements the in-memory Volser transaction registry. Transactions serialize and track operations on a given volume id and partition, hold attached `Volume *` objects, provide debug/status data to `volprocs.c`, and allow stale or abandoned operations to be reclaimed by the background GC loop.

## Important APIs and State

Module state includes `allTrans`, the active transaction list head; `transCounter`, the transaction id generator; `OLDTRANSTIME` and `OLDTRANSWARN`, timeout thresholds; and internal `GCDeletes`. Exported functions are `NewTrans`, `FindTrans`, `DeleteTrans`, `TRELE`, `GCTrans`, and `TransList`.

`NewTrans` enforces one active transaction per volume/partition and returns a refcounted transaction. `FindTrans` refreshes last-active time and increments the refcount. `DeleteTrans` detaches volumes, kills tracked Rx calls, unlinks/free transactions, or marks `TTDeleted` for deferred free. `TRELE` releases references and completes deferred deletion. `GCTrans` logs old transactions and deletes timed-out unreferenced ones, purging abandoned temporary `DESTROY_ME` volumes. `TransList` returns the raw list head.

## Control Flow

All list and refcount mutation is protected by `VTRANS_LOCK`. `NewTrans` allocates, scans for duplicates, initializes fields and per-transaction lock, and links at the list head. `FindTrans` scans by id and increments `refCount`. `DeleteTrans` either marks a referenced transaction deleted or unlinks, detaches, aborts the Rx call, destroys the lock, and frees it. `TRELE` decrements or deletes when `TTDeleted` and this is the last reference.

`GCTrans` runs from `volmain.c`'s background loop. It warns about old transactions, increments a timed-out transaction's refcount while operating on it, drops the global lock around `VPurgeVolume`, then reacquires and deletes safely, taking care to recompute next-list pointers after relocking.

## State and Persistence Behavior

Most state is in-memory transaction metadata. Persistent effects occur when `DeleteTrans` detaches an attached volume and when `GCTrans` purges abandoned temporary volumes marked `DESTROY_ME`. `DeleteTrans` also marks tracked Rx calls dead with `RX_CALL_DEAD`, affecting client-observable state.

## Dependencies and Integration Points

The module depends on `volser.h`, `volser_internal.h`, Rx call handling, and the OpenAFS volume package. It is driven by `volprocs.c` for every RPC transaction, by `volmain.c` for background GC and idle checks, and by `voltrans_inline.h` users that update debug fields inside `struct volser_trans`.

## Risks and Edge Cases

Risks include raw `TransList` access without locking, transaction id wraparound in very long-lived processes, misuse of `DeleteTrans` with pointers not in `allTrans`, races if GC lock-drop behavior is edited incorrectly, and confusion between global list locking and per-transaction debug locking.

## Test Signals

Tests should cover duplicate transaction rejection, find/release lifecycle, delete with outstanding references, final `TRELE` after `TTDeleted`, detach and Rx call cancellation on delete, GC warning/timeout behavior, GC purge of abandoned temporary volumes, and concurrent monitor traversal under load.
