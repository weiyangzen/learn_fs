# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Kconfig

## Purpose
This Kconfig entry exposes the VDO device-mapper target, described as a deduplication, compression, and thin-provisioning target.

## Important APIs, Types, And Functions
- `config DM_VDO` is a tristate option named `VDO: deduplication and compression target`.
- It depends on `64BIT` and `BLK_DEV_DM`.
- It selects `DM_BUFIO`, `LZ4_COMPRESS`, `LZ4_DECOMPRESS`, and `MIN_HEAP`.

## Control Flow
The build system includes the VDO target only when this option is enabled as built-in or module. If built as a module, the help text states the module name is `dm-vdo`.

## State And Persistence Behavior
Kconfig stores build-time selection only. Runtime VDO state is implemented by the C files included by the Makefile.

## Dependencies And Integration Points
The entry integrates VDO into the kernel configuration graph and ensures required compression, decompression, buffer I/O, and heap helpers are selected with the target.

## Risks
- VDO is unavailable on non-64-bit builds.
- Missing or incorrect selected dependencies would surface as build or link failures in the VDO object set.

## Test Signals
Build `DM_VDO=n`, `m`, and `y` where supported; verify dependency selection, module name, and that VDO object compilation follows the selected state.
