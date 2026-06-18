# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/channels.h

## Purpose

`en/channels.h` declares the public channel accessor and DIM management helpers implemented in `channels.c`.

## Important APIs, Types, and Functions

The header declares channel count, XSK state, regular/XSK/PTP RQN lookup, RX/TX DIM enable/disable, and RX/TX DIM toggle helpers for `struct mlx5e_channels`.

## Control Flow

Consumers use these helpers instead of directly walking `struct mlx5e_channels` when integrating with flow steering, RX resources, PTP, and ethtool coalescing.

## State and Persistence Behavior

The declarations represent read access to channel IDs and mutation of per-queue DIM state through the implementation.

## Dependencies and Integration Points

Depends on Linux kernel types and a forward declaration of `struct mlx5e_channels`. It avoids pulling all of `en.h` into simple users.

## Risks and Edge Cases

Callers must ensure channels are allocated and indexes are valid; implementation warnings are not a safety boundary.

## Test Signals

Compile users and run channel/DIM tests described for `channels.c`.
