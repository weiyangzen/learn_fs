# sources/distributed-fs/ceph-client/drivers/fwctl/mlx5/Makefile

## Purpose
This Kbuild file builds the mlx5 fwctl provider.

## Important Entries
`obj-$(CONFIG_FWCTL_MLX5) += mlx5_fwctl.o` and `mlx5_fwctl-y += main.o` map the provider symbol to its implementation.

## Control Flow and State
There is no runtime flow or persistent state in this file.

## Dependencies and Integration Points
The object depends on mlx5 core headers and the fwctl exported namespace.

## Risks and Test Signals
Build tests should cover modular and built-in mlx5 configurations and verify `MODULE_IMPORT_NS("FWCTL")` resolves.
