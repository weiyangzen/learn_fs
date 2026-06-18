# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_ipip.c

## Purpose
This file provides GRE-over-IPv4 and GRE-over-IPv6 offload operations for Spectrum IP-in-IP routing. It extracts Linux tunnel parameters, validates offloadable tunnel shapes, programs underlay nexthop and decapsulation registers, manages IPv6 destination-address KVDL references, initializes tunnel ECN mapping tables, and exposes underlay-device lookup.

## Important APIs, Types, And Functions
Exported helpers include `mlxsw_sp_ipip_netdev_parms4()`, `mlxsw_sp_ipip_netdev_parms6()`, `mlxsw_sp_ipip_netdev_saddr()`, `mlxsw_sp_l3addr_is_zero()`, `mlxsw_sp_ipip_ecn_encap_init()`, `mlxsw_sp_ipip_ecn_decap_init()`, and `mlxsw_sp_ipip_netdev_ul_dev_get()`. Operation tables are `mlxsw_sp1_ipip_ops_arr[]` and `mlxsw_sp2_ipip_ops_arr[]`, each containing GRE4 and GRE6 `mlxsw_sp_ipip_ops`. GRE-specific callbacks initialize parameters, update RATR nexthops, build RTDP decap entries, produce overlay loopback RIF configuration, handle netdev parameter changes, and set/unset remote IPv6 address references.

## Control Flow
Tunnel offload starts by reading `ip_tunnel` or `ip6_tnl` parameters and ensuring local and remote addresses are set, TTL and TOS/class inheritance match hardware assumptions, and no unsupported tunnel flags are present beyond optional keys. Nexthop updates pack `MLXSW_REG_RATR_TYPE_IPIP` with the loopback RIF and either an IPv4 DIP or IPv6 KVDL pointer. Decap programming writes RTDP with SIP filtering that matches Linux tunnel demux behavior and traps decap errors. Overlay netdev changes decide whether to rebuild tunnel state, update only nexthops, or update decap based on changed source, keys, link, and destination.

## State And Persistence
State lives in `struct mlxsw_sp_ipip_entry`, especially cached tunnel parameters, overlay device, loopback RIF, decap FIB entry, DIP KVDL index, and list node. Hardware state is register-backed RATR adjacency entries, RTDP tunnel entries, RITR loopback attributes, KVDL IPv6 address storage, parsing-depth requirements, and ECN remap tables. Nothing is persisted beyond current driver/hardware lifetime.

## Dependencies And Integration Points
The file depends on Linux IP tunnel and IPv6 tunnel internals, mlxsw router/IPIP management functions declared elsewhere, KVDL IPv6 address reference helpers, ECN helpers, RTDP/RATR/TIEEM/TIDEM register packing, and trap IDs for decap ECN errors. It is consumed through `spectrum_ipip.h` by router and RIF code.

## Risks And Edge Cases
Incomplete tunnels with zero local or remote address are valid Linux constructs but intentionally not offloaded. GRE key handling must distinguish input and output keys. IPv6 GRE depends on correct acquire/release of address KVDL references during netdev changes and rollback. The checked-out source contains a duplicated function declaration line before the GRE6 loopback config, which is a compile-risk signal. ECN table initialization must cover all inner/outer ECN combinations and trap invalid decap cases consistently.

## Test Signals
Test GRE4/GRE6 tunnel add/remove, keyed and unkeyed tunnels, remote/local address changes, underlay link changes, nexthop refresh, IPv6 address KVDL leak checks, rejection of unsupported flags/TOS/TTL/incomplete tunnels, ECN decap trap behavior, and offload survival across tunnel parameter churn.
