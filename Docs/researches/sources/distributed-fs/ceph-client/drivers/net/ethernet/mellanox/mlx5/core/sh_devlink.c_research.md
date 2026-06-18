# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.c

## Purpose

`sh_devlink.c` creates a shared devlink instance for mlx5 PF devices that expose a usable serial number in PCI VPD. The shared devlink groups related devices by serial number through the kernel devlink shared-device facility.

## Important APIs and Functions

`mlx5_shd_init()` reads PCI VPD, extracts the `V3` keyword or falls back to the standard serial-number keyword, strips trailing space-delimited firmware padding, and calls `devlink_shd_get()` with empty `mlx5_shd_ops`. `mlx5_shd_uninit()` releases the shared devlink with `devlink_shd_put()` if one was acquired.

## Control Flow

Only PF devices participate. VPD absence returns success, while other VPD allocation errors propagate. Missing serial keywords also return success because shared devlink is optional. A valid keyword is duplicated, trimmed at the first space, used to get/create the shared devlink, freed, and stored in `dev->shd`.

## State and Persistence Behavior

The only driver state is `dev->shd`. The shared devlink object is reference-counted by devlink core and keyed by serial number. No mlx5-specific devlink operations are registered in this file.

## Dependencies and Integration Points

It depends on PCI VPD helpers, devlink shared-device APIs, PF detection, and `dev->pdev`. It integrates with mlx5 core init/uninit ordering and any user tooling that observes shared devlink topology.

## Risks and Test Signals

Serial parsing stops at the first space; if a legitimate serial contains spaces, grouping may truncate. VPD `V3` and legacy SN fallback should be tested on old and new adapters. Verify PF-only behavior, VPD `-ENODEV` tolerance, shared devlink refcount release, and no leak when allocation or `devlink_shd_get()` fails.
