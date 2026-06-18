# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_nve.h

## Purpose
This header defines the shared NVE offload model and type-specific operations used by VXLAN support.

## Important APIs, Types, And Functions
`struct mlxsw_sp_nve_config` captures tunnel type, TTL, learning, UDP destination port, flow label, underlay table/protocol/source IP. `struct mlxsw_sp_nve` stores current config, multicast and IPv6 rhashtables, active tunnel count, resource limits, tunnel index, and Spectrum-2 underlay RIF. `struct mlxsw_sp_nve_ops` defines type-specific capability checks, config derivation, init/fini, FDB replay, and FDB offload clearing. The header exports Spectrum-1 and Spectrum-2 VXLAN ops.

## Control Flow
NVE core code selects an ops object by NVE type, asks it whether a candidate device can be offloaded, derives a normalized config, initializes or reuses the global tunnel, and delegates FDB replay/offload clearing to type-specific code.

## State And Persistence
The header declares runtime-only in-memory state. Hardware programming and resource references are managed by `spectrum_nve.c` and `spectrum_nve_vxlan.c`.

## Dependencies And Integration Points
It includes netlink, rhashtable, and Spectrum base types. It integrates FID/NVE core logic with VXLAN-specific implementation.

## Risks And Edge Cases
Because `num_nve_tunnels` is protected by RTNL, callers must honor RTNL around tunnel enable/disable. Adding new NVE types requires filling ops arrays and ensuring config equality semantics are valid for shared global tunnel state.

## Test Signals
Compile ops providers, validate config derivation for IPv4/IPv6 VXLAN, test multi-FID reuse of one tunnel config, and verify RTNL assertions in enable/disable paths.
