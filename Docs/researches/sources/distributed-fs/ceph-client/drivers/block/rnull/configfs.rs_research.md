# sources/distributed-fs/ceph-client/drivers/block/rnull/configfs.rs

## Purpose
Implements the configfs interface for the Rust null block driver. It creates the `rnull` subsystem and per-device config groups whose attributes control whether a null block disk exists and what parameters it uses.

## Important APIs, types, and functions
- `subsystem()` returns a pinned configfs subsystem with root `features` attribute and child groups of type `DeviceConfig`.
- `Config::show()` reports supported features: `blocksize,size,rotational,irqmode`.
- `Config::make_group()` initializes `DeviceConfigInner` with defaults: powered off, 4096 byte block size, non-rotational, 4096 MiB capacity, `IRQMode::None`, and group name.
- `IRQMode` supports `None` (`0`) and `Soft` (`1`) with `TryFrom<u8>` validation and `Display`.
- Device attributes: `power`, `blocksize`, `rotational`, `size`, and `irqmode`.

## Control flow
Users create a configfs group under `rnull`. Before power-on, they may change block size, rotational flag, size, and irq mode. Writing true to `power` constructs a `NullBlkDevice::new()` disk and stores it in `disk: Option<GenDisk<NullBlkDevice>>`; writing false drops the disk and powers off. Configuration attributes return `EBUSY` while powered.

## State and persistence behavior
Per-group state is protected by a Rust kernel `Mutex<DeviceConfigInner>`. The `GenDisk` object is owned by the `disk` option and destroyed by dropping it. Configfs group state lasts until userspace removes the group or the module unloads; it is not persisted across reboot/module reload.

## Dependencies and integration points
Depends on Rust-for-Linux configfs abstractions, kernel string formatting/parsing, `GenDiskBuilder::validate_block_size()`, and `NullBlkDevice::new()` from `rnull.rs`.

## Risks and test signals
- The code locks the mutex multiple times in some store paths; race behavior is still serialized, but powered checks and updates are split in a few methods.
- Capacity accepts any `u64` MiB value; very large values should be tested for builder/sector overflow behavior.
- Test configfs group creation/removal, power cycling, invalid booleans, invalid block sizes, invalid irq mode values, and attempts to mutate attributes while powered.
