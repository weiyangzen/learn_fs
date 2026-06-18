# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr_tcam.c

## Purpose
This file implements the multicast-routing backend that programs routes into ACL/TCAM with flexible actions. It converts generic MR route parameters into TCAM entries, action blocks, flow counters, and KVDL-backed egress RIF lists.

## Important APIs, Types, And Functions
The exported backend is `mlxsw_sp_mr_tcam_ops`. Internal state includes `struct mlxsw_sp_mr_tcam`, `mlxsw_sp_mr_tcam_route`, `mlxsw_sp_mr_tcam_erif_list`, and `mlxsw_sp_mr_erif_sublist`. Important helpers allocate/flush/commit RIGR2 eRIF sublists, create/destroy AFA blocks, populate eRIF lists, create/update/destroy routes through generation-specific `mlxsw_sp_mr_tcam_ops`, read flow counters, and incrementally update action, min MTU, iRIF, and eRIF membership.

## Control Flow
Backend init verifies `MC_ERIF_LIST_ENTRIES`, allocates generation-private TCAM state, and calls the lower TCAM ops init. Route create stores key/action/iRIF/min-MTU, builds a KVDL eRIF list, allocates a flow counter, creates an AFA block with counter plus trap or multicast-router action, allocates route-private TCAM storage, and inserts the route into hardware. Updates build a new eRIF list and AFA block first, update the TCAM entry atomically through lower ops, then destroy old action/list state. eRIF deletion similarly constructs a replacement list without the removed RIF before swapping.

## State And Persistence
Per-route runtime state includes eRIF KVDL sublists, current AFA block, counter index, route action, key, iRIF, min MTU, and lower-backend private state. Hardware state includes TCAM route entries, AFA blocks, flow counters, and RIGR2 linked-list KVDL records. No durable persistence exists beyond hardware programming lifetime.

## Dependencies And Integration Points
It depends on the generic MR core, KVDL allocator, flow counter allocator, AFA block APIs, ACL flex actions, hardware RIGR2 packing, and generation-specific MR TCAM lower ops stored in `mlxsw_sp->mr_tcam_ops`.

## Risks And Edge Cases
RIGR2 list commit assumes not-yet-pointed entries need no rollback on write failure. Action updates must avoid replacing the old AFA block until TCAM update succeeds. `route_irif_update()` only allows iRIF mutation while the route is trapped. eRIF removal creates a full copy, so KVDL pressure can make deletion fail. The checked-out source contains a duplicated function signature fragment near `mlxsw_sp_mr_tcam_erif_populate()`, a compile-risk signal.

## Test Signals
Test route create/update/destroy for trap, forward, and trap-and-forward, eRIF list sizes above one RIGR2 entry, eRIF add/delete rollback, flow counter reads, KVDL exhaustion, min-MTU/action/iRIF updates, lower TCAM update failure injection, and backend init failure when resources are absent.
