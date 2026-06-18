# sources/distributed-fs/ceph-client/drivers/mtd/ubi/gluebi.c

## Purpose
`gluebi.c` provides an MTD emulation layer over UBI volumes. It lets legacy MTD-oriented software access UBI volumes as fake `MTD_UBIVOLUME` devices whose eraseblock size is the UBI logical eraseblock size.

## Important APIs, Types, And Functions
`struct gluebi_device` embeds `struct mtd_info` plus a UBI volume descriptor, UBI/volume IDs, reference count, and list node. Global state is `gluebi_devices` protected by `devices_mutex`. Main functions are `find_gluebi_nolock()`, `gluebi_get_device()`, `gluebi_put_device()`, `gluebi_read()`, `gluebi_write()`, `gluebi_erase()`, `gluebi_create()`, `gluebi_remove()`, `gluebi_updated()`, `gluebi_resized()`, `gluebi_notify()`, `ubi_gluebi_init()`, and `ubi_gluebi_exit()`.

## Control Flow
Module init registers a UBI volume notifier. On `UBI_VOLUME_ADDED`, `gluebi_create()` allocates a gluebi object, duplicates the volume name for `mtd->name`, fills MTD geometry and operation callbacks, sets writable flags when UBI is not read-only, sizes dynamic volumes by reserved LEBs and static volumes by used bytes, registers the MTD device, then adds it to the gluebi list. On remove, `gluebi_remove()` refuses busy devices, unregisters the MTD device, and frees memory. Resize/update notifications adjust exposed MTD size, with static volume update using `used_bytes`.

MTD open calls `gluebi_get_device()`, which opens the backing UBI volume on the first reference and only increments a gluebi refcount for later MTD opens because MTD does not distinguish UBI open modes. Read/write translate absolute MTD offsets into LEB number and offset and loop over `ubi_read()` or `ubi_leb_write()`. Erase unmaps all but the last LEB and uses synchronous `ubi_leb_erase()` for the final block so MTD erase completion semantics are satisfied.

## State And Persistence
Gluebi state is transient list/refcount/device registration state. Persistent effects occur through backing UBI operations: writes map/write LEB data, erase unmaps or erases LEBs, and UBI volume updates/resizes change MTD-visible size. Removing a gluebi device does not delete the UBI volume; it removes only the emulated MTD surface.

## Dependencies And Integration Points
The file integrates with the public UBI volume notifier API, UBI volume open/read/write/erase functions from `<linux/mtd/ubi.h>`, Linux MTD core registration, and `ubi-media.h` constants. It also interacts with `build.c` because `ubi_attach_mtd_dev()` refuses attaching `MTD_UBIVOLUME` devices, preventing recursion.

## Risks
The single UBI descriptor per gluebi device means mixed MTD readers/writers are collapsed into one UBI open mode chosen at first open. Removal refuses busy devices, but module exit unregisters all remaining devices and logs unregister errors while continuing. Erase failure reports `fail_addr` as the start of the failed logical block. Write and erase alignment must match MTD writesize/erasesize or the backing UBI calls may be invalid.

## Test Signals
Test notifier enumeration creating MTD devices for existing UBI volumes, dynamic vs static size reporting, read/write spanning LEB boundaries, alignment rejection, erase completing synchronously, busy remove returning `-EBUSY`, size updates after static volume update and resize, and refusal to attach gluebi MTD devices back into UBI.
