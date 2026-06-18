# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mlx5_core.h

## Purpose
`mlx5_core.h` is the central internal header for the mlx5 core driver. It defines logging helpers, common constants, shared command attribute structs, utility inlines, and prototypes for core lifecycle, capability, port, event, devlink, SR-IOV, scheduling, firmware, alias-object, and recovery functions used across the driver.

## Important APIs, types, and functions
Key content includes `mlx5_core_dbg/err/warn/info` logging macros, `mlx5_printk()`, `ACCESS_KEY_LEN`, `FT_ID_FT_TYPE_OFFSET`, alias/other-VHCA access structs, port/link/eeprom structs, `mlx5_flexible_inlen()`, core capability/query prototypes, command lifecycle prototypes, HCA enable/disable, health/recovery hooks, SR-IOV APIs, event APIs, auxiliary device APIs, load/unload/init prototypes, port configuration/query APIs, firmware flash/version APIs, devlink rescan helpers, SF helpers, same-hardware checks, alias-object command prototypes, EC VF vport helpers, max EQ cap helper, and PCIe congestion support helper.

## Control flow
The header has no primary runtime flow, but its inline helpers implement small control decisions: overflow-safe flexible input length calculation, devlink-rescan locking, coredev SF checks, EC VF vport mapping, maximum EQ capability fallback, and PCIe congestion event support gating.

## State and persistence behavior
No state is owned by the header. It defines how other files access and mutate state in `struct mlx5_core_dev`, cached capability arrays, PCI device fields, devlink, and firmware objects.

## Dependencies and integration points
It pulls in Linux kernel, firmware, mlx5 CQ/FS/driver, and devcom definitions. Almost every mlx5 core source file depends on it. It is also the declaration point for cross-file contracts implemented in `main.c`, port files, command files, fw reset, devlink, and alias-object handling.

## Risks and edge cases
Because this is a broad internal contract, prototype or macro changes can have large blast radius. Logging macros dereference `dev->device`, so early init code must ensure it is set. Flexible input length returns `-ENOMEM` for overflow, so callers must treat it as a negative error length. Inline capability helpers must match firmware capability layout evolution.

## Test signals
Full mlx5 build coverage is the direct signal. Runtime validation comes from lifecycle, port configuration, devlink, SR-IOV, SF, alias-object, recovery, and capability tests that exercise the declared functions. Static analysis should focus on flexible-length error handling and lifecycle lock contracts.
