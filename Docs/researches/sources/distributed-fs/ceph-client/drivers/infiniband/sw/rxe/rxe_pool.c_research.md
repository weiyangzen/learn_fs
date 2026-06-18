# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.c

## Purpose

`rxe_pool.c` implements indexed, reference-counted pools for RXE ucontexts, PDs, AHs, SRQs, QPs, CQs, MRs, and MWs.

## Important APIs, Types, and Functions

Key functions are `rxe_pool_init()`, `__rxe_add_to_pool()`, `rxe_pool_get_index()`, `__rxe_get()`, `__rxe_put()`, `__rxe_cleanup()`, and `__rxe_finalize()`. `rxe_type_info[]` supplies object sizes, index ranges, limits, and cleanup callbacks.

## Control Flow

Creation allocates an object, adds its embedded element to a pool to reserve an index, initializes object-specific state, then finalizes it into the xarray. Lookup uses RCU and kref acquisition. Cleanup erases the xarray entry, drops the pool reference, waits for outstanding refs, invokes type cleanup, and decrements accounting.

## State and Persistence Behavior

Each pool in `rxe_dev` persists xarray state, index limits, next cyclic index, maximum elements, and current count. Each object persists an embedded `rxe_pool_elem` with kref, completion, index, and object pointer.

## Dependencies and Integration Points

The implementation uses Linux xarray, kref, completions, RCU, and RXE cleanup callbacks. It underpins all verbs object lifetimes and MR/MW/QP/AH lookups.

## Risks and Edge Cases

Objects are not visible by index until `rxe_finalize()`. Non-sleepable AH cleanup busy-waits and can timeout. Timeout after lingering references is severe. Index ranges affect user-visible IDs and rkey classification.

## Test Signals

Stress create/destroy for all object types, lookup-after-destroy races, AH atomic cleanup, MR/MW/QP index reuse, fault injection before finalization, and module unload with outstanding references.
