# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.h

## Purpose
Declares IOSM debugfs init/deinit hooks and provides no-op stubs when WWAN debugfs support is disabled.

## Important APIs, Types, And Functions
Exports `ipc_debugfs_init(struct iosm_imem *)` and `ipc_debugfs_deinit(struct iosm_imem *)` under `CONFIG_WWAN_DEBUGFS`; otherwise defines static inline empty stubs.

## Control Flow
Compile-time selection lets IOSM core call debugfs hooks unconditionally without linking debugfs objects in non-debugfs builds.

## State And Persistence
No state in the header. Enabled implementation stores state in `struct iosm_imem`.

## Dependencies And Integration Points
Relies on a forward-visible `struct iosm_imem` from including C files. Coupled with `iosm/Makefile`, which only adds debugfs/trace objects under `CONFIG_WWAN_DEBUGFS`.

## Risks
Stub signatures must stay identical to enabled declarations. Any caller requiring trace side effects must be guarded by the same config or tolerate no-ops.

## Test Signals
Build IOSM with `CONFIG_WWAN_DEBUGFS=y` and `n`, ensuring no unresolved symbols and no unused-function issues.
