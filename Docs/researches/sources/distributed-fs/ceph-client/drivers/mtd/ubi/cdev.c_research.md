# sources/distributed-fs/ceph-client/drivers/mtd/ubi/cdev.c

## Purpose
`cdev.c` implements UBI user-space character device operations. It covers per-volume devices for I/O and update operations, per-UBI devices for volume management, and the global control device for attaching/detaching MTD devices.

## Important APIs, Types, And Functions
The exported file-operation tables are `ubi_vol_cdev_operations`, `ubi_cdev_operations`, and `ubi_ctrl_cdev_operations`. Key volume operations are `vol_cdev_open()`, `vol_cdev_release()`, `vol_cdev_llseek()`, `vol_cdev_fsync()`, `vol_cdev_read()`, `vol_cdev_write()`, `vol_cdev_direct_write()`, and `vol_cdev_ioctl()`. Management helpers include `get_exclusive()`, `revoke_exclusive()`, `verify_mkvol_req()`, `verify_rsvol_req()`, `rename_volumes()`, `ubi_get_ec_info()`, `ubi_cdev_ioctl()`, and `ctrl_cdev_ioctl()`.

## Control Flow
Volume open maps inode major/minor to UBI device and volume ID, then opens the volume read-only or read-write. Release cancels incomplete update or atomic LEB change state, frees update buffers, and closes the volume descriptor.

Reads reject active updates and damaged update-marker volumes, clamp to `used_bytes`, allocate an aligned temporary buffer, translate file offsets into LEB numbers/offsets, and call `ubi_eba_read_leb()` in chunks. Direct writes are allowed only when the volume property `direct_writes` is enabled, reject static volumes, require minimum-I/O alignment, clamp to volume size, and call `ubi_eba_write_leb()`. Normal writes during `UBI_IOCVOLUP` or `UBI_IOCEBCH` feed update data through `ubi_more_update_data()` or `ubi_more_leb_change_data()`, then verify static-volume contents and notify `UBI_VOLUME_UPDATED` when complete.

`vol_cdev_ioctl()` implements volume update, atomic LEB change, erase/map/unmap/is-mapped, direct-write property, and ubiblock create/remove ioctls. `ubi_cdev_ioctl()` requires `CAP_SYS_RESOURCE` and creates/removes/resizes/renames volumes, triggers PEB bitflip scrub checks, and returns erase-counter ranges. `ctrl_cdev_ioctl()` attaches or detaches MTD devices by calling the build-layer attach/detach functions under `ubi_devices_mutex`.

## State And Persistence
The file manipulates descriptor modes and per-volume counters (`readers`, `writers`, `exclusive`, `metaonly`) under `volumes_lock`. Update state (`updating`, `changing_leb`, `upd_buf`, `upd_received`, `upd_bytes`) is transient but controls persistent writes to volume data. Volume creation, removal, resize, rename, update completion, LEB erase/map/unmap, and ubiblock create/remove all produce persistent or externally visible state through lower UBI layers. `ubi_get_ec_info()` exposes WL erase-counter state from `lookuptbl`.

## Dependencies And Integration Points
The ABI is defined by `<mtd/ubi-user.h>` ioctls and structs. The file depends on volume open/close APIs, EBA read/write/unmap, volume update/rename/create/remove/resize functions, WL flush and bitflip scrub checks, ubiblock, MTD device acquisition, and Linux user-copy/capability/compat ioctl helpers.

## Risks
The exclusive-mode transitions are central: update and atomic LEB change require a single opener and must revoke exclusive access on every completion/cancel path. Direct writes bypass the normal volume update protocol, so alignment and dynamic-volume checks are important. User request validation must prevent unterminated names, duplicate rename entries, invalid IDs, negative byte counts, overflow in erase-counter range handling, and unauthorized changes. Release marks interrupted updates as damaged, so incomplete writes are deliberately persistent error state.

## Test Signals
Exercise ioctl validation and permission failures, partial update release behavior, zero-byte update notification, static-volume CRC checking after update, atomic LEB change cancellation, direct-write alignment errors, rename collision/removal cases, attach/detach through `/dev/ubi_ctrl`, and `UBI_IOCECNFO` ranges including bad PEBs and overflow.
