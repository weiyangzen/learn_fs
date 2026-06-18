# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.c

## Purpose
Initializes and tears down IOSM debugfs integration under the WWAN debugfs directory, including trace channel setup.

## Important APIs, Types, And Functions
Exports `ipc_debugfs_init()` and `ipc_debugfs_deinit()`. Init calls `wwan_get_debugfs_dir()`, creates a module-named debugfs directory, starts trace support with `ipc_trace_init()`, and warns on trace setup failure. Deinit calls `ipc_trace_deinit()`, removes the debugfs directory recursively, and releases the WWAN debugfs dir reference.

## Control Flow
Called by IOSM device setup/teardown when compiled with `CONFIG_WWAN_DEBUGFS`. Trace initialization happens after debugfs directory creation; teardown reverses trace and directory ownership.

## State And Persistence
Stores debugfs directory dentries and trace pointer in `struct iosm_imem`. Debugfs entries persist until device teardown or module unload.

## Dependencies And Integration Points
Depends on Linux debugfs, WWAN debugfs helpers, IOSM IMEM state, and IOSM trace support.

## Risks
The code does not check `debugfs_create_dir()` failure before trace init. Deinit assumes init either populated or safely left nullable fields acceptable to trace/debugfs cleanup helpers.

## Test Signals
Build/run with `CONFIG_WWAN_DEBUGFS`, inspect `debugfs/wwan/wwanX/<module>`, verify trace channel creation, then unplug/unload and confirm recursive removal and WWAN debugfs ref release.
