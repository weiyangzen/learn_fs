# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.h

This header defines b43 debugfs interfaces and state when `CONFIG_B43_DEBUG` is enabled, and inline no-op stubs when it is disabled. It lets the rest of b43 call debug helpers without scattering config guards.

Important declarations are `enum b43_dyndbg`, `struct b43_txstatus_log`, `struct b43_dfs_file`, `struct b43_dfsentry`, and functions `b43_debug()`, `b43_debugfs_init()`, `b43_debugfs_exit()`, `b43_debugfs_add_device()`, `b43_debugfs_remove_device()`, and `b43_debugfs_log_txstat()`. Dynamic debug features cover transmit power, DMA overflow/verbosity, periodic work, LO, firmware, keys, and verbose stats.

Enabled runtime state stores debugfs dentries, cached file buffers, next MMIO/SHM addresses, TX status log, and dynamic debug booleans. Disabled builds store no state and always return false from `b43_debug()`.

Integration points are b43 core, DMA, LO, firmware/key/debug logging, and `debugfs.c`. Risks are enabled/disabled API drift, missing `b43_dfsentry` fields for new files, and enum-index mismatch with the bool array. Test signals are successful builds with and without `CONFIG_B43_DEBUG`, no-op behavior in disabled builds, and correct allocation/free/logging in enabled builds.
