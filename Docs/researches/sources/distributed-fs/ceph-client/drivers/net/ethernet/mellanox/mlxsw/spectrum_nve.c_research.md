# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.c

## Purpose
This file implements the shared NVE/VXLAN offload core. It manages global NVE tunnel lifetime, multicast flood lists, per-FID VNI enable/disable, FDB replay/offload cleanup, IPv6 address mappings for learned remote endpoints, NVE QoS/ECN initialization, and per-port tunnel decap queue setup.

## Important APIs, Types, And Functions
Public APIs include `mlxsw_sp_nve_init()`, `mlxsw_sp_nve_fini()`, `mlxsw_sp_nve_fid_enable()`, `mlxsw_sp_nve_fid_disable()`, `mlxsw_sp_nve_flood_ip_add()`, `mlxsw_sp_nve_flood_ip_del()`, IPv6 KVDL/map helpers, `mlxsw_sp_nve_learned_ip_resolve()`, and port init/fini. Internal structures represent multicast lists keyed by FID, linked TN UMT records, IPv4/IPv6 multicast entries, and MAC/FID-to-IPv6 endpoint mappings.

## Control Flow
Initialization allocates `mlxsw_sp_nve`, initializes multicast and IPv6 rhashtables, programs tunnel QoS and ECN maps, and queries per-record resource limits. FID enable validates VXLAN parameters through type ops, derives a config, rejects conflicting global tunnel configs, initializes the global tunnel on the first FID, sets the FID VNI, and replays VXLAN FDB entries. FID disable flushes flood IPs, hardware FDB entries, IPv6 maps, clears VXLAN offload flags, clears the FID VNI, and decrements global tunnel usage. Flood-IP add/create paths allocate list records in KVDL and write linked TN UMT entries; delete/flush carefully preserve the FID's first-record pointer semantics.

## State And Persistence
Runtime state includes the current global NVE config, multicast-list hash table, IPv6 endpoint hash/list, number of active NVE tunnels, max record sizes, tunnel KVDL index, and underlay RIF index for Spectrum-2. Hardware state includes TNQCR/TNEEM/TNDEM QoS/ECN maps, TN UMT records, FID flood indexes, VNI association, NVE FDB entries, KVDL IPv6 addresses, and global tunnel registers programmed by type-specific ops.

## Dependencies And Integration Points
The file depends on VXLAN ops through `spectrum_nve_vxlan.c`, FID APIs, router underlay RIF/decap promotion, KVDL, IPv6 address reference helpers, switchdev notifier FDB replay, SFDF FDB flush registers, and devlink resources for NVE multicast entries.

## Risks And Edge Cases
Only one global tunnel config can be active; mismatched VXLAN devices are rejected once a tunnel exists. Multicast record deletion is delicate because the first KVDL record index is stored in the FID; deleting first or middle records requires pointer rewrites or KVDL index swaps. IPv6 address maps must release address references on replace/delete/flush. The checked-out source contains several duplicated tokens/braces/comments and a duplicated `ops` declaration in `mlxsw_sp_nve_fid_enable()`, which are compile-risk signals. Many paths assume RTNL for FID/netdev operations.

## Test Signals
Test NVE init/fini, VXLAN FID enable/disable, conflicting tunnel configs, FDB replay and clear-offload behavior, IPv4/IPv6 flood IP add/delete/flush across multiple KVDL records, IPv6 endpoint replace/delete reference balance, ECN mapping traps, FDB flush by FID, and WARN-free unload after all FIDs are disabled.
