# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/Makefile

## Purpose

This HWS `Makefile` supplies a parent-directory include path for hardware steering sources.

## Important Content and Control Flow

It contains only the SPDX line and `subdir-ccflags-y += -I$(src)/..`, adding `core/steering` as an include root for HWS compilation units.

## State, Dependencies, and Integration

There is no runtime state. The build integration allows HWS files to include neighboring steering headers without object-specific include flags.

## Risks and Test Signals

The risk is compile failure if HWS headers move or if subdirectory flag inheritance changes. Test by building the HWS steering objects under relevant mlx5 Kconfig options.
