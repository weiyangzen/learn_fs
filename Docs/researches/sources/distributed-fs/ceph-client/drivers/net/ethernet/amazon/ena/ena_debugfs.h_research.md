# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_debugfs.h

Purpose: this header declares ENA debugfs lifecycle hooks and provides no-op stubs when debugfs support is disabled.

Important APIs, types, and functions: under `CONFIG_DEBUG_FS`, it declares `ena_debugfs_init(struct net_device *dev)` and `ena_debugfs_terminate(struct net_device *dev)`. Otherwise it defines empty static inline versions with the same signatures.

Control flow: including code can call the lifecycle hooks unconditionally. Compile-time configuration chooses real debugfs behavior or no-op behavior.

State and persistence: the header defines no state. Real state is `adapter->debugfs_base` in the netdev private structure when debugfs is enabled.

Dependencies and integration points: it includes Linux debugfs and netdevice headers plus `ena_netdev.h`, tying the hooks to ENA adapter state. It is used by the ENA netdev setup/teardown code.

Risks: because the disabled stubs silently do nothing, tests for debugfs entries must account for kernel configuration. The header includes `ena_netdev.h`, so include-order or dependency cycles need care.

Test signals: both `CONFIG_DEBUG_FS=y` and disabled builds should compile. Runtime debugfs tests should only expect entries in enabled builds; disabled builds should still probe and remove ENA devices normally.
