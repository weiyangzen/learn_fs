# sources/distributed-fs/ceph-client/drivers/char/ps3flash.c

## Purpose
`ps3flash.c` implements the PlayStation 3 FLASH ROM storage driver. It registers `/dev/ps3flash` as a misc device, provides user and kernel read/write access to the active flash storage region, uses the PS3 storage subsystem for sector I/O, and caches one bounce-buffer chunk with dirty writeback semantics.

## Important APIs, Types, and Functions
- `struct ps3flash_private` stores the bounce-buffer mutex, chunk size in sectors, cached start-sector tag, and dirty flag.
- `ps3flash_read_write_sectors()` delegates to `ps3stor_read_write_sectors()` using `dev->bounce_lpar`.
- `ps3flash_fetch()` writes back a dirty cached chunk if needed, reads the requested chunk, and tags it.
- `ps3flash_writeback()` writes a dirty tagged chunk to flash and clears dirty.
- `ps3flash_read()` and `ps3flash_write()` implement common user/kernel transfers over chunk boundaries.
- `ps3flash_kernel_read()`/`ps3flash_kernel_write()` back `ps3_os_area_flash_ops`; kernel writes force synchronous writeback.
- `ps3flash_interrupt()` completes asynchronous storage operations after `lv1_storage_get_async_status()`.
- `ps3flash_probe()` validates region alignment, binds the static bounce buffer, sets up PS3 storage, registers the misc device, and registers OS-area flash ops.

## Control Flow
Probe accepts only one flash device, validates region start and size are multiples of 256 KiB, configures the static bounce buffer, initializes private cache state, and registers with PS3 storage. Reads clamp to region size, compute chunk sector and offset, fetch each chunk under the private mutex, copy to user/kernel buffer, and advance. Writes fetch partial chunks or write back when replacing a full different chunk, copy into the bounce buffer, mark it dirty, and rely on flush/fsync/kernel-writeback for persistence.

## State and Persistence
The underlying flash region is persistent. Software keeps a single dirty cached chunk in the shared PS3 bounce buffer. `flush` and `fsync` call `ps3flash_writeback()`. User writes are not necessarily on flash until writeback. Global `ps3flash_dev` enforces a single device instance.

## Dependencies and Integration Points
The driver depends on PS3 system bus storage devices, LV1 hypervisor calls, `ps3stor_setup()`/teardown, the static `ps3flash_bounce_buffer`, misc core, completion-based interrupt handling, and OS-area flash registration.

## Risks
- Dirty cached data can be lost if writeback fails or is not triggered before removal/shutdown paths beyond normal file flush/fsync behavior.
- Global singleton design rejects multiple flash devices.
- Region and bounce buffer assumptions are PS3-specific and tightly coupled to platform storage.
- Flash writes are persistent firmware/storage modifications and require careful bounds and alignment behavior.

## Test Signals
Tests should validate probe alignment failures, missing bounce-buffer failure, singleton `-EBUSY`, read/write truncation at region end, dirty writeback on flush/fsync/kernel write, chunk crossing behavior, interrupt tag mismatch logging, and OS-area flash registration/unregistration.
