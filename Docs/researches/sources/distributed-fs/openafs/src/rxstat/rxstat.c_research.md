<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/rxstat.c -->
# sources/distributed-fs/openafs/src/rxstat/rxstat.c

## Purpose

`rxstat.c` implements the server-side RPC manager functions for retrieving, querying, enabling, disabling, clearing, and versioning Rx RPC statistics. It centralizes generic RX stats service behavior so multiple OpenAFS servers can expose the same RPC interface generated from `rxstat.xg`.

## Important APIs and Functions

The exported manager functions use the generated `MRXSTATS_` naming convention:

- `MRXSTATS_RetrieveProcessRPCStats`
- `MRXSTATS_RetrievePeerRPCStats`
- `MRXSTATS_QueryProcessRPCStats`
- `MRXSTATS_QueryPeerRPCStats`
- `MRXSTATS_EnableProcessRPCStats`
- `MRXSTATS_EnablePeerRPCStats`
- `MRXSTATS_DisableProcessRPCStats`
- `MRXSTATS_DisablePeerRPCStats`
- `MRXSTATS_QueryRPCStatsVersion`
- `MRXSTATS_ClearProcessRPCStats`
- `MRXSTATS_ClearPeerRPCStats`

Retrieve functions call `rx_RetrieveProcessRPCStats` or `rx_RetrievePeerRPCStats`, passing the client protocol version, output version and clock fields, and a returned allocation size. They store the returned stats pointer in `stats->rpcStats_val` and translate byte allocation size to `stats->rpcStats_len` by dividing by `sizeof(afs_uint32)`.

Query functions return the current enablement state from `rx_queryProcessRPCStats` and `rx_queryPeerRPCStats`. Enable/disable/clear functions authorize through `rx_RxStatUserOk(call)` before mutating RX stats collection state. `MRXSTATS_QueryRPCStatsVersion` returns `RX_STATS_RETRIEVAL_VERSION`.

## Control Flow

The file has direct wrapper control flow with little local logic. Mutating functions initialize `rc` to 0, check authorization, set `EPERM` on failure, and call the corresponding RX stats mutator on success. Retrieval functions delegate allocation and data population to the RX layer, then update the generated RPC array length regardless of the return code.

## State and Persistence Behavior

This file owns no persistent state. The actual process and peer RPC stats state lives in the RX subsystem. Calls here can toggle collection state and clear counters through RX APIs, so their effects are process-global within the hosting server. Retrieved `rpcStats_val` memory ownership is handed to the generated RPC/XDR layer through the `rpcStats` output structure.

## Dependencies and Integration Points

The file includes OpenAFS config/parameter headers, `roken.h` for non-kernel builds, `afs/stds.h`, `rx/rx.h`, and the generated `rx/rxstat.h`. In kernel non-UKERNEL builds it includes `sys/errno.h`. It depends directly on RX stats APIs and on generated RPC types such as `rpcStats`, `IN`, and `OUT`.

The manager function names match generated server stubs from `rxstat.xg`; those stubs dispatch incoming Rx RPC calls to these functions. Authorization is delegated to `rx_RxStatUserOk`, so security policy is centralized in the RX layer rather than in this file.

## Risks and Edge Cases

The retrieve functions set `stats->rpcStats_len` from `allocSize` even if the underlying retrieve call returns an error. If the RX API does not initialize `allocSize` and `stats->rpcStats_val` on failure, this could expose stale stack data or an invalid length; validation should confirm the RX retrieval contract. The cast to `u_int` can truncate very large allocation sizes, though stats arrays should be bounded by protocol design.

Mutating functions rely entirely on `rx_RxStatUserOk(call)` for access control. Any server exposing this interface must ensure that function correctly identifies privileged callers in its security class and deployment context. Clear operations accept `clearFlag` without local validation, so accepted semantics are defined by the RX subsystem.

## Test Signals

Unit tests or RPC integration tests should cover authorized and unauthorized enable/disable/clear calls, process and peer stats query toggles, retrieval length/value consistency, version query returning `RX_STATS_RETRIEVAL_VERSION`, and retrieval failure behavior. Tests should verify generated stubs marshal `rpcStats_len` as a count of `afs_uint32`, not bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxstat/rxstat.c -->
