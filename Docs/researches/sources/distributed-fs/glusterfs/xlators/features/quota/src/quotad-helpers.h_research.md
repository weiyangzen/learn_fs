# sources/distributed-fs/glusterfs/xlators/features/quota/src/quotad-helpers.h

## Purpose
`quotad-helpers.h` declares the helper routines for freeing aggregator state and constructing call frames from RPC service requests.

## Important APIs and Types
- `quotad_aggregator_free_state(quotad_aggregator_state_t *state)` releases state-owned dictionaries and memory.
- `quotad_aggregator_get_frame_from_req(rpcsvc_request_t *req)` allocates a frame/state pair and copies request credentials.

## Control Flow
The header supports the `quotad-aggregator.c` flow where each RPC actor allocates a frame before winding a nameless lookup and later frees it during reply submission.

## State and Persistence
No state is stored in this header. It exposes functions that manage per-request in-memory state.

## Dependencies and Integration Points
It includes `rpcsvc.h` and `quotad-aggregator.h`. Any code including it gains the request/frame helper contract.

## Risks
The API surface is small but cleanup-sensitive. Callers must ensure every allocated frame reaches reply submission or equivalent cleanup.

## Test Signals
Build coverage plus request-handler tests that ensure state is freed exactly once in success and error paths.
