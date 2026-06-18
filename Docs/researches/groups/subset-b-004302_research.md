# Research: subset-b-004302

Grouped research for UBI driver files under `sources/distributed-fs/ceph-client/drivers/mtd/ubi`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/build.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/build.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/cdev.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.c

## Purpose
`debug.c` provides UBI diagnostics, debugfs controls, erase-count inspection, and optional fault-injection hooks. It is not part of normal data I/O, but it strongly affects testing and failure simulation.

## Important APIs, Types, And Functions
Dump helpers include `ubi_dump_flash()`, `ubi_dump_ec_hdr()`, `ubi_dump_vid_hdr()`, `ubi_dump_vol_info()`, `ubi_dump_vtbl_record()`, `ubi_dump_av()`, `ubi_dump_aeb()`, and `ubi_dump_mkvol_req()`. Debugfs lifecycle functions are `ubi_debugfs_init()`, `ubi_debugfs_exit()`, `ubi_debugfs_init_dev()`, and `ubi_debugfs_exit_dev()`. Debugfs file handlers are `dfs_file_read()`, `dfs_file_write()`, and the `detailed_erase_block_info` seq-file operations. `ubi_dbg_power_cut()` implements legacy power-cut countdown behavior. With `CONFIG_MTD_UBI_FAULT_INJECTION`, `should_fail_*()` wrappers are generated from Linux fault attributes.

## Control Flow
Global debugfs initialization creates `/sys/kernel/debug/ubi` and, when enabled, a `fault_inject` subtree. Per-device initialization creates `ubiX` files for generic checks, I/O checks, fastmap checks, background-thread disablement, legacy bitflip/I/O/power-cut emulation, power-cut min/max counters, detailed erase counts, and optional bitmask-driven fault injection.

`dfs_file_read()` maps the dentry being read to a field in `ubi->dbg`, formats booleans or numeric masks/counters, and holds a UBI device reference while reading. `dfs_file_write()` copies a short user buffer, parses either boolean `0/1` controls or integer mask/counter values, and updates `ubi->dbg`. The erase-block seq-file takes a device reference on open and iterates every physical eraseblock, skipping bad blocks and printing known erase counters from `ubi->lookuptbl` under `wl_lock`.

## State And Persistence
Most state is transient debug state in `struct ubi_debug_info`: check toggles, background-thread disable flag, legacy failure controls, `emulate_failures` mask, and power-cut countdown values. Dump helpers read flash or print in-memory structures without changing persistent state. Fault injection can deliberately cause lower I/O paths to simulate ECC, bitflip, read, write, erase, header, all-FF, and power-cut failures, which can indirectly alter persistent UBI state through recovery code under test.

## Dependencies And Integration Points
This file integrates with debugfs, seq_file, Linux fault-injection framework, MTD reads, WL lookup tables, UBI device refcounting, and the debug header inline hooks used by I/O, EBA, WL, and fastmap code. `build.c` calls global and per-device debugfs lifecycle functions during module/device attach and detach.

## Risks
Debugfs controls are privileged by filesystem permissions rather than ioctl capability checks. Race safety depends on `ubi_get_device()` holding the device alive while a debugfs file is accessed. `dfs_file_write()` accepts only small buffers and only checks the first byte for boolean toggles, which is intentional but easy to misuse in tests. Erase-count iteration returns errors from `ubi_io_is_bad()`, so debugfs reads can fail on MTD-level errors. Fault-injection combinations can produce destructive scenarios and must be isolated to test media.

## Test Signals
Signals include debugfs root/per-device creation and recursive removal, read/write round-trips for every toggle and counter, erase-count output stability while WL state changes, power-cut countdown behavior across min/max ranges, and fault-injection masks triggering the expected lower-layer failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.h

## Purpose
`debug.h` defines UBI assertion/logging macros, dump/debugfs prototypes, legacy random failure helpers, fault-injection masks, and inline predicates consumed throughout UBI.

## Important APIs, Types, And Functions
The header exports dump and debugfs prototypes implemented in `debug.c`, `ubi_self_check_all_ff()`, and `ubi_dbg_power_cut()`. It defines `ubi_assert()`, `ubi_dbg_msg()`, subsystem logging macros (`dbg_gen`, `dbg_eba`, `dbg_wl`, `dbg_io`, `dbg_bld`), and `ubi_dbg_print_hex_dump()`. Fault masks include power-cut at EC/VID/data writes, bitflips, ECC errors, read/write/erase failures, all-FF header reads, all-FF-with-bitflips, bad header, and bad-header-with-ECC variants. Inline checks include `ubi_dbg_is_power_cut()`, `ubi_dbg_is_bitflip()`, `ubi_dbg_is_write_failure()`, `ubi_dbg_is_erase_failure()`, `ubi_dbg_is_eccerr()`, `ubi_dbg_is_read_failure()`, `ubi_dbg_is_ff()`, `ubi_dbg_is_ff_bitflips()`, `ubi_dbg_is_bad_hdr()`, `ubi_dbg_is_bad_hdr_ebadmsg()`, `ubi_dbg_is_bgt_disabled()`, `ubi_dbg_chk_io()`, `ubi_dbg_chk_gen()`, `ubi_dbg_chk_fastmap()`, and `ubi_enable_dbg_chk_fastmap()`.

## Control Flow
Callers use the `ubi_dbg_is_*()` predicates in hot paths. Each predicate first checks legacy random/debugfs controls where applicable, then consults the structured Linux fault-injection path when `CONFIG_MTD_UBI_FAULT_INJECTION` is enabled. Without that config, the structured `ubi_dbg_fail_*()` macros compile to `false`, keeping production overhead low. Fastmap debug checking is a direct flag in `ubi->dbg`.

## State And Persistence
The header itself stores no state, but it standardizes access to `ubi->dbg` fields that are mutable through debugfs. These controls do not persist across module/device lifetime, but they influence persistent media operations during tests by injecting failures into writes, erases, reads, and fastmap checks.

## Dependencies And Integration Points
It depends on Linux random helpers and UBI core/media types being visible through including code. It is included broadly by UBI internals through `ubi.h`, making its inline behavior part of I/O, WL, EBA, attach, and fastmap semantics. The fault-injection externs are defined in `debug.c`.

## Risks
Because these are inline predicates, semantic changes affect many subsystems at once. `ubi_assert()` logs and dumps a stack but does not halt execution, so callers must not rely on it as runtime validation. Legacy random failure probabilities are fixed, which can make tests nondeterministic unless debugfs controls are managed carefully. Fault masks share a single bitfield, so tests should avoid ambiguous combinations unless specifically validating compound failures.

## Test Signals
Compile both with and without `CONFIG_MTD_UBI_FAULT_INJECTION`, verify no unresolved `should_fail_*` references in non-injection builds, confirm masks invoke the intended fault attributes, check fastmap debug enablement through `fm_debug`, and ensure assertion/log macros produce useful subsystem tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/eba.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/eba.c

## Purpose
`eba.c` implements the Eraseblock Association subsystem: the in-memory mapping from volume logical eraseblocks to physical eraseblocks, per-LEB locking, sequence-number allocation, read/write/unmap/copy operations, bad-block recovery, and EBA initialization from attach information.

## Important APIs, Types, And Functions
Private mapping types are `struct ubi_eba_entry` and `struct ubi_eba_table`. Public functions include `ubi_next_sqnum()`, `ubi_eba_get_ldesc()`, `ubi_eba_create_table()`, `ubi_eba_destroy_table()`, `ubi_eba_copy_table()`, `ubi_eba_replace_table()`, `ubi_eba_is_mapped()`, `ubi_eba_unmap_leb()`, `ubi_eba_read_leb()`, `ubi_eba_read_leb_sg()`, `ubi_eba_write_leb()`, `ubi_eba_write_leb_st()`, `ubi_eba_atomic_leb_change()`, `ubi_eba_copy_leb()`, `self_check_eba()`, and `ubi_eba_init()`.

## Control Flow
The lock tree (`ubi->ltree`) creates an RB-tree entry per currently locked `(vol_id, lnum)`. `leb_read_lock()`, `leb_write_lock()`, and `leb_write_trylock()` increment users and take a per-LEB rwsem; unlock paths remove the entry when users reaches zero. This allows concurrent reads while serializing writes and WL moves.

`ubi_eba_read_leb()` locks the LEB, checks fastmap mappings when needed, returns `0xFF` for unmapped dynamic LEBs, optionally reads and validates VID/data CRC for static volumes, reads data, schedules scrub on bitflips, and returns ECC/CRC errors. `ubi_eba_write_leb()` either writes into an existing mapped dynamic PEB or allocates a new PEB, writes a VID header with a fresh sequence number, writes data, updates the table, and retries bad PEBs. Static writes include used-EB/data-size/CRC metadata and prohibit rewrite by assertion. Atomic LEB change writes a replacement PEB with `copy_flag` and CRC under `alc_mutex`.

WL movement uses `ubi_eba_copy_leb()`: it try-locks the LEB to avoid deadlocks with unmap, verifies the mapping still points at the source PEB, reads data, trims dynamic trailing `0xFF`, writes VID/data to the target, rereads the VID header, and updates the EBA table under `volumes_lock`.

## State And Persistence
EBA tables are RAM-only but are reconstructed from attach scan/fastmap state and persisted indirectly through VID headers and fastmap. `ubi->global_sqnum` is initialized from attach max sequence and written to every new VID header. Mapping updates are paired with WL state: old PEBs are returned for erase/scrub, new PEBs come from `ubi_wl_get_peb()`, and fastmap synchronization uses `fm_eba_sem`.

## Dependencies And Integration Points
EBA depends on UBI I/O helpers for VID/data reads/writes, WL allocation/put/scrub, attach information, volume tables, CRC32, fastmap checkmaps, and bad-block policy. Character devices, gluebi, volume update code, WL, and fastmap call into EBA for user data and mapping state.

## Risks
Lock ordering is delicate: LEB locks, `fm_eba_sem`, `buf_mutex`, `volumes_lock`, and WL move locks must avoid deadlock. Several paths switch the whole device to read-only mode on unexpected write or mapping errors to preserve data. Fastmap cannot observe interrupted unmaps, so `check_mapping()` lazily fixes stale mappings during first access. Recovery from write failure assumes dynamic volumes for partial recovery and may retry only when the error appears recoverable. EBA table copy/replace during resize must not race with WL moves.

## Test Signals
Test unmapped dynamic reads, static CRC mismatch, bitflip scrub scheduling, direct writes to mapped and unmapped LEBs, write failure recovery on bad-block-capable MTDs, atomic LEB change after simulated power loss, WL copy races with unmap/delete, fastmap stale mapping cleanup, bad-block reserve accounting during `ubi_eba_init()`, and `self_check_eba()` against full-scan attach info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/eba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap-wl.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap-wl.c

## Purpose
`fastmap-wl.c` extends wear-leveling behavior for fastmap. It manages fastmap anchor PEB selection, user and WL fastmap pools, synchronous pool refill, asynchronous fastmap update work, and returning fastmap-owned PEBs to WL erase scheduling.

## Important APIs, Types, And Functions
Key functions are `ubi_wl_get_fm_peb()`, `ubi_refill_pools_and_lock()`, `ubi_wl_get_peb()`, `ubi_ensure_anchor_pebs()`, `ubi_wl_put_fm_peb()`, `ubi_is_erase_work()`, `ubi_fastmap_close()`, and `may_reserve_for_fm()`. Helpers include `update_fastmap_work_fn()`, `find_anchor_wl_entry()`, `return_unused_pool_pebs()`, `wait_free_pebs_for_pool()`, `left_free_count()`, `can_fill_pools()`, `produce_free_peb()`, `next_peb_for_wl()`, `need_wear_leveling()`, and `get_peb_for_wl()`.

## Control Flow
Fastmap needs an anchor PEB below `UBI_FM_MAX_START`. `ubi_wl_get_fm_peb()` removes either an anchor candidate or mean WL entry from the free RB-tree under `wl_lock`. `ubi_refill_pools_and_lock()` first waits for enough free PEBs, then takes `fm_protect`, `work_sem`, and `fm_eba_sem` in write mode, returns unused pool PEBs to the free tree, returns an existing anchor, chooses a new anchor, and fills the user and WL pools from free WL entries.

`ubi_wl_get_peb()` is the EBA-facing allocator. It takes `fm_eba_sem` in read mode, updates fastmap when pools are exhausted, returns a PEB from `fm_pool`, protects it in WL state, and intentionally returns with the read semaphore held so EBA can safely update mappings before `up_read()`. WL-internal allocation uses `fm_wl_pool`; when empty in atomic contexts it schedules `fm_work` instead of updating fastmap synchronously.

`ubi_ensure_anchor_pebs()` tries to reserve an anchor immediately or schedules wear leveling to produce one. `ubi_wl_put_fm_peb()` maps fastmap superblock/data PEBs to internal fastmap volume IDs and schedules erase, handling the first attach case where WL has not seen the PEB before.

## State And Persistence
State includes `ubi->fm_pool`, `ubi->fm_wl_pool`, `ubi->fm_anchor`, `fm_work_scheduled`, `fm_pool_rsv_cnt`, free/used/protected WL trees, and work queues. Persistent state is affected when pool exhaustion or volume changes cause `ubi_update_fastmap()` to write a new on-flash fastmap. Unused pool PEBs are not free until explicitly returned to WL.

## Dependencies And Integration Points
The file is tightly coupled to WL internals (`wl_tree_add`, `wl_get_wle`, `find_wl_entry`, `schedule_erase`, `do_work`, `wear_leveling_worker`, `erase_worker`), EBA via `fm_eba_sem`, and fastmap writing via `ubi_update_fastmap()`. It is included in the UBI WL build rather than standing alone with its own includes.

## Risks
Semaphore ownership is subtle: callers of `ubi_wl_get_peb()` must release `fm_eba_sem`, and error paths also return with the semaphore held in some cases. Pool accounting must not consume PEBs needed for WL/EBA/bad-block reserves or fastmap blocks themselves. Anchor scarcity can force wear leveling or fastmap update failure. Asynchronous `fm_work_scheduled` prevents repeated scheduling, so missed clearing could stall updates.

## Test Signals
Test pool refill with low free counts, anchor selection below `UBI_FM_MAX_START`, pool exhaustion triggering fastmap update, async WL pool refill scheduling from atomic contexts, return of unused pool PEBs during close/update, bad first-fastmap recovery where `lookuptbl[pnum]` is missing, and semaphore balance around EBA writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap-wl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap.c

## Purpose
`fastmap.c` implements on-flash fastmap format sizing, attach-time fastmap parsing, pool scanning, debug self-checks, fastmap writing, invalidation, and fastmap update orchestration. Fastmap accelerates attach by persisting enough WL/EBA/volume state to avoid a full flash scan.

## Important APIs, Types, And Functions
Public functions are `ubi_calc_fm_size()`, `ubi_scan_fastmap()`, `ubi_fastmap_init_checkmap()`, `ubi_fastmap_destroy_checkmap()`, and `ubi_update_fastmap()`. Important helpers include `new_fm_vbuf()`, `add_aeb()`, `add_vol()`, `assign_aeb_to_av()`, `update_vol()`, `process_pool_aeb()`, `unmap_peb()`, `scan_pool()`, `count_fastmap_pebs()`, `ubi_attach_fastmap()`, `find_fm_anchor()`, `clone_aeb()`, `ubi_write_fastmap()`, `invalidate_fastmap()`, and `return_fm_pebs()`.

## Control Flow
Attach starts with a scan of early PEBs that populates `scan_ai->fastmap`; `find_fm_anchor()` chooses the newest fastmap superblock. `ubi_scan_fastmap()` clones candidate fastmap PEBs, reads the superblock, validates magic/version/used block count/size, reads EC and VID headers for all fastmap blocks, checks image sequence, reads fastmap payload blocks into `ubi->fm_buf`, validates CRC, then calls `ubi_attach_fastmap()`.

`ubi_attach_fastmap()` parses the serialized fastmap: free/used/scrub/erase lists, volume headers, and per-volume EBA tables. It then scans user and WL pools for changes after the fastmap was written, resolving newer duplicate LEBs with `ubi_compare_lebs()`, moving stale/unmapped PEBs to erase/free, and rejecting leaks where counted PEBs do not match expected device totals.

`ubi_update_fastmap()` refills pools and locks fastmap-related semaphores, allocates a new layout, obtains or reuses fastmap data PEBs and an anchor, writes the serialized fastmap, frees the old layout, and ensures a future anchor. On write failure it writes an invalid fastmap marker when possible; otherwise it switches UBI to read-only mode.

## State And Persistence
The on-flash format contains `ubi_fm_sb`, `ubi_fm_hdr`, two scan pools, EC entries for WL lists, volume headers, and EBA arrays. `ubi->fm_buf` is a full serialized image sized by `ubi_calc_fm_size()`. Runtime state includes `ubi->fm`, pool maximums, `fast_attach`, per-volume `checkmap` bitmaps for lazy stale-mapping validation, and debug `seen` bitmaps. Successful writes persist current WL/EBA state and pool contents; invalidation persists a fake fastmap superblock that forces next attach to full scan.

## Dependencies And Integration Points
Fastmap depends on UBI media format definitions, attach info allocators, EBA descriptors, WL pools and fastmap PEB allocation, UBI I/O helpers, CRC32, debug fastmap checks, and bad-block/image-sequence validation. `build.c` sets fastmap sizing and enables/disables it; `eba.c` uses checkmaps after fast attach; WL calls `ubi_update_fastmap()` on pool exhaustion.

## Risks
Fastmap correctness is data-safety critical because it can replace a full scan. The parser guards every serialized section against `fm_size` overflow and rejects bad magic, bad pool sizes, wrong image sequence, damaged pool PEBs, and PEB leaks. Pool scanning is required because pool PEBs may have changed after the fastmap was written. Failure to invalidate an obsolete fastmap can resurrect stale EBA/WL state, so update errors either invalidate or force read-only. Debug self-checks can be expensive but catch missed PEB accounting.

## Test Signals
Test no-fastmap fallback, bad magic/version/CRC/size handling, image sequence mismatch, pool PEB with all-FF VID becoming free, pool PEB with newer LEB replacing old mapping, stale pool mapping unmap, PEB leak detection, successful fast attach setting pool sizes and `fast_attach`, fastmap update under volume change, update failure invalidation, and read-only transition when invalidation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/fastmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/gluebi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/gluebi.c -->
