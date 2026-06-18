# Group Research: group_1819_winbtrfs_sources_windows_winbtrfs_src_scrub_c_sources_windows_winbt_ff499e12d42e

Scope confirmed against `Docs/research_subset_a.md`. The source tree `sources/windows/winbtrfs` is included in subset A. All three listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/scrub.c -->
# File Research: sources/windows/winbtrfs/src/scrub.c

## Purpose

`scrub.c` implements WinBtrfs scrub support: a privileged background consistency scan that reads allocated extents, verifies checksums or tree headers, records scrub errors, and repairs recoverable corruption by rewriting good mirrored or parity-derived data. It handles single/duplicate/RAID1-like profiles, RAID0, RAID10, RAID5, and RAID6, then exposes start/query/pause/resume/stop control entry points.

## Core Data Structures

- `scrub_context_stripe`: one physical stripe read, including IRP, start, length, buffer, IO status, checksum-error flag, and computed bad checksums.
- `scrub_context`: shared completion event plus stripe array and interlocked outstanding-read count.
- `path_part`: temporary path component while reconstructing a filename for a damaged data extent.
- `scrub_context_raid56_stripe`: RAID5/6 stripe buffer, missing/rewrite state, error bitmap, and IRP state.
- `scrub_context_raid56`: RAID5/6 run bitmaps for allocated sectors, checksum-covered sectors, tree sectors, checksum bytes, parity scratch buffers, and stripe state.

## Main Behavior

- Error logging maps corrupt physical addresses back to file paths, subvolume roots, metadata roots, tree levels, and first keys where possible.
- Mirrored/duplicate profiles compare copies, validate data checksums or metadata tree checksums, then overwrite bad writable copies from a good copy.
- RAID0 validates only the owning stripe and logs failures as unrecoverable because there is no redundancy.
- RAID10 validates mirror groups, repairs from a good sub-stripe when available, and falls back to sector/tree-block recovery when all members initially look bad.
- RAID5 validates data and rotating parity with XOR, repairs parity-only errors, and reconstructs one bad data sector/tree block when possible.
- RAID6 validates data plus P/Q parity, repairs parity-only errors, reconstructs one bad/missing data block, and can reconstruct two bad data blocks with Galois-field math when no device is missing.
- `scrub_chunk()` walks extent items, loads data checksums from `checksum_root`, coalesces metadata tree runs, splits data work into 1 MiB scrub units, and dispatches by chunk profile.
- `scrub_thread()` flushes pending writes, snapshots writable chunks, processes them with pause/stop handling, updates progress counters, records duration, and signals completion.

## Public Entry Points

- `start_scrub()` requires `SE_MANAGE_VOLUME_PRIVILEGE`, rejects locked/read-only volumes, active balance, and already-running scrub, then starts a system thread.
- `query_scrub()` returns status, timing, progress, error counters, and a variable-length serialized scrub error list.
- `pause_scrub()` clears the scrub event and accumulates elapsed duration.
- `resume_scrub()` sets the event and updates resume time.
- `stop_scrub()` sets `stopping` and wakes the scrub thread.

## Notable Details

- Scrub is write-capable and repairs in place unless the target device is read-only.
- Metadata validation includes checksum and logical address checks.
- Data validation depends on checksum items; sectors without data checksums are skipped.
- RAID5/6 locks chunk ranges during read/verify/rewrite.
- `log_unrecoverable_error()` has a FIXME noting it should still log even if detailed reference expansion fails.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/search.c -->
# File Research: sources/windows/winbtrfs/src/search.c

## Purpose

`search.c` implements WinBtrfs device discovery and mount-manager integration. It reacts to PnP disk/volume notifications, probes devices for Btrfs superblocks, creates or removes WinBtrfs volume children, handles BitLocker/FVE unlock notifications, and removes native drive letters from underlying component devices when WinBtrfs owns a filesystem.

## Main Behavior

- `fs_ignored()` checks a UUID-specific registry key under `registry_path` for a DWORD `Ignore` value.
- `test_vol()` determines sector size, reads and validates Btrfs superblocks, selects the newest valid backup generation, skips ignored UUIDs, and calls `add_volume_device()`.
- Locked BitLocker/FVE volumes register a target-device change callback for `GUID_IO_VOLUME_FVE_STATUS_CHANGE`; after unlock, discovery is retried from a queued work item.
- `disk_arrival()` probes partitionless whole disks only.
- `volume_arrival()` probes volume devices, ignores devices created by WinBtrfs, brings the volume online, reads size/device number, removes a whole-disk child if a partition appears, then probes with `test_vol()`.
- `volume_removal()` finds a child by normalized PnP name and removes it unless it is marked as the boot volume.
- `remove_volume_child()` unregisters notifications, surprise-removes or marks missing devices depending on degraded-mode policy, restores removed drive letters, updates removable-media flags, frees child resources, and deletes the volume device when the last child is gone.

## Mount Manager Integration

- `remove_drive_letter()` uses `IOCTL_MOUNTMGR_DELETE_POINTS`.
- `mountmgr_process_drive()` compares mountmgr device names with WinBtrfs child mountdev names, removes matching drive letters, and remembers that they should be restored later.
- `mountmgr_updated()` scans `\DosDevices\...` mount points.
- `mountmgr_thread()` waits for mountmgr change notifications, queries mount points, processes updates, and exits during shutdown or mountmgr failure.

## Locking and Lifetime

- `boot_lock` serializes arrival/removal discovery paths.
- `pdo_list_lock` protects the global PDO list.
- Each PDO `child_lock` protects child lists.
- `fve_data_lock` protects FVE callback records.
- Queued work items own copied `UNICODE_STRING` buffers and release them after callback execution.

## Notable Details

- Superblock probing validates checksums and prefers the highest generation among valid superblocks.
- Whole-disk mounts are removed when a partition for the same disk appears.
- Degraded mounts can remain active with an internal Btrfs device marked missing.
- Underlying component drive letters are removed while WinBtrfs owns the volume and restored when appropriate.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/search.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/security.c -->
# File Research: sources/windows/winbtrfs/src/security.c

## Purpose

`security.c` bridges Btrfs POSIX ownership metadata and Windows security descriptors. It parses SID-to-UID/GID mappings, synthesizes fallback SIDs, builds default ACLs, loads or inherits file security descriptors, handles `IRP_MJ_QUERY_SECURITY` and `IRP_MJ_SET_SECURITY`, updates dirty inode state after security changes, and derives POSIX UID/GID values for new files.

## SID and ACL Handling

- Built-in SIDs are defined for Administrators, Local System, Users, and Authenticated Users.
- `def_dacls` gives Administrators and System full access, Users read/execute inheritance, and Authenticated Users read/write/execute/delete.
- `add_user_mapping()` and `add_group_mapping()` parse `S-1-...` strings into heap SIDs and append mapping records.
- `uid_to_sid()` uses configured mappings first, maps UID 0 to Local System, and otherwise uses Samba `S-1-22-1-<uid>`.
- `sid_to_uid()` reverses configured mappings, Local System, and Samba user SIDs, falling back to `UID_NOBODY`.
- `gid_to_sid()` synthesizes Samba group SIDs as `S-1-22-2-<gid>`.
- `load_default_acl()` builds an ACL from `def_dacls`.

## Security Descriptor Flow

- `get_top_level_sd()` creates a default self-relative descriptor from inode UID/GID and default ACL.
- `fcb_get_sd()` first tries the persisted `EA_NTACL` xattr, otherwise creates a top-level descriptor or inherits from the parent with `SeAssignSecurityEx()`, then overwrites owner/group from inode UID/GID.
- `fcb_get_new_sd()` assigns security during file creation, derives `st_uid` from the owner SID, and calls `find_gid()`.

## Query and Set Dispatch

- `drv_query_security()` validates the filesystem device and CCB, checks `READ_CONTROL` for user-mode callers, maps the output buffer, calls `SeQuerySecurityDescriptorInfo()`, completes the IRP, and converts too-small buffers to `STATUS_BUFFER_OVERFLOW`.
- `set_file_security()` rejects read-only volumes/subvolumes, resolves ADS streams to parent FCBs, updates `fcb->sd` with `SeSetSecurityDescriptorInfo()`, marks security and inode metadata dirty, updates ctime/transid/sequence/root ctime, and queues a security-change notification.
- `drv_set_security()` computes required access from requested owner/group/DACL/SACL flags and enforces it for user-mode callers before calling `set_file_security()`.

## GID Selection

- `find_gid()` preserves parent GID when the parent has the setgid bit.
- Otherwise it searches configured group mappings against token owner, token primary group, and token group list.

## Notable Details

- Persisted `EA_NTACL` descriptors override synthesized or inherited descriptors.
- Alternate data stream security is redirected to the parent file FCB.
- Top-level SACL/mandatory-label support is noted as incomplete.
- SID mapping parsers mutate the input SID string while parsing by replacing dashes with NUL characters.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/security.c -->