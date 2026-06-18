# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_bsg.h

## Purpose

This header declares the UFS BSG device setup/teardown interface and provides disabled stubs.

## Important APIs, Types, and Functions

It forward-declares `struct ufs_hba` and declares `ufs_bsg_probe()` and `ufs_bsg_remove()` under `CONFIG_SCSI_UFS_BSG`.

## Control Flow

There is no runtime control flow. Compile-time configuration selects real hooks or stubs that return success/do nothing.

## State and Persistence Behavior

No state is owned by the header.

## Dependencies and Integration Points

It lets core probe/remove code call BSG support unconditionally while keeping BSG optional.

## Risks and Test Signals

Risks are signature drift and callers assuming a bsg node exists when the config is disabled. Test signals are builds and probe/remove paths with BSG enabled and disabled.
