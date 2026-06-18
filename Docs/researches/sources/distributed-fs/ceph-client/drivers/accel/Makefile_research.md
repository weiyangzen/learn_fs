# sources/distributed-fs/ceph-client/drivers/accel/Makefile

## Purpose
This kbuild file maps accelerator driver Kconfig symbols to vendor subdirectories.

## Important APIs, Types, And Functions
The key entries are `obj-$(CONFIG_DRM_ACCEL_AMDXDNA) += amdxdna/` plus corresponding entries for Arm Ethos-U, habanalabs, IVPU, QAIC, and Rocket. There is no runtime code.

## Control Flow
kbuild descends only into directories whose config symbols are enabled. The parent `drivers/Makefile` includes this directory when `CONFIG_DRM_ACCEL` is enabled.

## State, Dependencies, Integration, Risks, And Tests
State is the build graph derived from `.config`. Integration risk is direct: a wrong symbol or path silently excludes an accelerator driver from builds. Test signals are allmodconfig coverage, per-driver `M=drivers/accel/<driver>` builds, and checking that `CONFIG_DRM_ACCEL_AMDXDNA=m` produces `amdxdna.ko`.
