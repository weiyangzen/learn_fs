# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/Kconfig

## Purpose
This Kconfig file gates Mellanox Ethernet/RDMA networking drivers behind the `NET_VENDOR_MELLANOX` vendor option and includes the Kconfig files for mlx4, mlx5, mlxsw, mlxfw, and mlxbf_gige.

## Important Configuration
- `NET_VENDOR_MELLANOX` is a bool defaulting to `y`, dependent on `PCI || I2C`.
- The `if NET_VENDOR_MELLANOX` block controls visibility of all sourced Mellanox subdriver options.

## Control Flow
Kconfig evaluation exposes or hides the nested driver menus. The option itself does not directly build code; it allows selection of specific Mellanox drivers.

## State and Persistence
The persistent output is kernel configuration state in `.config`, which determines which Makefile objects are later compiled.

## Dependencies and Integration Points
It integrates with the top-level Ethernet vendor menu and delegates actual driver options to child Kconfig files.

## Risks and Test Signals
Risk is mainly accidental menu invisibility if dependencies or source paths drift. Test signals are `make menuconfig` visibility, `olddefconfig`, and builds with Mellanox vendor disabled or enabled.
