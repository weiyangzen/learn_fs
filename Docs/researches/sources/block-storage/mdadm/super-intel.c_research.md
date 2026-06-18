# File Research: sources/block-storage/mdadm/super-intel.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9958, source bytes 262105, report `Docs/researches/chunks/chunk_sources_block_storage_mdadm_super_intel_c_1_1_9958_3eeee6bd3e54_research.md`
- chunk 2: lines 9959-13343, source bytes 96448, report `Docs/researches/chunks/chunk_sources_block_storage_mdadm_super_intel_c_2_9959_13343_47434f495d98_research.md`

## Chunk Research

### Chunk 1: lines 1-9958

# Chunk Research: sources/block-storage/mdadm/super-intel.c lines 1-9958

## Scope

This chunk is the first 9,958 lines of mdadm's Intel Matrix Storage Manager (IMSM) metadata implementation. It defines the IMSM on-disk format, the in-memory container model, platform/HBA discovery, metadata load/examine/create/write paths, geometry validation, mdmon state projection, active-array state transitions, spare activation, and the first part of metadata update application.

The file continues after this chunk; the visible boundary cuts through `apply_reshape_container_disks_update()`, whose completion and the main `imsm_process_update()` dispatcher are in the next chunk.

## On-Disk And In-Memory State

- IMSM metadata is anchored by `struct imsm_super` at the second-to-last sector of each member disk, with optional extended MPB sectors before it. The signature is `MPB_SIGNATURE`, version fields are embedded after the signature prefix, and the checksum is a simple 32-bit additive checksum over `mpb_size` bytes excluding `check_sum` itself (`__gen_imsm_checksum()`).
- The packed metadata layout is variable length:
  - `struct imsm_super` contains `disk[1]`, followed by `num_disks` disk records.
  - `struct imsm_dev` records follow the disk table.
  - Each `imsm_dev` contains one `imsm_map`; a second map is present when `vol.migr_state != 0`.
  - Each `imsm_map` has a variable `disk_ord_tbl[num_members]`.
  - Optional BBM log data is stored at the end of the MPB.
- Size-preservation is guarded by `ASSERT_SIZE()` for `imsm_disk`, `imsm_map`, `imsm_vol`, `imsm_dev`, `imsm_super`, `bbm_log`, and `migr_record`.
- Important flags:
  - MPB attributes: RAID level support, expanded stripe sizes, 2TB volume/disk support, BBM, checksum verify.
  - Disk status: `SPARE_DISK`, `CONFIGURED_DISK`, `FAILED_DISK`, `JOURNAL_DISK`.
  - Map states: normal, uninitialized, degraded, failed.
  - Migration types: init, rebuild, verify/check, general migration, state change, repair.
  - RWH policy: off, distributed PPL, journaling drive, multiple PPL modes, bitmap.
- `struct intel_super` is the central in-memory object. It owns:
  - The raw MPB buffer (`buf`/`anchor`) and migration record buffer (`migr_rec_buf`/`migr_rec`).
  - Parsed devices in `devlist` using independently allocated `imsm_dev` copies.
  - Disk lists: active disks (`disks`), pending add/remove list (`disk_mgmt_list`), and missing disks (`missing`).
  - HBA/platform capability (`hba`, `orom`), bad block memory, update counters, sector size, current subarray, and create offset.
- `struct dl` is embedded inside `intel_super` and represents a physical disk with serial, fd, major/minor, IMSM disk record, metadata index, extent list, raid slot, and management action.
- Metadata update payloads are defined up front and later queued through mdmon update channels: create/kill/rename array, add/remove disk, activate spare, reshape, takeover, general migration checkpoint, size change, prealloc badblock memory, and RWH policy changes.

## Core Helpers And Format Accessors

- `get_imsm_map(dev, MAP_0/MAP_1/MAP_X)` centralizes map selection. `MAP_X` means "second map if present, else first map", which is used when the active kernel view should reflect current migration state.
- `sizeof_imsm_map()` and `sizeof_imsm_dev()` calculate variable metadata object sizes; many copy/allocation paths rely on these and are sensitive to corrupted `num_members` or map layout.
- `__get_imsm_dev()` and `get_imsm_dev()` abort on invalid indexes. Callers generally validate against `num_raid_devs`, but malformed metadata can still turn these into process aborts rather than recoverable load errors.
- `join_u32()`/`split_ull()` wrap 64-bit fields split into little-endian low/high `__u32` values; helpers expose total disk blocks, map offsets, blocks per member, stripe counts, device size, migration checkpoint area, and migration units.
- `update_imsm_raid_level()` preserves IMSM compatibility quirks where older RAID10 representations may use `raid_level == IMSM_T_RAID1` depending on member count. `get_imsm_raid_level()` reverses that encoding for mdadm-facing logic.
- Ordinal helpers (`get_imsm_ord_tbl_ent()`, `ord_to_idx()`, `get_imsm_disk_idx()`, `get_imsm_disk_slot()`, `set_imsm_ord_tbl_ent()`) manage disk-slot relationships and the top-byte `IMSM_ORD_REBUILD` flag.
- `imsm_num_data_members()`, `per_dev_array_size()`, `calc_component_size()`, `update_num_data_stripes()`, and `imsm_set_array_size()` derive volume capacity from RAID level, member count, domain count, stripe count, and metadata size fields.

## Platform And Device Dependencies

- The implementation depends on mdadm internals from `mdadm.h`, `mdmon.h`, `dlink.h`, `platform-intel.h`, `drive_encryption.h`, `sha1.h`, and `xmalloc.h`.
- It uses Linux-specific device interfaces:
  - `/proc/cmdline` and `IMSM_NO_PLATFORM`/`IMSM_DEVNAME_AS_SERIAL` env toggles.
  - `/sys/dev/block`, `/sys/block`, sysfs md state, mdstat parsing, and block device major/minor discovery.
  - SCSI inquiry through `SG_IO` and NVMe serial extraction through sysfs paths.
  - Raw block reads/writes/lseek/fsync against member devices.
- Intel platform checks are delegated to `find_intel_devices()`, `find_imsm_capability()`, `get_orom_by_device_id()`, OROM capability helpers, path attachment helpers, VMD/NVMe helpers, and controller/device lookup helpers.
- Encryption display delegates to `get_nvme_opal_encryption_information()` and `get_ata_encryption_information()`.
- PPL support depends on `struct ppl_header`, `PPL_HEADER_SIZE`, `PPL_ENTRY_SPACE`, and `crc32c_le()`.

## Load, Assembly, And Examination Flow

- `match_metadata_desc_imsm()` allocates the `supertype` for `imsm`/`default`, wiring it to `super_imsm`.
- `load_super_imsm()` is the single-device load path:
  1. Reject partitions.
  2. Allocate `intel_super`.
  3. Discover sector size.
  4. Try HBA/capability discovery unless hardware compatibility is ignored.
  5. `load_and_parse_mpb()` reads the MPB, normalizes 4K-sector metadata if needed, reads the member serial, parses variable devices, loads BBM, and clears high LBA fields when the 2TB-disk attribute is absent.
  6. Retry checksum failures briefly when mdmon may be racing metadata updates.
  7. Load migration record if a general migration is in progress and reject unsupported migration forms.
- `load_container_imsm()` and `load_super_imsm_all()` load all member MPBs either from an open md container or from a device list. They then run `imsm_thunderdome()` to choose one coherent MPB family/generation, merge disk lists into the champion, find missing disks, load migration records, and reject unsupported migration metadata.
- `imsm_thunderdome()` resolves multiple loaded MPBs by `family_num`, `check_sum`, `generation_num`, configured/spare status, and a merged serial-index ownership list. It can report family conflicts and prefers a populated family over free-floating spares.
- `find_missing()` creates placeholder `dl` entries for disks present in the MPB but absent from loaded device serials.
- `examine_super_imsm()`, `brief_examine_super_imsm()`, `brief_examine_subarrays_imsm()`, `export_examine_super_imsm()`, `detail_super_imsm()`, and `brief_detail_super_imsm()` expose human or environment-style metadata summaries.
- UUIDs are synthetic: `uuid_from_super_imsm()` hashes the MPB signature, original family number, current volume index, and volume name via SHA1. IMSM itself does not store md UUIDs.
- `getinfo_super_imsm()` projects either the container or the selected subarray into `struct mdinfo`; `getinfo_super_imsm_volume()` handles level/layout/chunk, member count, reshape fields, component size, consistency policy, PPL/bitmap sectors, resync/recovery starts, md text version, and UUID.
- `container_content_imsm()` builds an mdinfo list for all subarrays, filters unsupported attributes and unsupported migrations, blocks invalid geometry, attaches member devices, imports BBM entries, sets recovery starts, and invokes backup recovery for active reshapes.

## Bad Block Management

- BBM log entries use a 48-bit little-endian sector field (`bbm_log_block_addr`) and represent up to 256 contiguous LBAs per entry.
- `load_bbm_log()` allocates `super->bbm_log`, validates stored signature/count/size, copies the log from the MPB tail, or initializes an empty log.
- `record_new_badblock()` may replace an existing covered entry or append chunked entries; it refuses to exceed `BBM_LOG_MAX_ENTRIES`.
- `clear_disk_badblocks()` and `clear_badblock()` remove entries by swapping with the last active entry.
- `get_volume_badblocks()` filters per-disk BBM entries into `md_bb` for a volume's data range.
- `write_super_imsm()` serializes the in-memory BBM log into the MPB tail and toggles `MPB_ATTRIB_BBM` according to non-empty log size.

## 4K Sector Conversion

- IMSM metadata appears internally in 512-byte sector units. When the member device sector size is 4096, `convert_from_4k()` expands on-disk values by `IMSM_4K_DIV == 8` after reading; `convert_to_4k()` divides values before writing.
- Conversion covers disk total blocks, device size/current migration unit, map blocks-per-member, blocks-per-strip, PBA offsets, migration record fields, BBM sector starts/counts, and checksum.
- Risk: conversion mutates the shared `super->anchor` buffer in place. Call flows must convert back after temporary write conversion; most paths do so, but `store_super_imsm()` converts to 4K and writes without visibly converting back in this chunk.

## Migration And Reshape State

- The code distinguishes:
  - Initialization/resync/repair using migration state and duplicate maps.
  - Rebuild using map0 as destination and map1 as degraded source/current state.
  - General migration/reshape using a separate `migr_record` stored at the last sector of selected member disks.
- `migrate()` marks a device as migrating, duplicates map0 into map1, clears rebuild flags for general migration, optionally clears the migration record, and sets map0 to the target state.
- `end_migration()` collapses migration state, merges unfinished rebuild flags when needed, recomputes degraded state, clears migration type/current unit, and sets map0 state.
- `blocks_per_migr_unit()` maps IMSM migration units to md recovery/reshape blocks for init, repair, verify, rebuild, and general migration. It depends on helper calculations for migration strip size, stripes-per-unit, parity depth, and migration block mapping.
- `read_imsm_migr_rec()`/`load_imsm_migr_rec()` read the migration record from the last disk sector, only from slot 0 or 1 of a general-migrating array.
- `write_imsm_migr_rec()` writes the record back to the first two slots and emits an `update_general_migration_checkpoint` locally and through mdmon if configured.
- `check_mpb_migr_compatibility()` rejects migration optimization area changes (`pba_of_lba0` differs between maps) and unsupported descending reshapes.
- `imsm_reshape_blocks_arrays_changes()` blocks spare/missing disk activation while any dev in the container is under general migration.
- `imsm_progress_container_reshape()` begins general migration on the next array whose member count lags behind a prior array after a container-level reshape.

## Create, Add, Remove, And Write Paths

- `init_super_imsm()` creates a fresh container MPB or delegates to `init_super_imsm_volume()` when adding a volume to an existing container.
- `init_super_imsm_volume()` validates volume count, resizes MPB buffer if needed, handles requested missing disks, enforces unique POSIX-compatible IMSM volume names, builds `imsm_dev`/map state, computes array size, sets initial migration/init state, assigns RWH policy, appends to `devlist`, and updates metadata version/attributes.
- `add_to_super_imsm()` handles disk addition at container level:
  - Enforces Intel HBA/capability compatibility.
  - Reads serial and device size/sector size.
  - Rejects unsupported NVMe/multipath/non-Intel NVMe configurations when platform capabilities disallow them.
  - Clears the migration record area on disk.
  - Marks the new disk as spare and either queues it for mdmon or writes standalone spare metadata immediately.
- `add_to_super_imsm_volume()` assigns a container disk to the current volume slot, ensures sector-size consistency, prevents duplicate inclusion, updates missing-disk placeholders, writes first-volume family/orig family/creation time, and records `current_disk`.
- `remove_from_super_imsm()` is mdmon-only and queues a `DISK_REMOVE` action in `disk_mgmt_list`.
- `mark_spare()` restores a disk's real serial if possible and marks it as a spare.
- `write_super_imsm()` is the main serializer:
  - Increments generation.
  - Fixes missing `orig_family_num`.
  - Rebuilds MPB disk table from present and missing disks.
  - Copies parsed `devlist` devices into the raw MPB buffer.
  - Appends BBM log.
  - Recomputes MPB size/checksum.
  - Clears migration record unless a general migration is active.
  - Converts to 4K if needed.
  - Writes MPB and migration record to active, non-failed members, then writes standalone spare records.
- `store_imsm_mpb()` writes extended MPB sectors before the anchor and the anchor at the second-to-last sector.
- `write_init_super_imsm()` handles post-create initialization. Without mdmon it kills old metadata on members, initializes PPL/bitmap where required, and writes superblocks. With mdmon it queues create or disk-management updates.

## PPL And Bitmap Handling

- IMSM reserves a 1 MiB area after volume data for multiple PPLs or internal bitmap. PPL and bitmap are mutually exclusive.
- `get_ppl_sector()`, `get_bitmap_header_sector()`, and `get_bitmap_sector()` compute metadata areas from map start and component size.
- `write_init_ppl_imsm()` zeros the PPL area, creates a PPL header with MPB original family signature, and writes a deliberately invalid entry when replacing invalid PPL state to force resync.
- `validate_ppl_imsm()` scans possible PPL headers inside the 1 MiB area, validates CRC/signature/generation, can upgrade legacy PPL size metadata to multiple-PPL area through `update_subarray(UOPT_PPL)`, and initializes or patches headers depending on array/rebuild state.
- `write_init_ppl_imsm_all()` initializes PPL on all active RAID5 members with PPL policy.
- `write_init_bitmap_imsm_vol()` and `write_init_bitmap_imsm_all()` initialize the bitmap area for volumes using bitmap consistency policy.
- `update_subarray_imsm()` can switch RWH policy to PPL/off/bitmap/no-bitmap and initializes bitmap immediately when enabling bitmap.

## Geometry, Free Space, And Platform Limits

- `validate_geometry_imsm_container()` validates fresh container-member devices against HBA/platform capabilities, maximum disks, 2TB disk support, and NVMe namespace support, and reports available size excluding IMSM reservations.
- `get_extents()` gathers used volume extents plus metadata reservation per disk. Spares use minimal reservation to remain eligible for any array; active disks account for reserved metadata/dirty stripe regions.
- `merge_extents()` coalesces extents from all candidate disks to find a common start and free region, optionally for expansion. It updates `super->create_offset`.
- `validate_geometry_imsm_orom()` checks OROM disk-per-array limits, supported RAID levels/member counts, default or requested chunk size, supported chunk mask, md layout compatibility, and 2TB volume support.
- `validate_geometry_imsm_volume()` validates a volume inside a loaded container, requiring candidate devices to be container members, respecting OROM constraints that all disks be members of all volumes, and using `merge_extents()` for a common free space window.
- `imsm_get_free_size()` and `autolayout_imsm()` support no-device autolayout by marking selected `dl->raiddisk` slots and preserving slot order with the first volume when a container already has volumes.
- `validate_geometry_imsm()` dispatches between fresh container creation, volume autolayout, existing-container volume creation, or busy-device container membership checks.
- `count_volumes()`, `__count_volumes()`, `active_arrays_by_format()`, `get_devices()`, and `count_volumes_list()` inspect mdstat/sysfs and HBA-attached devices to enforce platform volume-per-controller limits.

## mdmon Active-Array Control

- `imsm_open_new()` validates a subarray index and queues/prepares a badblock-memory preallocation update.
- `imsm_set_array_state()` is the main active-array state callback:
  - Handles reshape progress and completion.
  - Calls `handle_missing()` before activation.
  - Starts init/repair migration when md reports incomplete resync and no reshape is blocking.
  - Completes resync migrations.
  - Updates checkpoint units from md last checkpoint.
  - Marks dirty/clean state and sets `RAIDVOL_DSRECORD_VALID` for PPL dirty state.
- `imsm_set_disk()` handles member-level transitions:
  - Marks new failures in map0 and map1.
  - Clears rebuild flags in map1 when a rebuilding disk becomes in-sync.
  - Computes normal/degraded/failed map transitions.
  - Ends rebuild or general migration when md progress reaches completion.
  - Updates `failed_disk_num`, map state, last checkpoint, and update counters.
- `mark_failure()`, `mark_missing()`, and `handle_missing()` propagate missing/failed disks into maps, update serial/scsi_id placeholders, clear disk BBM entries, and may end non-general migration when rebuild state is complete enough.
- `imsm_check_degraded()` encodes RAID0/1/10/5 failure tolerance; RAID10 explicitly checks mirror pairs.
- `imsm_count_failed()` counts failures/rebuild markers across map0/map1 depending on map selector.

## Spare Activation And Disk Management Updates

- `imsm_activate_spare()` selects replacement disks for degraded arrays. It blocks during container reshape, during existing rebuild, for unsupported takeover RAID4 state, for uninitialized volumes, and when another failed subarray still has undeleted failed disks.
- Spare selection preference:
  1. Re-add previous occupant (`imsm_readd()`).
  2. Continue partially assimilated spare (`imsm_add_spare(... activate_new=0)`).
  3. Activate pristine spare (`activate_new=1`).
- `imsm_add_spare()` verifies the candidate is not already in the array/test list, is not failed/in-use/deleted, has matching sector size, and has sufficient free extents for every member volume at each volume's required offset.
- `imsm_activate_spare()` returns mdinfo entries for md to add and creates an `update_activate_spare` metadata update list.
- `prepare_spare_to_activate()` initializes bitmap metadata on the chosen spare when the target volume uses internal bitmap consistency.
- `apply_update_activate_spare()` mutates metadata for queued spare activation: assigns new indexes for pristine spares, marks disk configured, starts rebuild migration, updates ord tables, bumps family number, and deletes the replaced disk if no active array still references it.
- `add_remove_disk_update()` drains `disk_mgmt_list`, adding new disks to `super->disks` or marking/removing queued removals.

## Update Application Covered In This Chunk

- The chunk includes full implementations for:
  - `apply_reshape_migration_update()`: starts a general migration on a subarray, optionally changes RAID level/chunk/member count, converts a spare into a new member for RAID0-to-RAID5 style migration, recomputes blocks per member and array size, and uses `space_list` for copy-on-write device replacement.
  - `apply_size_change_update()`: changes device size, blocks per member, and data stripe count.
  - `apply_update_activate_spare()`: described above.
- The chunk begins `apply_reshape_container_disks_update()`, which converts supplied spares into active members and starts container-disk-count reshape across devices, but the function body is truncated by the chunk boundary before its map copy/update logic is complete.

## Risks And Edge Cases

- Many metadata accessors assume prior validation and call `abort()` for invalid dev indexes. This is robust for internal invariants but harsh for corrupted on-disk metadata.
- Variable-length pointer arithmetic relies on untrusted on-disk counts (`num_disks`, `num_raid_devs`, `num_members`, `mpb_size`) being sane. Some checksum/signature checks exist, but bounds validation is not uniformly explicit before walking structures.
- `load_imsm_mpb()` uses `anchor->mpb_size` before endian conversion in at least the `ROUND_UP(anchor->mpb_size, sector_size)` path; this depends on host/endian assumptions common to mdadm/Linux but is notable for portability.
- In-place 4K conversion is easy to misuse. Writers must ensure metadata is restored to internal 512-sector units after conversion; not every path in this chunk visibly converts back.
- Several paths operate on raw block devices and depend on correct `sector_size`. A mixed sector-size container is rejected, but standalone spare metadata and migration-record clearing have to use the target disk's member sector size carefully.
- `clear_badblock()` always returns success even if no exact entry was found.
- `record_new_badblock()` handles fixed-size entry chunks but does not sort BBM entries; consumers scan linearly.
- `is_bad_block_in_volume()` checks overlap using inclusive end conditions that may treat an entry ending exactly at `start_sector + size` as in-volume.
- `active_arrays_by_format()`/volume counting walks live mdstat/sysfs and block devices; races with mdmon or kernel md state are expected and partially handled elsewhere with retries.
- `count_volumes_list()` has complex `used` state transitions (`1`, `2`, `3`, `4`) and loads/free supertype copies per device; misclassification can affect platform volume-limit enforcement.
- `kill_subarray_imsm()` removes a node from `devlist` without freeing it in the non-mdmon path, which may be acceptable for process lifetime but is a leak-shaped local behavior.
- `apply_reshape_migration_update()` restricts `subdev` to 0 or 1 despite `IMSM_MAX_DEVICES` and multiple-volume containers; this may be a format/tool limitation but is a notable validation boundary.
- `apply_reshape_migration_update()` logs `new_disk->index` in a debug line before checking `new_disk == NULL`.
- The adjacent post-boundary code contains a FIXME in takeover disk index handling, confirming maintainers consider part of the takeover index update logic suspect.

## Cross-Chunk References

- `apply_reshape_container_disks_update()` starts in this chunk at line 9897 but continues after line 9958. Adjacent context shows it copies old maps, creates map1, marks one device for `MIGR_GEN_MIGR`, updates member count, recomputes array size, clears the migration record, and returns via `update_reshape_exit`.
- `apply_takeover_update()` and the main `imsm_process_update()` dispatcher are after the chunk boundary. The dispatcher applies update types defined in this chunk and calls the apply helpers implemented here.
- Forward declarations in this chunk refer to later definitions outside the current range:
  - `recover_backup_imsm()`
  - `imsm_prepare_update()`
  - `imsm_delete()`
  - reshape/takeover/bitmap APIs later in the file
  - final `struct superswitch super_imsm`
- Functions in this chunk are consumed by the later superswitch table and mdadm/mdmon entry points: load, store, write-init, validate geometry, getinfo, container content, activate spare, set array/disk state, badblock handling, reshape, and bitmap operations.

### Chunk 2: lines 9959-13343

# Chunk Research: sources/block-storage/mdadm/super-intel.c lines 9959-13343

## Scope

This chunk covers the tail of IMSM reshape-apply logic, mdmon metadata update preparation/processing, disk deletion and degradation helpers, container validation, bad-block handling, migration backup/recovery, drive policy checks, spare criteria, reshape analysis/execution, reshape management, internal bitmap support, and the final `super_imsm` superswitch registration.

The first lines are a continuation from the previous chunk: `apply_reshape_container_disks_update()` has already found or allocated a replacement `imsm_dev`; this chunk finishes expanding maps, swapping `id->dev`, clearing the migration record, and returning success.

## APIs And Entry Points

- `imsm_process_update(st, update)` is the mdmon-side dispatcher for `enum imsm_update_type` records. It handles checkpoint, takeover, container reshape, migration reshape, size change, spare activation, array create/kill/rename, disk add/remove, bad-block preallocation, and RWH policy updates.
- `imsm_prepare_update(st, update)` validates update payload sizes and preallocates memory needed by `imsm_process_update()`, including `update->space`, `update->space_list`, and enlarged metadata buffers via `super->next_buf`.
- `apply_takeover_update(u, super, space_list)` applies RAID10-to-RAID0 and RAID0-to-RAID10 metadata transformations.
- Migration/reshape backup hooks include `init_migr_record_imsm()`, `save_backup_imsm()`, `save_checkpoint_imsm()`, `recover_backup_imsm()`, `wait_for_reshape_imsm()`, `check_degradation_change()`, and `imsm_manage_reshape()`.
- Internal bitmap hooks include `add_internal_bitmap_imsm()`, `locate_bitmap_imsm()`, `write_init_bitmap_imsm()`, and `set_bitmap_imsm()`.
- The chunk closes by populating `struct superswitch super_imsm`, wiring the above functions into mdadm/mdmon's metadata abstraction.

## Control Flow

Metadata updates follow a two-phase local/remote pattern. Callers allocate a typed update record, invoke `imsm_update_metadata_locally()`, and optionally queue the same record with `append_metadata_update()` if `st->update_tail` is present. `imsm_update_metadata_locally()` constructs a temporary `metadata_update`, calls `imsm_prepare_update()`, then `imsm_process_update()`, and finally frees any preallocated `space_list` nodes.

Container reshape flow starts in `imsm_reshape_super()` when the target device name equals the container name. It validates a pure RAID-disk-count increase through `imsm_reshape_is_allowed_on_container()`, fixes size mismatches, builds an `update_reshape_container_disks` record with selected spares, applies it locally, and may queue it. The apply function was started in the previous chunk and finishes here by enlarging each `imsm_map`, copying the old map to `MAP_1`, marking only selected arrays as `MIGR_GEN_MIGR`, resetting array size, replacing the `imsm_dev`, and clearing `super->migr_rec`.

Volume reshape flow starts in `imsm_reshape_super()` when operating on a subarray. It resolves the active subarray by mdstat, sets `super->current_vol`, calls `imsm_analyze_change()`, then dispatches to takeover, migration, or array-size updates. `imsm_analyze_change()` supports RAID0->RAID5 migration, RAID0<->RAID10 takeover, RAID5 layout changes between supported IMSM layouts, chunk-size migration except RAID10, and expand-only size changes.

Runtime reshape management is performed by `imsm_manage_reshape()`. It locates exactly one volume with `MIGR_GEN_MIGR`, initializes or reloads migration checkpoint state, allocates a checkpoint buffer, loops over migration units, backs up critical stripes into the IMSM migration copy area when source/destination geometry overlaps, advances kernel reshape through sysfs `sync_max`/`suspend_lo`/`suspend_hi`, writes checkpoint states, watches degradation, and clears on-disk migration records after success.

Recovery flow in `recover_backup_imsm()` only runs during assembly when sysfs `array_state` is `inactive`, the migration record indicates data in the copy area, and exactly one IMSM volume is in general migration. It reads the migration copy area from valid member disks, writes it back to the destination offset, tolerates skipped disks only up to `imsm_get_allowed_degradation()`, then marks the copy area normal through `save_checkpoint_imsm()`.

## State And Dependencies

Key mutated state includes `super->buf`, `super->next_buf`, `super->updates_pending`, `super->anchor->num_disks`, `num_raid_devs`, disk `index`/`raiddisk`/status flags, `imsm_dev` map state, RAID level, member counts, order tables, array size, migration unit fields, BBM log entries, and RWH bitmap policy.

The chunk depends on earlier IMSM helpers for map access, map sizing, ordinal access, RAID geometry, metadata mutation, disk lookup, geometry validation, and bitmap layout. It also uses mdadm-wide sysfs helpers, mdstat lookup, spare selection, metadata queueing, bad-block helpers, stripe conversion, platform/HBA discovery, ATA/NVMe encryption probes, device size/path helpers, and OS calls like `open()`, `lseek()`, `read()`, `write()`, `fsync()`, and `posix_memalign()`.

## Risks And Cross-Chunk References

- The takeover path contains an inline FIXME warning that nested index renumbering for RAID10-to-RAID0 failed disks may be wrong.
- Several update paths assume prepared scratch memory exists and use generic allocations as linked-list nodes; size/type mismatches could corrupt later frees.
- `apply_reshape_migration_update()` is defined just before this chunk and only accepts `u->subdev <= 1`, while this chunk’s callers can operate on selected subarrays.
- `recover_backup_imsm()` may issue partial restore writes before deciding too many disks were skipped.
- `imsm_manage_reshape()` aborts on `degraded > 1`, while allowed degradation is topology-dependent elsewhere.
- `write_init_bitmap_imsm()` computes `to_write` but writes `MAX_SECTOR_SIZE` each loop.
- This chunk starts mid-`apply_reshape_container_disks_update()`; setup and spare conversion are in the previous chunk around lines 9897-9958.
- Earlier definitions around lines 529-610 provide `enum imsm_update_type`, update structs, `geo_params`, and reshape type enums used throughout this chunk.
- The final `super_imsm` table is the integration boundary for the whole file, exposing both earlier and current chunk functions to mdadm/mdmon.

## Summary

This chunk is the operational back half of IMSM metadata handling. It turns prepared typed updates into durable metadata mutations, validates platform and drive policies, manages online reshape backup/checkpoint/recovery, supports bad-block and internal bitmap hooks, and registers the completed IMSM implementation with mdadm’s superswitch interface.
