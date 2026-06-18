# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_dbgfs.h

## Purpose
This header declares QAT debugfs lifecycle hooks and provides no-op stubs when `CONFIG_DEBUG_FS` is disabled.

## Important APIs, Types, And Functions
APIs are `adf_dbgfs_init()`, `adf_dbgfs_add()`, `adf_dbgfs_rm()`, and `adf_dbgfs_exit()`. In non-debugfs builds, static inline stubs do nothing.

## Control Flow
The header controls build-time flow: callers can invoke debugfs hooks unconditionally while compiled code either performs debugfs operations or no-ops.

## State And Persistence Behavior
No state is stored here. Runtime state is in `adf_dbgfs.c` and feature-specific debugfs modules.

## Dependencies And Integration Points
It integrates PCI drivers and common lifecycle code with optional debugfs support.

## Risks
The stubs mean tests must cover both debugfs-enabled and disabled builds. Function signatures must remain identical across branches.

## Test Signals
Build with and without `CONFIG_DEBUG_FS`, probe devices, and confirm debugfs files exist only in enabled builds while probe still succeeds in disabled builds.
