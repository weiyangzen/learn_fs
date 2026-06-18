# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.h

## Purpose
This header defines the IP-in-IP offload interface shared between tunnel-specific code and Spectrum router/RIF users. It centralizes tunnel type IDs, cached tunnel parameters, per-tunnel entry state, operation callbacks, and parameter extraction helpers for IPv4 and IPv6 GRE devices.

## Important APIs, Types, And Functions
The public helpers are `mlxsw_sp_ipip_netdev_parms4()`, `mlxsw_sp_ipip_netdev_parms6()`, `mlxsw_sp_ipip_netdev_saddr()`, and `mlxsw_sp_l3addr_is_zero()`. `enum mlxsw_sp_ipip_type` defines GRE4, GRE6, and max. `struct mlxsw_sp_ipip_parms` stores underlay protocol, source/destination L3 addresses, link index, and input/output keys. `struct mlxsw_sp_ipip_entry` tracks the overlay netdev, loopback RIF, decap FIB entry, cached params, DIP KVDL index, and list membership. `struct mlxsw_sp_ipip_ops` is the callback vector for capability checks, nexthop programming, loopback configuration, decap programming, netdev changes, and remote-address lifecycle. The header exports Spectrum-1 and Spectrum-2 operation arrays.

## Control Flow
Router code identifies a tunnel type, selects an ops table entry, validates `can_offload()`, creates an overlay loopback RIF from `ol_loopback_config()`, calls `rem_ip_addr_set()` for address-backed resources, programs decap through `decap_config()`, and refreshes nexthops through `nexthop_update()`. Netdev notifier paths use `ol_netdev_change()` to reconcile runtime tunnel changes with hardware state.

## State And Persistence
The header defines only runtime data structures. `mlxsw_sp_ipip_entry` is the durable in-memory representation for as long as a tunnel is offloaded; hardware persistence is handled by the implementation file through registers and KVDL entries.

## Dependencies And Integration Points
It includes Spectrum router definitions, Linux FIB/tunnel headers, and IPv6 tunnel definitions. It is integrated by router, RIF, and nexthop code that need a protocol-neutral IPIP offload contract.

## Risks And Edge Cases
The ops ABI assumes callbacks maintain KVDL and RIF lifetimes across rollback. Callers must respect `inc_parsing_depth` and `double_rif_entry` generation differences. The `ol_dev` pointer is a live netdev dependency and must be protected by the router/netdev notifier lifecycle. New tunnel types require both enum expansion and ops-array population.

## Test Signals
Build coverage should catch missing callback implementations. Runtime signals include successful GRE4/GRE6 offload creation, netdev-change reconciliation, address reference release, nexthop updates, and generation-specific behavior for Spectrum-1 versus Spectrum-2.
