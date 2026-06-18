# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_mr.h

## Purpose
This header defines the generic multicast-routing offload contract used by Spectrum router code and backend hardware implementations. It describes route keys, route values, actions, backend operation vectors, and the public table/route/VIF/RIF lifecycle API.

## Important APIs, Types, And Functions
`enum mlxsw_sp_mr_route_action` distinguishes forward, trap, and trap-and-forward. `struct mlxsw_sp_mr_route_key` stores VR ID, protocol, group/source addresses, and masks. `struct mlxsw_sp_mr_route_info` carries action, ingress RIF, egress RIF array, count, and minimum MTU. `struct mlxsw_sp_mr_route_params` combines key, value, and priority. `struct mlxsw_sp_mr_ops` is the backend ABI with init/fini, create/update/destroy, stats, action/min-MTU/iRIF/eRIF updates, and private-size fields. Public functions cover core init/fini, route add/delete, VIF add/delete, RIF add/delete/MTU update, table create/destroy/flush, and emptiness checks.

## Control Flow
Users create an MR core with a backend ops vector, create per-VR/protocol tables, add VIFs and routes as multicast routing events arrive, and notify the core when RIFs appear/disappear or change MTU. The core then calls backend ops with route params and incremental updates.

## State And Persistence
The header declares opaque `mlxsw_sp_mr` and `mlxsw_sp_mr_table` types; concrete state is in `spectrum_mr.c` and backend-private blobs. All state is runtime only.

## Dependencies And Integration Points
It includes Linux `mroute`/`mroute6`, Spectrum router types, and main Spectrum definitions. It is consumed by router multicast code and TCAM backend code.

## Risks And Edge Cases
Backend implementers must honor the update semantics: some updates are ordered so route action changes make iRIF/eRIF changes visible at the right time. `erif_indices` is caller-allocated and only valid for the duration of the backend call. New route actions or priorities require synchronized core/backend updates.

## Test Signals
Compile all backend ops implementations, verify route create/update/destroy ABI use, route stats propagation, and correct behavior for VIF/RIF event ordering.
