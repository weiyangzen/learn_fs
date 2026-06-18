# Research: subset-b-004303

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/io.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/io.c

Purpose: this file is the UBI physical I/O layer over MTD. It normalizes reads, writes, erases, bad-block operations, EC header access, VID header access, and debug self-checking for the rest of UBI. It is deliberately paranoid: every header read from flash is CRC checked and semantically validated, writes are checked against erased flash assumptions, and debug modes can emulate bitflips, power cuts, all-FF reads, ECC errors, and write/erase failures.

Important APIs, types, and functions: exported entry points include `ubi_io_read()`, `ubi_io_write()`, `ubi_io_sync_erase()`, `ubi_io_is_bad()`, `ubi_io_mark_bad()`, `ubi_io_read_ec_hdr()`, `ubi_io_write_ec_hdr()`, `ubi_io_read_vid_hdr()`, `ubi_io_write_vid_hdr()`, and `ubi_self_check_all_ff()`. Internal helpers include `validate_ec_hdr()`, `validate_vid_hdr()`, `do_sync_erase()`, `torture_peb()`, `nor_erase_prepare()`, and self-check routines for bad PEBs, EC/VID headers, and post-write verification. `struct ubi_vid_io_buf` from `ubi.h` is central because VID headers can be unaligned inside an aligned MTD write buffer.

Control flow: generic reads call `mtd_read()` with retry handling and translate MTD bitflip/ECC results into UBI-specific status codes. Writes reject read-only mode, require header-min-I/O alignment, check that the target range is all `0xFF`, optionally validate existing EC/VID headers for data-area writes, call `mtd_write()`, verify written bytes in debug mode, and confirm the remaining PEB tail is still erased. Erases optionally invalidate NOR EC/VID magic first, optionally torture the PEB with test patterns, then call MTD erase, verify all-FF, and return the number of erase cycles performed. Header read paths read aligned EC/VID storage, check magic, all-FF state, CRC, semantic constraints, and debug fault injection. Header write paths fill magic/version/offset/CRC fields and then delegate to `ubi_io_write()`.

State and persistence behavior: this file persists EC headers, VID headers, data area bytes, bad-block marks, and erase counters through MTD. It also updates no long-lived in-memory state except through `ubi_ro_mode()` on emulated power cuts or failures reported upward. EC headers record `ubi->image_seq`, VID/data offsets, and erase counters; VID headers carry volume identity, LEB number, copy flag, sequence number, data length/CRC, and compatibility semantics.

Dependencies and integration points: it depends on MTD primitives (`mtd_read`, `mtd_write`, `mtd_erase`, `mtd_block_isbad`, `mtd_block_markbad`), Linux CRC32, UBI media structs from `ubi-media.h`, debug controls from `debug.h` via `ubi.h`, and helper state in `struct ubi_device` such as `peb_size`, `leb_start`, `vid_hdr_shift`, and min I/O sizes. Higher layers use this file through EBA, attach, volume table, and wear-leveling code.

Risks: the status-code distinctions are subtle: callers must preserve differences between empty flash, bad headers, bad headers with ECC errors, and correctable bitflips. VID header unaligned-buffer handling is easy to break if callers bypass `ubi_vid_io_buf`. Debug self-checks allocate large buffers and read back whole regions, so they are expensive but valuable. NOR erase preparation writes zeros to magic fields before erasing and has power-cut ordering assumptions. Incorrect MTD drivers that report success without filling buffers are mitigated but still a core risk.

Test signals: useful signals are successful attach across empty, valid, and corrupted images; correct classification of `UBI_IO_FF`, `UBI_IO_BAD_HDR`, `UBI_IO_BAD_HDR_EBADMSG`, and `UBI_IO_BITFLIPS`; EC/VID CRC failures being rejected; bitflips causing scrub paths later; write failures switching or propagating safely; NOR interrupted-erase recovery; bad-block mark behavior on NAND; and debugfs fault injection exercising all emulated branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/io.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/misc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/misc.c

Purpose: this file collects small UBI-wide helpers for data-length trimming, static-volume verification, bad-eraseblock reserve accounting, byte-pattern checking, and standardized UBI log messages.

Important APIs, types, and functions: `ubi_calc_data_len()` trims trailing `0xFF` data and aligns the result to `ubi->min_io_size`. `ubi_check_volume()` fully reads a static volume through `ubi_eba_read_leb()` to verify per-LEB CRCs. `ubi_update_reserved()` and `ubi_calculate_reserved()` manage bad-eraseblock reserve targets. `ubi_check_pattern()` tests a buffer for one byte value. `ubi_msg()`, `ubi_warn()`, and `ubi_err()` format per-device kernel messages and include caller information for warnings/errors.

Control flow: data trimming scans backward to the last non-`0xFF` byte and rounds up. Static volume checking allocates one usable-LEB buffer, loops across `used_ebs`, uses `last_eb_bytes` for the final LEB, reads with CRC checking enabled, returns `1` for ECC/data corruption, and propagates negative errors. Reserve calculation derives the required reserve level from the configured bad PEB limit minus current bad count; reserve update moves available PEBs into reserved accounting under the caller's `volumes_lock`.

State and persistence behavior: reserve helpers update in-memory `ubi_device` accounting (`avail_pebs`, `rsvd_pebs`, `beb_rsvd_pebs`, `beb_rsvd_level`) but do not write flash directly. Static volume checking can cause callers to mark `vol->corrupted`, but the helper itself only reads. Logging has no persistence beyond kernel logs.

Dependencies and integration points: these helpers are used from API open paths, volume update/write code, wear-leveling bad-block handling, and IO/debug checks. They depend on EBA reads, vmalloc/vfree, MTD ECC classification helpers, alignment fields from `struct ubi_device`, and kernel printk formatting.

Risks: `ubi_calc_data_len()` assumes input length is min-I/O aligned. Static-volume checking can be slow for large volumes and allocates a full usable LEB. Reserve updates depend on callers holding `volumes_lock`; missing that lock would corrupt global accounting. Returning positive `1` for corruption is a special convention callers must not treat as success.

Test signals: check trimming of all-FF, partially written, and aligned buffers; static-volume CRC success and ECC failure handling; reserve accounting after new bad PEBs, over-limit bad PEB counts, and no available PEBs; and expected log prefixes for normal, warning, and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/nvmem.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/nvmem.c

Purpose: this file registers selected UBI volumes as read-only NVMEM providers when their device-tree node contains an `nvmem-layout` child. It lets platform data such as calibration cells be read from UBI-backed storage through the generic NVMEM framework.

Important APIs, types, and functions: `struct ubi_nvmem` tracks the registered `nvmem_device`, UBI number, volume id, usable LEB size, and list link. `ubi_nvmem_reg_read()` implements NVMEM reads by opening the volume read-only and translating linear offsets into `(lnum, offset)` UBI reads. `ubi_nvmem_add()` builds the `nvmem_config`; `ubi_nvmem_remove()` unregisters matching providers. `nvmem_notify()` handles UBI volume events. Module init/exit register and unregister a UBI volume notifier.

Control flow: on `UBI_VOLUME_ADDED`, the notifier checks for an OF node and `nvmem-layout`, validates size fields, allocates state, registers a root-only read-only NVMEM device whose size is `usable_leb_size * vi->size`, and records it in a global list. On `UBI_VOLUME_RESIZED`, it removes the old provider and falls through to add a replacement. On `UBI_VOLUME_SHUTDOWN`, it removes the provider. NVMEM reads open the volume, loop while bytes remain, read at most one usable LEB segment per iteration, and close the volume.

State and persistence behavior: this module adds no flash format. Persistent bytes are the underlying UBI volume contents. Runtime state is the global `nvmem_devices` list protected by `devices_mutex`; each read opens the volume fresh, so it observes current volume mapping and size as exposed by UBI notifications.

Dependencies and integration points: it depends on the UBI notifier API from `kapi.c`, UBI read-only volume access, OF device nodes attached to UBI volumes, and `<linux/nvmem-provider.h>`. It is careful to use UBI volume info devices (`vi->dev`) for naming, ownership, and OF linkage.

Risks: pointer arithmetic on `void *val` relies on the kernel's GNU C behavior. Notifier documentation says callbacks must not use UBI API, but the NVMEM read path uses UBI API outside the notifier, while add/remove use only metadata and NVMEM registration. Missing `nvmem-layout` silently skips registration. Resize removes and recreates providers, which can invalidate consumers during topology changes.

Test signals: boot with a UBI volume node containing `nvmem-layout` and verify an NVMEM provider appears; read cells crossing LEB boundaries; resize a volume and observe provider re-registration with the new size; remove/detach the volume and verify unregister; check read-only/root-only policy; and validate failure paths for missing OF nodes and invalid volume sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi-media.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi-media.h

Purpose: this header defines UBI's on-flash ABI: magic values, format version, erase-counter headers, volume-identifier headers, volume table records, internal volume ids, compatibility flags, and fastmap data structures. It is the contract between images on flash, attach-time scanners, update/write paths, and external image-building tools.

Important APIs, types, and functions: key constants include `UBI_VERSION`, `UBI_MAX_ERASECOUNTER`, `UBI_CRC32_INIT`, `UBI_EC_HDR_MAGIC`, `UBI_VID_HDR_MAGIC`, `UBI_MAX_VOLUMES`, `UBI_VOL_NAME_MAX`, layout volume constants, and fastmap magic/size limits. Main structs are packed big-endian `struct ubi_ec_hdr`, `struct ubi_vid_hdr`, `struct ubi_vtbl_record`, and fastmap structs `ubi_fm_sb`, `ubi_fm_hdr`, `ubi_fm_scan_pool`, `ubi_fm_ec`, `ubi_fm_volhdr`, and `ubi_fm_eba`.

Control flow: no executable control flow exists here, but the layout drives IO and attach logic. EC headers identify valid UBI PEBs and carry erase counter, image sequence, VID offset, and data offset. VID headers map PEBs to `(vol_id, lnum)`, encode static/dynamic type, copy state, sequence numbers, and optional data CRC/size. Volume table records in the layout volume define user volumes and update markers. Fastmap structures summarize enough PEB and EBA state for faster attach.

State and persistence behavior: all structures are persistent and packed for exact flash representation. Multi-byte fields are big endian. CRC fields cover each header/record excluding the final CRC field. The layout volume stores two redundant LEBs of volume-table data. VID sequence numbers and copy flags are central to recovering from interrupted erase, update, and wear-leveling moves.

Dependencies and integration points: included by `ubi.h` and consumed by IO validation, attach scanning, EBA copy logic, volume table code, fastmap, and user-space tooling that writes UBI images. The compatibility enum for internal volumes tells older implementations whether to delete, preserve, reject, or attach read-only when unknown internal volumes are found.

Risks: any struct packing, field size, endian, or CRC coverage change is an on-flash compatibility break. `UBI_MAX_ERASECOUNTER` remains 31-bit despite a 64-bit EC field. Dynamic-volume VID data CRC fields are normally zero except for wear-leveling copies, which makes validation context-sensitive. Autoresize and skip-CRC flags affect first-boot sizing and static-volume integrity policy.

Test signals: verify binary offsets and sizes of EC/VID/vtbl/fastmap structs; attach old and new images; corrupt magic/CRC fields and confirm expected rejection; simulate duplicate LEB copies and validate sequence/copy-flag selection; test autoresize and skip-CRC volume flags; and fastmap attach fallback when fastmap headers are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi-media.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi.h

Purpose: this is the private UBI core header. It defines the central in-memory types, subsystem interfaces, constants, inline helpers, debug hooks, tree iteration macros, VID buffer allocation, volume/device state, attach information, and prototypes connecting attach, EBA, WL, volume table, API, fastmap, block, and IO code.

Important APIs, types, and functions: central structs include `ubi_device`, `ubi_volume`, `ubi_volume_desc`, `ubi_wl_entry`, `ubi_ltree_entry`, `ubi_attach_info`, `ubi_ainf_volume`, `ubi_ainf_peb`, `ubi_work`, `ubi_fastmap_layout`, `ubi_fm_pool`, `ubi_debug_info`, and `ubi_vid_io_buf`. Important helpers include `ubi_leb_valid()`, `ubi_init_vid_buf()`, `ubi_alloc_vid_buf()`, `ubi_free_vid_buf()`, `ubi_get_vid_hdr()`, `ubi_ro_mode()`, `ubi_io_read_data()`, `ubi_io_write_data()`, `vol_id2idx()`, `idx2vol_id()`, `ubi_is_fm_vol()`, and `ubi_find_fm_block()`.

Control flow: the header itself only supplies inline control paths, but those are important. VID buffer helpers hide aligned-buffer plus shifted-header addressing. Data IO helpers translate LEB-relative offsets to physical data offsets and inject data-write power-cut emulation. `ubi_ro_mode()` globally flips the device to read-only and dumps a stack once. Volume-id/index helpers map user volume IDs and internal volume IDs into `ubi->volumes[]` slots.

State and persistence behavior: `struct ubi_device` is the main runtime state container: volume table copy, PEB accounting, bad-block reserve accounting, EBA lock tree, fastmap pools, WL trees/queues/workers, MTD geometry, IO alignment, global sequence number, and debug knobs. `struct ubi_volume` holds persistent metadata mirrored from the volume table plus transient open/update/check state and the EBA mapping table. Attach structs are temporary representations of scanned flash before final device state is built.

Dependencies and integration points: this header pulls in Linux list/rbtree/locking/device/cdev/MTD headers and `ubi-media.h`. Every UBI implementation file in this group depends on it, and the prototypes document the subsystem boundaries: attach builds scanned state, vtbl initializes volumes, EBA maps LEBs, WL manages PEB lifecycle, IO touches MTD, kapi exports public functions, and fastmap/block support is optionally compiled.

Risks: because this header centralizes locking and state, field semantics are easy to misuse. `volumes_lock`, `wl_lock`, `device_mutex`, `move_mutex`, `work_sem`, `fm_eba_sem`, and `fm_protect` each protect distinct but overlapping state. Direct access to `ubi->volumes[]`, `vol->eba_tbl`, or WL trees must follow documented locking. Fastmap inline stubs must preserve behavior when disabled. The `ubi_io_write_data()` power-cut hook can turn ordinary writes into read-only transitions in debug builds.

Test signals: build with and without `CONFIG_MTD_UBI_FASTMAP` and `CONFIG_MTD_UBI_BLOCK`; lockdep coverage of volume/WL/EBA operations; correct internal-volume index mapping; VID buffer tests for shifted and unshifted headers; power-cut debug behavior on data writes; and attach/detach cycles that allocate and free all core structures without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/upd.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/upd.c

Purpose: this file implements whole-volume update and atomic LEB change support. Volume updates are made crash-detectable by an update marker stored in the volume table; interrupted updates leave the volume treated as damaged until a new update completes. Atomic LEB change collects replacement data and asks EBA to switch a single LEB atomically.

Important APIs, types, and functions: public internal entry points are `ubi_start_update()`, `ubi_more_update_data()`, `ubi_start_leb_change()`, and `ubi_more_leb_change_data()`. Internal helpers `set_update_marker()`, `clear_update_marker()`, and `write_leb()` manage the volume-table marker and per-LEB write semantics for dynamic versus static volumes.

Control flow: starting an update allocates a full LEB update buffer, sets the persistent update marker, unmaps every reserved LEB, flushes all WL erase work, and either clears the marker for zero-byte updates or initializes expected byte/LEB counters. Incremental update writes copy user data into `vol->upd_buf`, flush complete LEBs or the final partial LEB via `write_leb()`, and when all bytes arrive flush WL work, clear the marker, update static-volume size/corruption fields, free the buffer, and return the number of bytes accepted in the final call. Atomic LEB change similarly accumulates user data and calls `ubi_eba_atomic_leb_change()` once all bytes are present.

State and persistence behavior: the persistent state is `vtbl_rec.upd_marker`, written through `ubi_change_vtbl_record()`. Runtime state is `vol->updating`, `vol->changing_leb`, `upd_bytes`, `upd_received`, `upd_ebs`, `ch_lnum`, and `upd_buf`. Static-volume completion updates `used_bytes`, `used_ebs`, `last_eb_bytes`, and clears `corrupted`; dynamic updates trim trailing `0xFF` to keep later append space writable.

Dependencies and integration points: update marker writes go through the volume table path. LEB unmap/write/change calls go through EBA. WL flushing ensures old mappings are physically processed before update completion. User data is copied with `copy_from_user()`, and size arithmetic uses alignment and division helpers from Linux.

Risks: error paths after setting `vol->updating` or allocating `upd_buf` can leave cleanup responsibilities to the ioctl caller or higher layers; callers must serialize through volume/device locks. Whole-volume update first unmaps all LEBs, so the update marker is the main protection against exposing partial contents after reboot. Static-volume final LEB writes can be unaligned at the logical data level but must be padded correctly. Dynamic-volume trimming of trailing `0xFF` is required for writable free space and can change what is physically mapped.

Test signals: simulate interrupted updates and verify `upd_marker` blocks normal IO; complete zero-byte, dynamic, and static updates; write updates in small chunks crossing LEB boundaries; verify static `used_bytes` and CRC checking after update; inject EBA/WL failures; test atomic LEB change power-cut behavior; and verify dynamic trailing-FF trimming leaves all-FF LEBs unmapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/upd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vmt.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/vmt.c

Purpose: this file implements UBI volume management after a device is attached: create, remove, resize, rename, add existing volumes to the device model, free volumes on detach, expose per-volume sysfs attributes, and self-check volume state against the volume table.

Important APIs, types, and functions: main entry points are `ubi_create_volume()`, `ubi_remove_volume()`, `ubi_resize_volume()`, `ubi_rename_volumes()`, `ubi_add_volume()`, and `ubi_free_volume()`. Support code includes `vol_attribute_show()`, `vol_release()`, `find_volume_fwnode()`, `self_check_volume()`, and `self_check_volumes()`. Volume devices expose attributes such as `reserved_ebs`, `type`, `name`, `corrupted`, `alignment`, `usable_eb_size`, `data_bytes`, and `upd_marker`.

Control flow: creation validates available IDs/names under `volumes_lock`, computes usable LEB size and reserved PEBs, reserves accounting, flushes old erase work for that volume ID, creates an EBA table, initializes dynamic/static size fields, publishes the volume in `ubi->volumes[]`, registers cdev/device nodes, writes the volume table record, sends `UBI_VOLUME_ADDED`, and self-checks. Removal requires exclusive open, marks the volume dead to block new refs, sends shutdown notification, clears the volume-table record unless suppressed, unmaps all LEBs, deletes device nodes, returns PEB accounting, updates bad-block reserve, sends removed notification, and self-checks. Resize swaps EBA tables and updates accounting before committing the volume-table size, flushing when shrinking. Rename first updates the volume table for the whole batch, then updates RAM names or removes selected volumes.

State and persistence behavior: persistent metadata changes are volume table records written via `ubi_change_vtbl_record()` and physical unmaps through EBA/WL. Runtime state includes cdev/device registration, sysfs visibility, `is_dead`, reference counts, EBA table pointers, name/size/type fields, and global PEB accounting. `find_volume_fwnode()` attaches firmware nodes from a parent `volumes` child by `volname` or `volid`, enabling integrations such as NVMEM.

Dependencies and integration points: it integrates with Linux device/cdev/sysfs infrastructure, UBI volume notifier calls, EBA table allocation/replacement/unmap, WL flush, bad-block reserve accounting, volume table updates, firmware node APIs, and debug self-checks.

Risks: publish ordering matters: the volume is added to `ubi->volumes[]` before sysfs/cdev exposure, and removal uses `is_dead` to avoid races with sysfs reads. Resize rollback is complex because EBA tables and PEB accounting are changed before the volume table commit. Removing with `no_vtbl` is used after a batch volume-table rename/remove and must not double-clear records. `find_volume_fwnode()` matching by name uses `strncmp()` with volume name length, so ambiguous prefixes deserve review.

Test signals: create auto-ID and explicit-ID volumes; reject duplicate names and insufficient PEBs; verify sysfs attributes during concurrent removal; remove busy versus exclusive volumes; resize grow/shrink including static too-small rejection and shrink flush; batch rename/remove crash behavior; notifier ordering for shutdown/removed/resized/renamed; firmware-node association; and debug self-checks comparing RAM volume fields to vtbl records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vtbl.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/vtbl.c

Purpose: this file manages the on-flash volume table stored in the internal layout volume. It validates volume-table records, updates records atomically through the layout volume, recovers redundant table copies after unclean reboot, creates an empty layout volume on blank flash, and initializes in-memory `ubi_volume` objects from attach information.

Important APIs, types, and functions: main entry points are `ubi_change_vtbl_record()`, `ubi_vtbl_rename_volumes()`, and `ubi_read_volume_table()`. Key helpers include `ubi_update_layout_vol()`, `vtbl_check()`, `create_vtbl()`, `process_lvol()`, `create_empty_lvol()`, `init_volumes()`, `check_av()`, `check_attaching_info()`, and `self_vtbl_check()`. `empty_vtbl_record` holds the CRC of an all-zero record.

Control flow: record changes update the in-memory `ubi->vtbl`, compute CRCs, and write the full table to both layout-volume LEBs using `ubi_eba_atomic_leb_change()`. Attach computes slot count from LEB size, finds the layout volume in attach info, creates it if the flash is empty, or processes existing LEB0/LEB1 copies. `process_lvol()` prefers valid LEB0 as most recent, restores LEB1 from it if needed, or restores LEB0 from valid LEB1 when LEB0 is corrupted. `init_volumes()` allocates volume objects for nonempty records, handles autoresize and skip-check flags, initializes fastmap check maps, derives static-volume used sizes from scanned LEBs, and creates the internal layout volume object.

State and persistence behavior: the volume table is persistent, duplicated in layout volume LEB0 and LEB1, and protected per-record by CRC. The in-memory `ubi->vtbl` is the authoritative mutable copy while attached. Attach-time `ubi_attach_info` is reconciled against the table; unknown volumes found on flash can be discarded as unfinished removals. Layout-volume updates are atomic at the LEB level and preserve legacy redundancy.

Dependencies and integration points: it depends on EBA atomic LEB change, IO data reads/writes, attach allocation helpers, fastmap checkmap setup, UBI media constants, CRC32, and global PEB accounting. It is called before normal volume devices are registered and feeds `vmt.c` with initialized volumes.

Risks: attach recovery depends on the assumption that LEB0 is updated before LEB1 and is newer if both are valid but differ. Static volumes without scanned LEBs are treated as empty because the volume table does not store static data size, a documented limitation. Autoresize must appear on at most one volume. `vtbl_check()` must reject inconsistent alignment, duplicate names, invalid flags, and oversized reservations before runtime state is trusted.

Test signals: blank-flash attach creates two layout copies; corrupt LEB0 or LEB1 and verify restoration; corrupt both and reject attach; update table and simulate power cuts between copy updates; validate duplicate-name and bad-record rejection; attach static volumes with missing LEBs and observe corrupted/empty handling; autoresize flag detection; and consistency checks between attach info and volume records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/vtbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.c

Purpose: this file implements UBI wear leveling, scrubbing, physical eraseblock lifecycle, asynchronous erase work, bad-block handling, and the UBI background thread. It operates on PEBs and erase counters, while EBA maps logical data onto the PEBs it provides.

Important APIs, types, and functions: main entry points are `ubi_wl_init()`, `ubi_wl_close()`, `ubi_wl_get_peb()`, `ubi_wl_put_peb()`, `ubi_wl_scrub_peb()`, `ubi_wl_flush()`, `ubi_sync_erase()`, `ubi_bitflip_check()`, and `ubi_thread()`. Core helpers include `wl_tree_add()`, `wl_get_wle()`, `find_wl_entry()`, `find_mean_wl_entry()`, `prot_queue_add()`, `prot_queue_del()`, `schedule_erase()`, `wear_leveling_worker()`, `ensure_wear_leveling()`, `__erase_worker()`, `serve_prot_queue()`, `do_work()`, `shutdown_work()`, and `erase_aeb()`.

Control flow: initialization builds WL entries from attach lists: free PEBs enter the free RB-tree, used PEBs enter used or scrub trees, erase-list PEBs get scheduled, and fastmap PEBs are linked or erased. `ubi_wl_get_peb()` chooses a mean erase-counter free PEB, removes it from free, places it in the protection queue, verifies its writable area is all-FF, and returns the PEB number. `ubi_wl_put_peb()` removes a PEB from used/scrub/erroneous/protection state or coordinates with an active move, then schedules erase work. The background thread drains work items. Erase work calls `ubi_sync_erase()`, writes a new EC header, returns the PEB to free or fastmap anchor state, advances the protection queue, and schedules WL if needed.

State and persistence behavior: runtime state lives in `ubi_device`: used/free/scrub/erroneous RB-trees, protection queue, lookup table, pending work list, move markers, max EC, bad PEB accounting, reserve accounting, and background-thread state. Persistent state changes are EC increments and EC header writes, PEB erasures, bad-block marks, and copied VID/data from wear-leveling moves. The protection queue delays moves for newly allocated PEBs by a number of erase cycles.

Dependencies and integration points: WL calls IO for erase/header writes/bitflip checks, EBA for copying LEBs during moves, fastmap hooks when enabled, misc reserve helpers for bad-block accounting, and Linux kthreads/freezer/rbtree/locking infrastructure. EBA calls WL to get/put/scrub PEBs and flush pending erases for volume operations.

Risks: the move state machine is concurrency-sensitive: `move_from`, `move_to`, `move_to_put`, `move_mutex`, `wl_lock`, `work_sem`, `fm_eba_sem`, and `fm_protect` must remain correctly ordered. Error classification determines whether to protect, scrub, torture, mark erroneous, erase, or switch the whole device read-only. `ubi_wl_get_peb()` returns with `fm_eba_sem` held in the non-fastmap path according to its comment, so call pairing must be audited with EBA. Bad-block reserve exhaustion can force read-only mode. Fastmap anchor reservation alters free-tree selection.

Test signals: attach initialization should account for every good PEB exactly once; free/used/scrub/erroneous/protection transitions should satisfy debug self-checks; wear leveling should trigger when EC difference exceeds threshold; bitflips should schedule scrubbing and return `-EUCLEAN`; erase failures should mark bad PEBs and update reserves; background-thread failure count should switch to read-only after repeated errors; `ubi_wl_flush()` should drain targeted work; and fastmap-enabled builds should preserve anchors and pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.h

Purpose: this private header supplies wear-leveling declarations that vary with `CONFIG_MTD_UBI_FASTMAP`. It lets `wl.c` call static fastmap-aware helpers from the included fastmap WL implementation while keeping no-fastmap fallbacks minimal.

Important APIs, types, and functions: in fastmap builds it declares `update_fastmap_work_fn()`, `find_anchor_wl_entry()`, `get_peb_for_wl()`, `next_peb_for_wl()`, `need_wear_leveling()`, `ubi_fastmap_close()`, `ubi_fastmap_init()`, and `may_reserve_for_fm()`. Without fastmap it declares only `get_peb_for_wl()`, provides no-op `ubi_fastmap_close()` and `ubi_fastmap_init()`, and makes `may_reserve_for_fm()` return its input.

Control flow: `ubi_fastmap_init()` contributes fastmap reservation requirements to the caller's reserved PEB count, zeros pool reservations when fastmap is disabled, and initializes the fastmap work item. The no-fastmap branch compiles out these behaviors so WL uses its local non-fastmap `get_peb_for_wl()` implementation and plain wear-leveling threshold logic.

State and persistence behavior: this header itself stores no state. In fastmap mode it controls initialization of `ubi->fm_work` and reservation accounting for fastmap pools and two fastmap copies, which later affects persistent fastmap updates on flash. In no-fastmap mode no additional state is reserved.

Dependencies and integration points: it is included by `wl.c` after `ubi.h`. The declarations correspond to functions supplied either by `fastmap-wl.c` included from `wl.c` or by local no-fastmap functions at the end of `wl.c`.

Risks: because these functions are `static` declarations for code included into one translation unit, mismatches between `wl.h`, `wl.c`, and `fastmap-wl.c` can fail at compile time or subtly alter WL selection. Reservation math in `ubi_fastmap_init()` directly reduces available PEBs during WL init. The no-fastmap no-ops must keep behavior identical to older WL logic.

Test signals: build both fastmap and no-fastmap configurations; verify reserved PEB counts with fastmap enabled, disabled at runtime, and compiled out; confirm `fm_work` is initialized when needed; and exercise anchor reservation paths versus no-fastmap free-PEB selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/wl.h -->
