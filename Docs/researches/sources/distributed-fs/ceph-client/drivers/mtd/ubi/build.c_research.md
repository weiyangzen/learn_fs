# sources/distributed-fs/ceph-client/drivers/mtd/ubi/build.c

## Purpose
`build.c` owns UBI module/device construction and teardown. It registers the UBI class, control misc device, debugfs root, ubiblock integration, and MTD notifier; parses `mtd=` boot/module parameters; attaches selected MTD devices as `struct ubi_device`; exposes sysfs device attributes; and detaches devices cleanly.

## Important APIs, Types, And Functions
`struct mtd_dev_param` stores parsed attach parameters: MTD name/path/number, requested UBI number, VID header offset, bad-block reserve policy, fastmap enable flag, and fastmap pool reservation flag. Global state includes `ubi_devices[]`, `ubi_devices_mutex`, `ubi_devices_lock`, `ubi_wl_entry_slab`, and optional `fm_autoconvert`/`fm_debug`.

Public integration functions include `ubi_attach_mtd_dev()`, `ubi_detach_mtd_dev()`, `ubi_get_device()`, `ubi_put_device()`, `ubi_get_by_major()`, `ubi_major2num()`, `ubi_volume_notify()`, `ubi_notify_all()`, and `ubi_enumerate_volumes()`. Initialization flows through `ubi_init()` and, depending on module/built-in mode, `ubi_init_attach()`. Helpers include `io_init()`, `uif_init()`, `uif_close()`, `autoresize()`, `open_mtd_device()`, `ubi_notify_add()`, and `ubi_mtd_param_parse()`.

## Control Flow
`ubi_init()` validates on-flash header sizes, registers sysfs class and `/dev/ubi_ctrl`, creates the WL slab, initializes debugfs and ubiblock, registers the MTD notifier, then optionally attaches configured MTDs. `ubi_init_attach()` opens each configured MTD and calls `ubi_attach_mtd_dev()`, detaching already attached devices on module-mode failure.

`ubi_attach_mtd_dev()` is serialized by `ubi_devices_mutex`. It rejects duplicate MTDs, gluebi-recursive MTDs, unsupported MLC NAND without SLC emulation, and zero erasesize devices; allocates a UBI number; initializes `struct ubi_device`; configures fastmap pool sizing and debug checking; runs `io_init()`; allocates PEB/fastmap buffers; performs `ubi_attach()`; handles autoresize; builds character devices and volume devices via `uif_init()`; creates per-device debugfs; starts the background thread; enables WL work; publishes `ubi_devices[ubi_num]`; and emits volume-added notifications.

`ubi_detach_mtd_dev()` obtains and removes the device from the global registry, marks it dead, sends shutdown/removed notifications, updates fastmap before shutdown unless fastmap checking is enabled, stops background work, removes debugfs/user interfaces, closes WL, frees internal volumes/tables/buffers, drops the MTD reference, and releases the device.

## State And Persistence
Persistent state is on flash: EC/VID layout, volume table, EBA mappings, erase counters, and fastmap. In-memory state includes global device registry, per-device locks, volumes, WL state, sysfs/debugfs/cdev objects, buffers, and fastmap pools. `io_init()` derives physical geometry and offsets from MTD properties and may force read-only mode when headers share a minimum I/O unit or the MTD is not writable. `autoresize()` clears `UBI_VTBL_AUTORESIZE_FLG` and persists volume table changes through resize or record update. Fastmap is persisted on volume add/remove/resize/rename notifications and on detach.

## Dependencies And Integration Points
This file integrates with MTD (`get_mtd_device*`, `mtd_div_by_eb`, device-tree compatible `"linux,ubi"`), Linux cdev/sysfs/miscdevice/kthread APIs, debugfs, ubiblock, UBI attach/WL/EBA/volume-management subsystems, notifier chains, and module parameters. `ubi_notify_add()` auto-attaches compatible MTDs discovered by the MTD notifier.

## Risks
Attach/detach ordering is safety-critical: publishing `ubi_devices[]` happens only after successful setup, and teardown must prevent new references before freeing resources. Refcount accounting uses both `ubi_get_device()` and direct adjustment in detach; mistakes can leave busy devices freed or undeletable. Geometry checks protect against invalid VID/data offsets and out-of-bounds VID buffers. Fastmap update failure is logged rather than fatal in some notification paths, so recovery depends on later full attach scanning or invalidation logic. Module-vs-built-in error handling intentionally differs and can hide attach failures during boot.

## Test Signals
Useful signals include successful class/control device registration, `mtd=` parser rejection of malformed fields, attach failure unwinding without leaked cdev/debugfs/MTD refs, duplicate attach rejection, read-only attach on write-protected MTD, autoresize clearing the flag on flash, fastmap update on detach, and notifier-created add events for compatible MTD device-tree nodes.
