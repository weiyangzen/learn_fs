# File Research: sources/block-storage/linux-dm/drivers/md/bcache/Kconfig

## Purpose
Defines bcache-specific configuration: enabling bcache, optional runtime/debug tooling, closure debugging, and asynchronous device registration.

## Main Interfaces
- `BCACHE` tristate builds the block-device cache driver and selects `CRC64`.
- `BCACHE_DEBUG` enables expensive developer checks and runtime debug controls.
- `BCACHE_CLOSURES_DEBUG` selects `DEBUG_FS` and exposes active closure state.
- `BCACHE_ASYNC_REGISTRATION` adds `/sys/fs/bcache/register_async`.

## Control Flow
All subordinate options depend on `BCACHE`. Debug closure tracking requires debugfs because the implementation exports a debugfs listing of active closures.

## Integration Points
`BCACHE` is sourced from the parent MD Kconfig and drives the bcache subdirectory Makefile. The async registration option is consumed by bcache registration/sysfs code outside this group.

## Notable Behaviors
- Bcache is described as a btree-indexed SSD-optimized cache for other block devices.
- Closure debugging is specifically for stuck asynchronous operation diagnosis.
- Asynchronous registration returns from sysfs writes before the kernel workqueue completes actual device registration.

## Risks And Review Focus
- Debug options enable expensive checks and should not be assumed free in production paths.
- Async registration changes user-visible sysfs completion semantics.
