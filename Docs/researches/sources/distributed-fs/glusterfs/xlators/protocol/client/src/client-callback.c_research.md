# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-callback.c

## Purpose
Implements client-side handlers for server-to-client Gluster callback RPCs. It decodes callback payloads, converts them into generic upcall structures, forwards child up/down events, and registers the callback actor table for the Gluster callback program.

## Important APIs, Types, And Functions
Actors include `client_cbk_null`, `client_cbk_fetchspec`, `client_cbk_ino_flush`, `client_cbk_cache_invalidation`, `client_cbk_recall_lease`, `client_cbk_child_up`, `client_cbk_child_down`, `client_cbk_inodelk_contention`, and `client_cbk_entrylk_contention`. Decode paths use `xdr_to_generic()` and conversion helpers such as `gf_proto_cache_invalidation_to_upcall()`, `gf_proto_recall_lease_to_upcall()`, and lock-contention converters. `gluster_cbk_actors[]` maps `GF_CBK_*` IDs to functions, and `gluster_cbk_prog` exports program name, number, version, actors, and actor count.

## Control Flow
RPC dispatch calls the actor for the callback ID. Cache invalidation, recall lease, and lock-contention handlers decode XDR from the supplied iovec, build `gf_upcall` payloads, set event types where required, and call `default_notify(this, GF_EVENT_UPCALL, &upcall_data)`. Child up/down callbacks update `clnt_conf_t.child_up` and notify the xlator. All decode paths free XDR-allocated fields and unref dictionaries before returning.

## State And Persistence
Persistent client state touched here is `conf->child_up`. Other data is transient callback-local decoded protocol structs and upcall structs. Upcall consumers above the client handle any cache invalidation or lease state changes.

## Dependencies And Integration Points
Depends on `client.h`, `rpc-clnt.h`, client message IDs, XDR protocol structs, Gluster upcall conversion helpers, `default_notify`, and the RPC client callback program registration mechanism.

## Risks
Handlers rely on `THIS` being the correct client xlator context. Cache invalidation returns `0` even after decode/conversion failures, while other handlers return `ret`; RPC layer expectations should be checked. Missing `event_type` assignment in cache invalidation may be intentional in the converter but is worth verifying against upcall consumers. Memory ownership is manual for XDR strings/xdata and converted dicts.

## Test Signals
Simulate each `GF_CBK_*` actor with valid and malformed XDR. Verify cache invalidation and recall lease reach upper xlators, child up/down toggles `conf->child_up`, lock contention upcalls include domains/names/xdata, all XDR allocations are freed, and unknown/null callbacks log without crashing.
