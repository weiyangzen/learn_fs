# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/reporter_vnic.h

## Purpose

`reporter_vnic.h` declares the vNIC health reporter lifecycle and shared counter-diagnose helper.

## Important APIs, Types, and Functions

- `mlx5_reporter_vnic_create()` creates the devlink health reporter.
- `mlx5_reporter_vnic_destroy()` destroys it if present.
- `mlx5_reporter_vnic_diagnose_counters()` writes vNIC environment counters for a selected vport to a devlink fmsg.

## Control Flow

Core health setup includes this header to create/destroy the reporter. Other health reporters can call the counter helper to include vNIC counters in their own diagnostics.

## State and Persistence Behavior

The header has no storage. Implementations mutate `dev->priv.health.vnic_reporter` and sample firmware counters.

## Dependencies and Integration Points

Depends on `mlx5_core.h` and devlink fmsg types. It integrates core health diagnostics with vNIC/environment counter reporting.

## Risks and Edge Cases

Callers must pass a valid `devlink_fmsg`, vport number, and correct `other_vport` flag. Reporter creation can fail and is represented as an error pointer in health state.

## Test Signals

Compile all health reporter users and run devlink health diagnose paths with and without the vNIC reporter present.
