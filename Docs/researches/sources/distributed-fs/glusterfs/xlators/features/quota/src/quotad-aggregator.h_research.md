# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-aggregator.h

## Purpose
`quotad-aggregator.h` declares the quotad aggregator request state and public entry points used by the quotad server and helper files. It is the bridge between RPC request handling and the nameless lookup helper.

## Important APIs and Types
- `quotad_aggregator_state_t` stores allocator pool, current xlator, active child subvolume, inode table, loc, request xdata, and lookup xdata for one aggregator request.
- `quotad_aggregator_lookup_cbk_t` is the callback signature used by `qd_nameless_lookup()` to return a protocol-specific response object to aggregator code.
- `qd_nameless_lookup()` is declared for performing GFID-based child lookups.
- `quotad_aggregator_init()` is declared for starting and registering the RPC service.

## Control Flow
The header enables `quotad-helpers.c` to allocate and attach state, `quotad.c` to expose nameless lookup, and `quotad-aggregator.c` to initialize and handle RPC actors.

## State and Persistence
Only per-request in-memory state is defined. Dictionaries inside the state are ref-counted and freed by `quotad_aggregator_free_state()` in `quotad-helpers.c`.

## Dependencies and Integration Points
The header includes `quota.h` and GlusterFS stack definitions. It is included by both helper and service implementation files, so changes to `quotad_aggregator_state_t` affect allocation/free and lookup paths together.

## Risks
The `active_subvol` and `itable` fields must remain consistent with the child selected by volume UUID; stale or mismatched state would route validation to the wrong volume. The generic callback signature uses `void *rsp`, so response type correctness is enforced only by calling convention.

## Test Signals
Compile coverage for all includers plus RPC integration tests that allocate frames, select child volumes, and free state on both success and error paths.
