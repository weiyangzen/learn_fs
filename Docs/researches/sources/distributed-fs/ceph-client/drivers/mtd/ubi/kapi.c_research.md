# sources/distributed-fs/ceph-client/drivers/mtd/ubi/kapi.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/kapi.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/kapi.c

Purpose: this file implements the exported in-kernel UBI API used by other kernel subsystems and modules. It exposes device/volume information, volume open/close by number/name/path, logical eraseblock read/write/change/map/unmap/erase operations, MTD sync, and volume notification registration.

Important APIs, types, and functions: key exports are `ubi_get_device_info()`, `ubi_get_volume_info()`, `ubi_open_volume()`, `ubi_open_volume_nm()`, `ubi_open_volume_path()`, `ubi_close_volume()`, `ubi_leb_read()`, `ubi_leb_read_sg()`, `ubi_leb_write()`, `ubi_leb_change()`, `ubi_leb_erase()`, `ubi_leb_unmap()`, `ubi_leb_map()`, `ubi_is_mapped()`, `ubi_sync()`, `ubi_register_volume_notifier()`, and `ubi_unregister_volume_notifier()`. `struct ubi_volume_desc` carries the opened volume and mode. `ubi_get_num_by_path()` maps a character device path to UBI and volume numbers.

Control flow: open first pins the UBI device, validates mode and volume id, gets a module reference, updates reader/writer/exclusive/metaonly counters under `volumes_lock`, pins the volume device, then performs first-open static-volume CRC checking under `ckvol_mutex` unless skip-check is set. Close reverses open-mode counters and drops device/module references. Read paths share `leb_read_sanity_check()` and call EBA read helpers, marking static volumes corrupted on ECC errors. Write/change/map/unmap/erase paths reject read-only descriptors, static volumes, invalid LEB ranges, unaligned writes, and update-marker damage before delegating to EBA and WL.

State and persistence behavior: this layer maintains transient open state: reader/writer counts, `exclusive`, `metaonly`, `ref_count`, and the `checked`/`corrupted` static-volume flags. Persistent changes happen below it through EBA and WL: writes create or update LEB mappings, erases/unmaps schedule PEB erase work, atomic LEB change preserves crash consistency, and `ubi_sync()` flushes MTD caches. The notifier chain itself is in-memory state, while initial registration can synthesize `UBI_VOLUME_ADDED` notifications for existing volumes.

Dependencies and integration points: it bridges exported UBI symbols to `build.c` device reference helpers, `misc.c` static-volume checks, `eba.c` mapping operations, `wl.c` erase flushing, Linux VFS path/stat helpers, module reference counting, blocking notifier chains, and the public `<linux/mtd/ubi.h>` API.

Risks: open-mode accounting must remain balanced on every error path or volumes can become permanently busy. Notifier callbacks are documented as unable to call UBI API, so consumers must avoid reentrancy. Static-volume CRC checking on first open can be expensive and can mark a volume corrupted. `ubi_leb_unmap()` is intentionally not persistent until the physical erase finishes, so callers that need guaranteed all-FF state must use `ubi_leb_erase()` or rewrite the LEB. The path-to-device conversion depends on UBI character-device major/minor layout.

Test signals: validate mode exclusion with multiple readers, one writer, exclusive, and metaonly opens; first-open CRC checks for static volumes; update-marker operations returning `-EBADF`; dynamic-volume write alignment validation; atomic LEB changes across simulated power cuts; unmap versus erase persistence behavior; path/name open helpers; notifier delivery for existing and later volume events; and `ubi_sync()` invoking MTD sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/kapi.c -->
