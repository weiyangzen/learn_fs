# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Makefile

## Purpose
This Makefile maps Mellanox Kconfig symbols to subdirectories built by kbuild.

## Important Build Rules
- `obj-$(CONFIG_MLX4_CORE) += mlx4/`
- `obj-$(CONFIG_MLX5_CORE) += mlx5/core/`
- `obj-$(CONFIG_MLXSW_CORE) += mlxsw/`
- `obj-$(CONFIG_MLXFW) += mlxfw/`
- `obj-$(CONFIG_MLXBF_GIGE) += mlxbf_gige/`

## Control Flow
Kbuild evaluates the config-dependent object assignments and descends only into selected subtrees.

## State and Persistence
No runtime state exists. The file contributes to build graph state determined by `.config`.

## Dependencies and Integration Points
It depends on the Mellanox child directories and their local Makefiles. It connects vendor-level config symbols to concrete compilation.

## Risks and Test Signals
Risks include symbol or directory rename drift. Test signals are allmodconfig/allnoconfig builds and targeted builds for each Mellanox driver family.
