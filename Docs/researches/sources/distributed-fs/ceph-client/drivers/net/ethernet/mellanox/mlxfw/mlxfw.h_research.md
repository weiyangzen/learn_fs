# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxfw/mlxfw.h

## Purpose
`mlxfw.h` is the public in-kernel interface for the Mellanox firmware flash library. It defines the device wrapper, firmware FSM states and errors, reactivation statuses, device operation callbacks, logging helpers, and the `mlxfw_firmware_flash()` entry point.

## Important APIs, Types, and Functions
Important types are `struct mlxfw_dev`, `enum mlxfw_fsm_state`, `enum mlxfw_fsm_state_err`, `enum mlxfw_fsm_reactivate_status`, and `struct mlxfw_dev_ops`. Operations include component query/update, FSM lock/query/cancel/release, block download, component verify, activate, and optional reactivate. `mlxfw_dev_dev()` maps devlink to device for logging.

## Control Flow and State
The header has no direct runtime flow, but it defines the callback contract used by `mlxfw_fsm.c`. If `CONFIG_MLXFW` is not reachable, `mlxfw_firmware_flash()` is an inline `-EOPNOTSUPP` stub. State is caller-owned in `struct mlxfw_dev`: PSID identity, PSID size, devlink pointer, and operations table.

## Dependencies and Integration Points
It depends on Linux firmware, netlink extack, device, and devlink APIs. It is consumed by mlxsw and any device driver that delegates firmware flashing to mlxfw.

## Risks and Test Signals
Risks include callback contract drift, missing operation implementations, wrong PSID length, and callers not handling the stub case. Test signals are build coverage with reachable/unreachable `CONFIG_MLXFW`, devlink flash invocation, callback error propagation, and compile-time use of all enum values by device implementations.
