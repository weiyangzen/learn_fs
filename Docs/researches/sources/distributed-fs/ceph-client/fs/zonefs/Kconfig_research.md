# sources/distributed-fs/ceph-client/fs/zonefs/Kconfig

## Purpose
`fs/zonefs/Kconfig` declares the kernel configuration option for building zonefs, a simple filesystem that exposes zones of a zoned block device as files.

## Important APIs, types, and functions
It defines `CONFIG_ZONEFS_FS` as a tristate option named "zonefs filesystem support". It depends on `BLOCK` and `BLK_DEV_ZONED`, and selects `FS_IOMAP` and `CRC32`.

## Control flow
Kconfig controls whether `fs/zonefs` is omitted, built in, or built as a module. Selecting the option ensures iomap helpers and CRC32 support are present for file IO and superblock checksum validation.

## State and persistence
No runtime state exists here. The selected config determines whether zonefs can mount on-disk zonefs-formatted zoned devices.

## Dependencies and integration points
It integrates zonefs into the kernel filesystem build menu and expresses hard dependencies on zoned block device infrastructure.

## Risks and test signals
Risks are missing dependencies when source files use iomap or CRC helpers, or accidental enablement without zoned block support. Test signals include allmodconfig, built-in, module, and dependency-disabled builds.
