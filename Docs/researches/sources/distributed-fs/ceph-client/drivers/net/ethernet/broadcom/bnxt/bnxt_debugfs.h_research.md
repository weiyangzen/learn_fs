# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_debugfs.h

Purpose: Declares the bnxt debugfs lifecycle hooks and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled.

Important APIs, types, and functions: Exposes `bnxt_debug_init()`, `bnxt_debug_exit()`, `bnxt_debug_dev_init()`, and `bnxt_debug_dev_exit()` as real prototypes under `CONFIG_DEBUG_FS` and static inline empty functions otherwise.

Control flow: There is no runtime flow in the header beyond compile-time selection. Driver init/remove and device probe/remove paths can call these hooks unconditionally because the header supplies stubs for non-debugfs builds.

State and persistence behavior: The header does not define state. State is owned by `bnxt_debugfs.c` through debugfs dentries when compiled in.

Dependencies and integration points: It includes Broadcom HSI and `bnxt.h` so `struct bnxt` is available for device-level hooks. It integrates the optional debugfs implementation with the always-built driver lifecycle.

Risks: Since stubs silently do nothing, tests for debugfs behavior must ensure the config option is enabled. Including broad headers from a small interface can increase compile coupling.

Test signals: Compile both `CONFIG_DEBUG_FS=y` and `n`, verify call sites need no ifdefs, and confirm no unresolved symbols or dead references when debugfs is disabled.
