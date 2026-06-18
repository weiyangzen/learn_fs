# sources/distributed-fs/ceph/src/mds/MDSContinuation.h

## Purpose

`MDSContinuation.h` declares `MDSContinuation`, a small adapter between Ceph's generic `Continuation` framework and MDS callback types. It lets staged server operations request callbacks already wrapped as `MDSInternalContext` or `MDSIOContextBase`.

## Important APIs And Control Flow

`MDSContinuation` stores a `Server*` and passes `NULL` to the base `Continuation` constructor. `get_internal_callback(stage)` calls the base `get_callback(stage)` and wraps the returned generic context in `MDSInternalContextWrapper(server->mds, ...)`. `get_io_callback(stage)` similarly wraps the stage callback in `MDSIOContextWrapper`.

## State And Persistence Behavior

This file has no persistence behavior. It holds only the server pointer needed to access `server->mds` for context wrapping. Persistent side effects occur in the staged callbacks created by users of the continuation.

## Dependencies And Integration Points

It includes `common/Continuation.h`, `mds/Mutation.h`, `mds/Server.h`, and `MDSContext.h`. It is intended for multi-stage MDS server operations where some stages complete internally and others complete from I/O.

## Risks And Test Signals

The main risks are callback ownership and incorrect wrapper selection. A stage that completes from I/O must use `get_io_callback` so it acquires `mds_lock`; a stage already under MDS control should use `get_internal_callback`. Tests should cover staged operation cancellation, callback deletion, and lock expectations for both wrapper types.
