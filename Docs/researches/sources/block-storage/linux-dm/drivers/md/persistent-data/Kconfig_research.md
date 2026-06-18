# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/Kconfig

## Purpose
Kconfig entry for the device-mapper persistent-data metadata library.

## Main Definition
- `config DM_PERSISTENT_DATA`
  - Type: `tristate`
  - Depends on: `BLK_DEV_DM`
  - Selects: `LIBCRC32C`, `DM_BUFIO`
  - Help text describes it as an immutable on-disk data structure support library for device-mapper targets, especially thin provisioning.

## Role in Repository
This controls whether the persistent-data library is built into the kernel, as a module, or omitted. The selected dependencies match the implementation: checksums use CRC32C, and block caching/locking is built on `dm-bufio`.
