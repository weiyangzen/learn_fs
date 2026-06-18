# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/fallback_table.c

## Purpose
`fallback_table.c` owns runtime configuration for firmware sysfs fallback and exposes sysctls under `kernel/firmware_config`.

## Important APIs, Types, And Functions
It defines exported namespace symbol `fw_fallback_config` with `force_sysfs_fallback`, `ignore_sysfs_fallback`, `loading_timeout`, and `old_timeout`. With sysctl enabled it provides `register_firmware_config_sysctl()` and `unregister_firmware_config_sysctl()`.

## Control Flow, State, And Persistence
The initial force value follows `CONFIG_FW_LOADER_USER_HELPER_FALLBACK`, and default timeout is 60 seconds. Registering creates a sysctl table for `force_sysfs_fallback` and `ignore_sysfs_fallback`, both clamped between 0 and 1. Unregistering removes the table and clears the header pointer.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include sysctl, exported symbol namespaces, and fallback/sysfs headers. It is consumed by `fallback.c` and `sysfs.c` timeout handlers. Risks include global mutable policy affecting all firmware requests, sysctl unavailable builds relying on defaults, and force/ignore precedence. Test signals include sysctl registration, min/max enforcement, forced fallback with helper enabled, ignored fallback suppressing sysfs devices, and module unload cleanup.
