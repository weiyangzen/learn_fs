# sources/distributed-fs/ceph-client/drivers/ufs/core/Kconfig

## Purpose

`core/Kconfig` defines optional features for the generic UFS host controller core.

## Important APIs, Types, and Functions

Symbols are `SCSI_UFS_BSG`, `SCSI_UFS_CRYPTO`, `SCSI_UFS_FAULT_INJECTION`, and `SCSI_UFS_HWMON`. BSG selects `BLK_DEV_BSGLIB`; crypto depends on `BLK_INLINE_ENCRYPTION`; fault injection depends on `FAULT_INJECTION`; hwmon depends on compatible `HWMON` linkage.

## Control Flow

The options are only visible after the top-level `SCSI_UFSHCD` menu is enabled. Each option controls whether its corresponding core object and public stubs compile into `ufshcd-core`.

## State and Persistence Behavior

The file affects compile-time feature presence: BSG device nodes, inline encryption keyslot support, fault injection attributes, and hwmon temperature device creation. It has no runtime state itself.

## Dependencies and Integration Points

It integrates UFS with block BSG, blk-crypto, kernel fault-injection/debugfs, and hwmon subsystems.

## Risks and Test Signals

Risks include enabling user ABI surfaces without their subsystem dependencies and mismatched built-in/module constraints. Test signals are config matrix builds and runtime checks that disabled options compile to inert inline stubs while enabled options create the expected sysfs/debugfs/device nodes.
