<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.c

## Purpose

`enic_api.c` exports a small public ENIC API for issuing firmware device commands proxied to a VF by index. It is intended for peer kernel components that need controlled access to ENIC devcmd operations.

## Important APIs, Types, and Functions

The sole exported function is `enic_api_devcmd_proxy_by_index(struct net_device *netdev, int vf, enum vnic_devcmd_cmd cmd, u64 *a0, u64 *a1, int wait)`. It obtains `struct enic` from the netdev, waits while `enic_api_busy` is set, locks `devcmd_lock`, starts proxy mode with `vnic_dev_cmd_proxy_by_index_start`, runs `vnic_dev_cmd`, ends proxy mode, and returns the firmware command result.

## Control Flow

Callers enter with a netdev and VF index. The function spin-waits with `cpu_relax()` while reset paths mark the API busy. It then serializes against other devcmd users with `devcmd_lock`, wraps the command in proxy start/end calls, and releases both locks.

## State and Persistence Behavior

It mutates only transient vNIC proxy state around the command. Persistent effects depend on the command passed by the caller and firmware behavior. `enic_api_busy` is set elsewhere during reset/hang recovery to block external activity.

## Dependencies and Integration Points

The file depends on `vnic_dev`, `vnic_devcmd`, `enic_res`, and `enic.h`. The symbol is exported with `EXPORT_SYMBOL`, so lock semantics here are part of an inter-module contract.

## Risks and Edge Cases

The busy wait is a raw spin loop, so a stuck `enic_api_busy` can burn CPU. There is no VF validation here; callers or firmware must reject invalid VF indexes. Lock ordering with reset paths is critical: API lock is taken before `devcmd_lock`, matching the reset path's busy-flag coordination.

## Test Signals

Test proxied devcmd success/failure, concurrent calls during `enic_reset`/`enic_tx_hang_reset`, invalid VF indexes, long wait command timeout behavior, and module users resolving the exported symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/enic_api.c -->
