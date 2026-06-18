# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve_vxlan.c

## Purpose
This file provides VXLAN-specific NVE operations for Spectrum-1 and Spectrum-2+. It validates Linux VXLAN device configuration, converts it to mlxsw NVE config, programs global VXLAN tunnel registers, controls parsing depth and UDP destination port parsing, promotes router decap, and replays/clears VXLAN FDB offload state.

## Important APIs, Types, And Functions
Exported ops are `mlxsw_sp1_nve_vxlan_ops` and `mlxsw_sp2_nve_vxlan_ops`. Shared helpers validate IPv4/IPv6 flags, reject unsupported VXLAN attributes, derive source underlay protocol/IP, and pack TNGCR with TTL/source IP and randomized UDP source-port prefix. Spectrum-1 paths program TNGCR underlay VR and RTDP NVE entry. Spectrum-2 paths additionally program TNPC learning, underlay RIF, SPVTR tunnel-port VLAN mode, SPVID decap ethertype behavior, and RTDP egress RIF.

## Control Flow
Capability validation rejects multicast remote IP, missing source IP, bound local interface, non-default source-port range, non-inherit TOS, TTL inherit or zero TTL, nonzero flow label, unsupported flags, and Spectrum-1 802.1ad bridge VXLAN. Init sets VXLAN UDP destination parsing, increases parsing depth, programs generation-specific tunnel config, writes RTDP, and promotes router decap. Error paths clear config, decrease parsing depth, and reset UDP parsing. Fini demotes decap and reverses init state. FDB replay calls `vxlan_fdb_replay()` with the mlxsw switchdev notifier.

## State And Persistence
No large local state is owned. It writes global tunnel hardware state and stores Spectrum-2 underlay RIF index in `nve->ul_rif_index`. VXLAN offload marks live in the VXLAN/FDB subsystem and are replayed or cleared through kernel VXLAN helpers.

## Dependencies And Integration Points
Dependencies include Linux VXLAN internals, random byte generation for UDP source-port prefix, Spectrum parsing-depth and UDP-port parsing controls, router underlay VR/RIF and decap promotion, register packers TNGCR/RTDP/TNPC/SPVTR/SPVID, and switchdev notifier FDB replay.

## Risks And Edge Cases
VXLAN offload is intentionally narrow and rejects many valid software configurations. Spectrum-2 init must release the underlay RIF on every failure after acquisition. Random UDP source-port prefix should remain within Linux VXLAN default range. Parsing depth and UDP destination port must be balanced on all error/fini paths. Global tunnel config sharing means per-device differences are rejected by NVE core.

## Test Signals
Test accepted IPv4 and IPv6 VXLAN configs, rejected unsupported flags and TTL/TOS/source/remote settings, Spectrum-1 802.1ad rejection, Spectrum-2 underlay RIF get/put balance, RTDP programming, FDB replay errors and cleanup, and tunnel fini after multiple enabled FIDs.
