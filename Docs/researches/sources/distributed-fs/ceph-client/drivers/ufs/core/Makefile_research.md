# sources/distributed-fs/ceph-client/drivers/ufs/core/Makefile

## Purpose

This Makefile builds the generic UFS core module or built-in object.

## Important APIs, Types, and Functions

`ufshcd-core.o` always includes `ufshcd.o`, `ufs-sysfs.o`, `ufs-mcq.o`, and `ufs-txeq.o`. Optional objects are `ufs-rpmb.o`, `ufs-debugfs.o`, `ufs_bsg.o`, `ufshcd-crypto.o`, `ufs-fault-injection.o`, and `ufs-hwmon.o` based on their config symbols.

## Control Flow

kbuild aggregates the listed objects into `ufshcd-core.o` when `CONFIG_SCSI_UFSHCD` is enabled.

## State and Persistence Behavior

No runtime state is stored here. The file determines which runtime features and ABI entry points exist in the built driver.

## Dependencies and Integration Points

It connects Kconfig choices to actual object inclusion and keeps core UFS support centralized for host glue drivers.

## Risks and Test Signals

Risks are missing optional objects after Kconfig enablement, unconditional references to disabled features, and object-order surprises. Test signals include build coverage for each optional symbol and module load with all combinations supported by dependencies.
