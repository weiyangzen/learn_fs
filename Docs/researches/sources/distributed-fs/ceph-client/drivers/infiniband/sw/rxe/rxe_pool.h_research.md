# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.h

## Purpose

`rxe_pool.h` defines RXE pooled-object metadata, pool state, object type IDs, and convenience macros for lifecycle operations.

## Important APIs, Types, and Functions

It defines `enum rxe_elem_type`, `struct rxe_pool_elem`, `struct rxe_pool`, and wrappers such as `rxe_add_to_pool()`, `rxe_get()`, `rxe_put()`, `rxe_cleanup()`, `rxe_read()`, and `rxe_finalize()`.

## Control Flow

Callers allocate an RXE object, add it to the pool, initialize it, finalize it for lookup, and later reference or cleanup it through these APIs.

## State and Persistence Behavior

Pool metadata persists in the RXE device. Embedded elements persist for each RDMA object and coordinate lookup visibility and final release.

## Dependencies and Integration Points

The header depends on kernel xarray/kref/completion/list primitives through the RXE include graph and is included by `rxe_verbs.h`.

## Risks and Edge Cases

Macros require an embedded field named `elem`. Finalizing before initialization or cleaning up while users expect lookup visibility can create severe lifetime bugs.

## Test Signals

Compile all pool users and run refcount/leak/race tests around create, lookup, cleanup, and finalization.
