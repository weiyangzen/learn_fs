# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/Makefile

## Purpose

This `Makefile` supplies a build include path for the mlx5 steering subtree.

## Important Content and Control Flow

It contains only the SPDX line and `subdir-ccflags-y += -I$(src)/..`, which adds the parent mlx5 core directory to compiler include paths for objects built in this directory and its subdirectories.

## State, Dependencies, and Integration

There is no runtime state. The build-state effect is that steering sources can include headers from `core/..` relative to their source path without every object adding its own include flag.

## Risks and Test Signals

The risk is build breakage if directory layout changes or if another Makefile stops inheriting this flag. Test by building mlx5 steering objects and checking that local includes resolve without adding broader include paths.
