# Group Research: group_1663_reactos_sources_windows_reactos_drivers_filesystems_btrfs_scrub_c_s_022523d43e3b

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/scrub.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/scrub.c

## Scope And Purpose

`scrub.c` implements the WinBtrfs/ReactOS Btrfs scrub engine. It walks allocated extents in every writable chunk, reads the physical stripes, verifies data checksums or metadata tree checksums, logs corruption with filesystem context, and repairs recoverable errors by rewriting bad mirrors or parity stripes. It also exposes the public scrub control/query operations: `start_scrub`, `query_scrub`, `pause_scrub`, `resume_scrub`, and `stop_scrub`.

Complete file read: 3452 lines.

## Main Structures

- `SCRUB_UNIT` is 1 MiB and bounds normal non-RAID56 scrub reads.
- `scrub_context` and `scrub_context_stripe` track asynchronous stripe reads for duplicate, RAID0, RAID1-like, RAID10, and single layout handling.
- `scrub_context_raid56` and `scrub_context_raid56_stripe` track full-stripe RAID5/6 reads, allocation bitmaps, checksum-presence bitmaps, tree/data classification, per-stripe error bitmaps, parity scratch buffers, and rewrite state.
- `path_part` is a temporary path reconstruction node used to translate checksum errors back into a user-visible subvolume/path/offset report.

## Error Attribution

The file invests substantial logic in making scrub errors actionable rather than only reporting a logical address.

- `log_file_checksum_error` reconstructs a file path from subvolume, inode, and offset. It follows `INODE_REF`, `INODE_EXTREF`, and `ROOT_BACKREF` records, handles subvolume boundaries, converts UTF-8 path bytes to UTF-16, and appends a `scrub_error` to `Vcb->scrub.errors`.
- `log_file_checksum_error_shared` handles shared data refs by reading the referencing leaf and finding matching `EXTENT_DATA` records.
- `log_tree_checksum_error` records metadata root, level, and first key when available.
- `log_tree_checksum_error_shared` follows shared block refs by reading the parent tree and finding the child pointer.
- `log_unrecoverable_error` looks up the extent item/metadata item for a corrupted address, parses inline and separate backrefs, and delegates to file/tree attribution helpers.
- `log_error` is the common entry point. Recoverable errors are directly recorded; unrecoverable errors are expanded through extent backrefs.

All scrub error list mutations and counters are protected by `Vcb->scrub.stats_lock`.

## Normal Stripe Scrubbing

`scrub_extent` prepares asynchronous IRPs for each stripe involved in a logical extent. It handles buffered, direct, and neither-buffered-nor-direct device I/O, waits for all reads through a completion event, updates `Vcb->scrub.data_scrubbed`, records read errors against devices, and then dispatches by layout:

- `scrub_extent_dup` handles duplicate, RAID1-like, RAID1C3/C4, and single layouts. With data checksums it validates against checksum items; for metadata it validates tree checksums and logical addresses. If one good copy exists, it logs recoverable errors and overwrites bad copies. If all copies are bad, it attempts sector/node-level reconstruction from any individually good copy.
- `scrub_extent_raid0` verifies each sector/node on its owning stripe. It can detect and log corruption but cannot recover because RAID0 has no redundancy.
- `scrub_extent_raid10` validates mirrored sub-stripes in RAID0 placement groups. It repairs bad mirrors from good mirrors when possible, falls back to sector/node-level validation when every mirror in a group initially looks bad, and writes repaired buffers back to writable devices.
- `scrub_data_extent` walks a bitmap where clear bits represent sectors with checksum coverage, splits runs into `SCRUB_UNIT` pieces, and calls `scrub_extent`.

## RAID5/RAID6 Scrubbing

RAID5/6 handling is separate because scrub must operate on full stripes with parity.

- `scrub_chunk_raid56` batches extents into contiguous stripe runs, limiting work by extent count and data volume.
- `scrub_chunk_raid56_stripe_run` builds allocation, checksum, and metadata bitmaps for the run by scanning the extent tree and checksum tree. It then reads physical stripes in bounded chunks, verifies device reads, calls RAID5 or RAID6 per-stripe logic, and writes any stripe buffers marked `rewrite`.
- `scrub_raid5_stripe` validates data/metadata sectors, recomputes XOR parity, detects parity-only errors, reconstructs a single bad data/metadata sector from parity, and logs unrecoverable cases when missing/corrupt state exceeds RAID5 tolerance.
- `scrub_raid6_stripe` validates P and Q parity, handles one- and two-error recovery using Galois-field operations, updates parity when needed, and distinguishes missing-device tolerance from actual checksum corruption.

The RAID56 code depends on helpers such as `do_xor`, `galois_double`, `galois_divpower`, `gmul`, `gdiv`, and `gpow2`, and it locks the affected chunk range while validating and rewriting.

## Chunk-Level Flow

`scrub_chunk` is the main extent walker for non-RAID56 layouts. It chooses the effective scrub layout from the chunk flags, acquires `Vcb->tree_lock` shared, walks `TYPE_EXTENT_ITEM` and `TYPE_METADATA_ITEM` records in the extent tree, loads data checksum coverage from `Vcb->checksum_root`, coalesces adjacent metadata nodes into `tree_run`s, and advances the caller’s offset after each processed extent. It intentionally caps each invocation to at most 64 extents or 128 MiB so the scrub thread can pause/stop between batches.

`scrub_thread` initializes scrub state, flushes pending writes through `do_write` when needed, snapshots writable chunks into a local work list, then iterates chunks until done or stopped. It waits on `Vcb->scrub.event` so pause/resume/stop can control forward progress, sets `c->reloc` while a chunk is being scrubbed, updates chunk counters and finish time under `stats_lock`, accumulates duration, closes the thread handle, and signals `Vcb->scrub.finished`.

## Public API Behavior

- `start_scrub` requires `SE_MANAGE_VOLUME_PRIVILEGE`, rejects locked volumes, concurrent balance, already-running scrub, and readonly mounts, initializes scrub state, and starts `scrub_thread`.
- `query_scrub` requires the same privilege, reports status/timing/progress/error fields, and serializes the variable-length scrub error list into `btrfs_query_scrub`.
- `pause_scrub` clears the scrub event and accounts elapsed duration.
- `resume_scrub` sets the event and refreshes `resume_time`.
- `stop_scrub` clears pause state, sets `stopping`, and wakes the worker.

## Integration Points

This file integrates with the driver’s extent tree, checksum tree, root/subvolume list, chunk/device model, async Windows IRP APIs, device statistics, writeback path, notification of scrub control state, and user-facing ioctl structures declared elsewhere in the driver.

Important external functions/macros include `find_item`, `find_next_item`, `read_data`, `write_data_phys`, `sync/read checksum helpers`, `check_tree_checksum`, `get_tree_checksum`, `check_sector_csum`, `get_sector_csum`, `do_calc_job`, `log_device_error`, `chunk_lock_range`, `chunk_unlock_range`, `do_write`, `free_trees`, and Btrfs layout constants.

## Risks And Notes

- The file is memory- and IRP-heavy; most paths free allocated buffers, MDLs, and IRPs, but correctness depends on every `goto end` path preserving initialized state.
- Several expressions look suspicious and should be reviewed separately: comparisons against `(uint8_t*)csum + (j + Vcb->csum_size)` where `j * Vcb->csum_size` seems intended, a check of `tp.item->key.obj_id == TYPE_EXTENT_ITEM` where `obj_type` likely matters, and `c->devices[j + j]->devobj` inside a loop over `k`.
- RAID5/6 recovery is complex and sensitive to off-by-one errors in stripe/parity mapping, especially with metadata nodes spanning multiple sectors.
- `query_scrub` serializes variable-length errors and returns `STATUS_BUFFER_OVERFLOW` when the caller buffer is too small, with `Information` set to required/used size semantics inherited from this implementation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/search.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/search.c

## Scope And Purpose

`search.c` handles Btrfs device discovery, arrival/removal notifications, encrypted-volume unlock callbacks, child volume teardown, drive-letter removal/restoration, and mount-manager monitoring. Despite the filename, this is not B-tree search logic; it is the driver’s Windows PnP and mount-manager discovery layer.

Complete file read: 1128 lines.

## Discovery And Ignore Handling

`fs_ignored` builds a registry path from the driver registry root plus the Btrfs filesystem UUID and reads a `REG_DWORD` value named `Ignore`. If set, the discovered filesystem is skipped. It allocates the UUID path dynamically, opens/creates the registry key with `ZwCreateKey`, queries the value with `ZwQueryValueKey`, and frees temporary allocations.

`test_vol` probes a `PDEVICE_OBJECT`/`PFILE_OBJECT` pair. It determines sector size, reads the primary Btrfs superblock, optionally scans backup superblocks and keeps the newest generation, verifies checksum and magic, checks the ignore registry setting, clears `DO_VERIFY_VOLUME`, and calls `add_volume_device`. If the read returns `STATUS_FVE_LOCKED_VOLUME`, it either requests retry behavior or registers a BitLocker/FVE unlock notification.

## FVE Callback Path

The file maintains `fve_data_list` under `fve_data_lock`.

- `register_fve_callback` stores the device path and registers a target-device-change notification for `GUID_IO_VOLUME_FVE_STATUS_CHANGE`.
- `event_notification` receives the FVE event, finds the stored device record, copies the path into a work-item context, and queues `fve_callback`.
- `fve_callback` retries `volume_arrival` with the callback flag set. If arrival succeeds, it unregisters the PnP notification and removes the stored record.

This defers volume probing out of the notification callback and avoids doing heavier mount logic directly in the callback context.

## Disk And Volume Arrival

`disk_arrival` handles disk-interface arrivals. It opens the device, rejects disks with partitions because partition arrivals will be considered separately, queries length and storage device number, and calls `test_vol`.

`volume_arrival` handles volume-interface arrivals. It opens the device under `boot_lock`, ignores devices created by this driver, sends `IOCTL_VOLUME_ONLINE`, queries length and storage device number, removes a whole-disk Btrfs child if a partition appears for the same disk, and then calls `test_vol`.

Both paths protect boot/discovery state with `boot_lock`.

## Removal And Child Teardown

`volume_removal` normalizes device paths with `\\?\`/`\??\` style prefixes, scans all PDOs and volume children, and removes matching non-boot children.

`remove_volume_child` is the central teardown routine. The caller must hold `pdode->child_lock` exclusively, and the function releases it before returning. It unregisters child notifications, triggers surprise removal unless degraded mode permits missing devices, disables the volume interface, restores drive letters to remaining children if appropriate, marks devices missing for degraded mounts, updates removable-media characteristics, drops object/path references, removes the child from lists, decrements `children_loaded`, and deletes the volume device when the last child disappears and no opens remain.

The function also invalidates bus relations when the PDO set changes.

## Mount Manager Coordination

`remove_drive_letter` asks mountmgr to delete mount points for a device name, using the standard two-call buffer-size pattern for `IOCTL_MOUNTMGR_DELETE_POINTS`.

`mountmgr_thread` opens `MOUNTMGR_DEVICE_NAME`, loops on `IOCTL_MOUNTMGR_CHANGE_NOTIFY`, queries current mount points on each change, and passes them to `mountmgr_updated`.

`mountmgr_updated` filters `\DosDevices\...` symbolic links, extracts their target device names, and calls `mountmgr_process_drive`.

`mountmgr_process_drive` scans known Btrfs child devices, compares their `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME` result to the mountmgr device name, removes the drive letter if the child belongs to this driver, and marks `had_drive_letter` so removal teardown can restore it later if needed.

## PnP Notification Wrappers

The file wraps notification callbacks with queued work items:

- `enqueue_pnp_callback` copies the symbolic link name and queues `do_pnp_callback`.
- `volume_notification` routes volume interface arrival/removal to `volume_arrival2` or `volume_removal`.
- `pnp_notification` routes disk interface arrival/removal to `disk_arrival` or `volume_removal`.

This avoids doing expensive probing while still in the notification callback.

## Integration Points

This file interacts with global driver state: `pdo_list`, `pdo_list_lock`, `registry_path`, `mountmgr_thread_event`, `mountmgr_thread_handle`, `shutting_down`, `busobj`, `boot_lock`, `drvobj`, and `master_devobj`. It depends on helper APIs such as `dev_ioctl`, `sync_read_phys`, `check_superblock_checksum`, `add_volume_device`, `pnp_surprise_removal`, `mountmgr_add_drive_letter`, and Windows storage/mountmgr IOCTLs.

## Risks And Notes

- `register_fve_callback` appears to leak the allocated `fve_data` if `IoRegisterPlugPlayNotification` fails, because it logs and returns without freeing `d`.
- `remove_volume_child` has non-obvious lock ownership: it releases `pdode->child_lock` internally. Callers must not release it again after this function succeeds through that path.
- PnP/mountmgr paths are race-prone by nature; this file uses locks and work items, but correctness depends on object references and list membership remaining valid across notification interleavings.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/search.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/security.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/security.c

## Scope And Purpose

`security.c` maps Unix-style Btrfs ownership metadata to Windows security descriptors and implements `IRP_MJ_QUERY_SECURITY` and `IRP_MJ_SET_SECURITY`. It also creates default security descriptors, inherits descriptors for new files, persists descriptor changes through the FCB dirty path, and derives Btrfs uid/gid values from Windows token/SID data.

Complete file read: 1012 lines.

## SID And Mapping Model

The file defines compact `sid_header` structures for common SIDs:

- BUILTIN\Administrators
- NT AUTHORITY\SYSTEM
- BUILTIN\Users
- NT AUTHORITY\Authenticated Users

`def_dacls` defines the top-level/default DACL: administrators and SYSTEM get full access, users get read/execute inheritance, authenticated users get read/write/execute/delete entries, with a FIXME for mandatory integrity labels.

External mapping state is held in `uid_map_list`, `gid_map_list`, and protected by `mapping_lock`.

`add_user_mapping` and `add_group_mapping` parse textual SID strings of the form `S-1-...`, allocate binary SID buffers, and append uid/gid mappings. They mutate the input SID string by replacing dashes with NULs while parsing.

`uid_to_sid` first checks explicit uid mappings. If none exists, uid 0 maps to SYSTEM, and other uids map to Samba-style `S-1-22-1-<uid>`.

`sid_to_uid` performs the inverse lookup: explicit mapping first, SYSTEM to uid 0, Samba `S-1-22-1-X` to `X`, otherwise `UID_NOBODY`.

`gid_to_sid` always emits Samba-style `S-1-22-2-<gid>` unless a future FIXME is implemented.

## Descriptor Creation And Loading

`load_default_acl` constructs an ACL from `def_dacls`.

`get_top_level_sd` creates an absolute security descriptor for a root/top-level FCB, sets owner from `st_uid`, group from `st_gid`, attaches the default DACL, converts it to self-relative form, and stores it in `fcb->sd`.

`fcb_get_sd` fills `fcb->sd` for an existing file:

- If requested, it first tries to load the `EA_NTACL` extended attribute.
- Without a parent, it calls `get_top_level_sd`.
- With a parent, it uses `SeAssignSecurityEx` for inherited security, converts the result to absolute form, replaces owner/group with values derived from the inode uid/gid, converts back to self-relative form, and stores the updated descriptor.

Alternate data streams use their parent file’s descriptor when queried or set.

## Query Security Dispatch

`get_file_security` calls `SeQuerySecurityDescriptorInfo` against the effective FCB security descriptor.

`drv_query_security` is the `IRP_MJ_QUERY_SECURITY` dispatch routine. It validates that the device is a filesystem VCB, checks for a CCB, enforces `READ_CONTROL` for user-mode callers, maps the caller buffer, delegates to `get_file_security`, and completes the IRP. If the descriptor does not fit, it maps `STATUS_BUFFER_TOO_SMALL` to `STATUS_BUFFER_OVERFLOW` and returns the needed length in `IoStatus.Information`.

## Set Security Dispatch

`set_file_security` applies descriptor changes:

- Rejects readonly volumes and readonly subvolumes.
- Resolves ADS operations to the parent FCB.
- Acquires the FCB resource exclusively.
- Calls `SeSetSecurityDescriptorInfo`.
- Frees the old descriptor after success.
- Updates ctime unless the user explicitly set change time.
- Updates inode transaction, sequence, root transaction/time, and dirty flags.
- Marks the FCB dirty and sends a `FILE_NOTIFY_CHANGE_SECURITY` notification.

`drv_set_security` validates the VCB/CCB, derives required access from requested security fields (`WRITE_OWNER`, `WRITE_DAC`, `ACCESS_SYSTEM_SECURITY`), enforces those rights for user-mode callers, calls `set_file_security`, and completes the IRP.

## New File Ownership And Group Selection

`search_for_gid` scans explicit gid mappings for a matching SID and writes `st_gid`.

`find_gid` chooses a new object’s gid. If the parent has `S_ISGID`, it inherits the parent gid. Otherwise it scans the caller token owner, primary group, and group list under `mapping_lock`, using the first SID found in `gid_map_list`.

`fcb_get_new_sd` creates a security descriptor for a newly created object using `SeAssignSecurityEx`, then extracts the descriptor owner and maps it back to `st_uid`; finally it calls `find_gid` to choose `st_gid`.

## Integration Points

This file connects Windows security APIs (`SeAssignSecurityEx`, `SeQuerySecurityDescriptorInfo`, `SeSetSecurityDescriptorInfo`, `Rtl*SecurityDescriptor`, token query APIs, generic file object mappings) to Btrfs inode fields (`st_uid`, `st_gid`, `st_ctime`, `st_mode`, `sequence`) and driver state (`sd_dirty`, `sd_deleted`, `inode_item_changed`, root item timestamps, dirty FCB queue, security change notification).

## Risks And Notes

- The SID string parsers modify their input buffers in place; callers must pass mutable buffers.
- `add_user_mapping` and `add_group_mapping` compute SID size from dash count. Because the authority plus subauthority parsing is hand-written, malformed SID strings may produce partially populated SID buffers rather than a clean parse failure.
- `gid_to_sid` does not consult `gid_map_list`, while `find_gid` does use it for reverse mapping from token SIDs to gids. Group SID round-tripping is therefore intentionally incomplete.
- In `fcb_get_sd`, several error paths after `SeAssignSecurityEx` can return without freeing the newly assigned `fcb->sd`; callers should treat partial descriptor setup failures carefully.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/security.c -->