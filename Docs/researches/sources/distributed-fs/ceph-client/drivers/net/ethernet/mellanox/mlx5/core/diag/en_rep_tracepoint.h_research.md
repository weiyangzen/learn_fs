# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/en_rep_tracepoint.h

## Purpose

`en_rep_tracepoint.h` declares a representor-neighbor tracepoint for mlx5 Ethernet eswitch/representor neighbor updates.

## Important APIs, Types, and Functions

- `TRACE_EVENT(mlx5e_rep_neigh_update, ...)` records netdev name, MAC address, IPv4/IPv6 destination, and neighbor connectivity.
- The event reads `struct mlx5e_neigh_hash_entry`, `struct mlx5e_neigh`, and a hardware address passed by the caller.

## Control Flow

Representor neighbor update code calls the generated `trace_mlx5e_rep_neigh_update()` helper. The trace assignment maps IPv4 into an IPv6-mapped address for consistent output and copies IPv6 directly for AF_INET6.

## State and Persistence Behavior

No persistent state is changed. Events are transient tracing output.

## Dependencies and Integration Points

Depends on Linux tracepoint APIs and `en_rep.h` neighbor types. It integrates with TC/eswitch representor neighbor tracking and offload debugging.

## Risks and Edge Cases

- The tracepoint assumes `nhe->neigh_dev` and `ha` remain valid during trace assignment.
- Families other than AF_INET/AF_INET6 leave address arrays zeroed.

## Test Signals

Enable the tracepoint and trigger representor neighbor connect/disconnect events for IPv4 and IPv6. Verify netdev name, MAC, addresses, and `neigh_connected` values.
