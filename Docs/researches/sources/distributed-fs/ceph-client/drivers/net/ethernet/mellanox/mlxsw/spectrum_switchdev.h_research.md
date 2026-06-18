# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.h

## Purpose

`spectrum_switchdev.h` is a narrow internal header exposing bridge-port lookup and STP-state query helpers to other mlxsw Spectrum files, especially SPAN destination resolution.

## Important APIs, Types, And Functions

The file forward-declares `struct mlxsw_sp_bridge` and `struct mlxsw_sp_bridge_port`. `mlxsw_sp_bridge_port_find()` locates the offloaded bridge-port object for a given bridge member netdevice. `mlxsw_sp_bridge_port_stp_state()` returns the cached STP state from that bridge-port object.

## Control Flow

Callers use these helpers after they have a Spectrum bridge object and a candidate bridge member device. SPAN uses this to verify that a bridge FDB-selected egress port is in a forwarding state before offloading remote mirroring.

## State And Persistence

The header exposes read-only access to switchdev state held in `spectrum_switchdev.c`. It does not allocate or persist state itself.

## Dependencies And Integration Points

The only direct include is `<linux/netdevice.h>`. The integration point is intentionally small to avoid exposing the full bridge data model to unrelated subsystems.

## Risks And Edge Cases

Callers must handle `NULL` from `mlxsw_sp_bridge_port_find()` because bridge devices can be absent, not offloaded, or in transition. The returned pointer is meaningful only under the synchronization assumptions of the caller, normally RTNL.

## Test Signals

Compile-time usage should remain limited. Runtime signals are SPAN remote mirror offload through bridge destinations and STP transitions that cause mirror respin to enable or disable offloadability. No local executable tests were run for this research item.
