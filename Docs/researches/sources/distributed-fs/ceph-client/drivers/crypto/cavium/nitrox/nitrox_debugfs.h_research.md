# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.h

Purpose: declares or stubs NITROX debugfs lifecycle helpers.

Important APIs and control flow: when `CONFIG_DEBUG_FS` is enabled, `nitrox_debugfs_init()` and `nitrox_debugfs_exit()` are external functions. Otherwise, static inline no-op stubs preserve caller code without conditional compilation.

State and dependencies: owns no state; it depends on `nitrox_dev.h` for the device type and on build-time `CONFIG_DEBUG_FS`.

Integration points: main PCI/device code can call debugfs init/exit unconditionally.

Risks and test signals: risks are low but include callers assuming debugfs files exist when stubs are compiled. Test signals include builds with DEBUG_FS on/off and teardown paths invoking exit safely in both configurations.
