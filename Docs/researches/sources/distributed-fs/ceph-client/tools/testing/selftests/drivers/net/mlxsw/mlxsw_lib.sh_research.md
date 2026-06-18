# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/mlxsw_lib.sh

## Purpose

Shared mlxsw-specific helper library for Spectrum revision gating and descriptor limits.

## Important APIs, Types, and Functions

Initializes `MLXSW_CHIP` from `devlink dev info`, derives `MLXSW_SPECTRUM_REV`, and exports `mlxsw_on_spectrum`, `__mlxsw_only_on_spectrum`, `mlxsw_only_on_spectrum`, and `mlxsw_max_descriptors_get`. It integrates with kselftest logging through `log_test_xfail`.

## Control Flow

When sourced, the file detects the running mlxsw driver/revision. Tests can call `mlxsw_only_on_spectrum` with revisions such as `2` or `3+` to xfail unsupported hardware, or call `mlxsw_max_descriptors_get` to obtain expected descriptor-pool sizes per Spectrum generation.

## State and Persistence Behavior

State is shell-global: `MLXSW_CHIP` and `MLXSW_SPECTRUM_REV` variables. It performs no persistent device changes.

## Dependencies and Integration Points

Depends on `$DEVLINK_DEV`, `devlink -j`, `jq`, bash arithmetic, and the caller's test logging functions.

## Risks and Edge Cases

Unknown driver strings or new Spectrum revisions cause stderr messages or failures until the mapping is updated. Because it exits on missing devlink info during sourcing, callers need a valid devlink-capable mlxsw device.

## Test Signals

Signals are correct revision comparison, xfail logging on unsupported hardware, and descriptor constants matching firmware/hardware expectations.
