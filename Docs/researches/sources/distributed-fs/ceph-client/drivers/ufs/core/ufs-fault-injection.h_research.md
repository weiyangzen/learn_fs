# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs-fault-injection.h

## Purpose

This header defines the compile-time contract for UFS fault injection.

## Important APIs, Types, and Functions

It declares `ufs_fault_inject_hba_init()`, `ufs_trigger_eh()`, and `ufs_fail_completion()` when enabled, and inline no-op/false stubs otherwise.

## Control Flow

No runtime control flow is present. `CONFIG_SCSI_UFS_FAULT_INJECTION` selects real hooks.

## State and Persistence Behavior

The header owns no state and lets core code call fault-injection hooks unconditionally.

## Dependencies and Integration Points

It depends on `linux/kconfig.h`, `linux/types.h`, and a forward declaration of `struct ufs_hba`.

## Risks and Test Signals

Risks are mismatched stub semantics and accidental build dependencies on fault-injection internals. Test signals are compile coverage for enabled and disabled configurations.
