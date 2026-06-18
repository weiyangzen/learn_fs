# sources/distributed-fs/ceph-client/drivers/mtd/ubi/ubi.h

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
