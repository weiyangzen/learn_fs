# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.c

## Purpose
This file implements the generic multicast-routing offload core. It tracks multicast routing tables, virtual interfaces, multicast forwarding cache routes, route-to-VIF relationships, route action decisions, catchall trap routes, and periodic hardware counter synchronization. Hardware programming is delegated through `mlxsw_sp_mr_ops`.

## Important APIs, Types, And Functions
Key types are `struct mlxsw_sp_mr`, `mlxsw_sp_mr_table`, `mlxsw_sp_mr_vif`, `mlxsw_sp_mr_route`, and route/VIF list-entry structures. Public APIs include `mlxsw_sp_mr_init()`, `mlxsw_sp_mr_fini()`, `mlxsw_sp_mr_table_create()`, `mlxsw_sp_mr_table_destroy()`, `mlxsw_sp_mr_table_flush()`, `mlxsw_sp_mr_table_empty()`, route add/delete, VIF add/delete, RIF add/delete, and RIF MTU update. Protocol-specific tables build IPv4 and IPv6 route keys, reject proxy `(*,*)` routes, and classify regular VIFs.

## Control Flow
Initialization allocates core state, initializes backend ops, and schedules delayed stats work. Table create initializes route hash/list state, per-VIF lists, protocol ops, and a catchall trap route. Route add validates the MFC, creates a route object linked to iVIF/eVIFs, computes min MTU and action, detects duplicate/proxy cases, writes hardware through ops, inserts into list/hash, and updates `MFC_OFFLOAD`. Replace reuses the original route private state and swaps data structures after hardware update. VIF/RIF resolve and unresolve paths update affected routes' iRIF/eRIF lists, min MTU, actions, and offload flags.

## State And Persistence
Runtime state includes the global table list, per-table VIF array, route hash table and list, cached route action/min MTU, retained `mr_mfc` refs, and backend private blobs. Hardware state lives behind ops calls. Periodic stats work reads backend counters and writes packet/byte/lastuse into kernel MFC counters. No on-disk state exists.

## Dependencies And Integration Points
The file integrates Linux IPv4/IPv6 multicast routing structures, router RIF objects, delayed work, rhashtable, and backend implementations such as `spectrum_mr_tcam.c`. It updates kernel MFC offload flags and counters, so it is tied to the multicast router control plane.

## Risks And Edge Cases
Route action changes depend on VIF regularity, RIF presence, `(*,G)` ingress membership, and valid eVIF count. Error rollback during VIF resolution must reverse partial iRIF/eRIF changes. `route_list_lock` protects route lists but hash operations are also used outside some list locks. MTU increases are not recomputed globally in `mlxsw_sp_mr_rif_mtu_update()`, only decreases update min MTU. The checked-out source contains duplicated assignments/calls in a few locations, which are compile or review-risk signals.

## Test Signals
Test IPv4/IPv6 `(S,G)` and `(*,G)` route add/replace/delete, proxy-route rejection, unresolved VIF trap behavior, tunnel/register VIF trap-and-forward behavior, RIF add/del resolving existing routes, MTU decrease propagation, table flush/destroy warnings, delayed stats updates to MFC counters, and backend error rollback.
