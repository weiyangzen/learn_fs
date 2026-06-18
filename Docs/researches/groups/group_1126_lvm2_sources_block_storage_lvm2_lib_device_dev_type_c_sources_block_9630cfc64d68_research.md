# Group Research: group_1126_lvm2_sources_block_storage_lvm2_lib_device_dev_type_c_sources_block_9630cfc64d68

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-type.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev-type.c

## Purpose
Implements LVM2 device type recognition, partition detection, topology/sysfs property reads, blkid filesystem probing, and signature wiping dispatch. It is the central implementation behind `dev-type.h`, mapping kernel block major names to LVM behavior and exposing helpers used by filters, PV creation, lvresize filesystem handling, and device identity logic.

## Main Responsibilities
- Defines `dev_known_types[]`, the built-in major-name table with max partition counts for sd, md, loop, device-mapper, dasd, nvme, virtio, zram, and other block drivers.
- Builds `struct dev_types` from `/proc/devices` plus optional `devices/types` config overrides in `create_dev_types`.
- Classifies device subsystems with helpers such as `dev_is_nvme`, `dev_is_scsi`, `dev_is_mpath`, `dev_is_lv`, `dev_subsystem_part_major`, and `dev_subsystem_name`.
- Detects whether a device is partitionable and whether it has an actual partition table, using sysfs, native MBR/GPT reads, DASD CDL checks, and optional udev properties.
- Resolves partition devices to primary devices with `dev_get_primary_dev`, using known major/minor partition math first and sysfs parent lookup as fallback.
- Provides blkid-backed filesystem information via `fs_block_size_and_type` and `fs_get_blkid` when `BLKID_WIPING_SUPPORT` is compiled in.
- Wipes existing signatures with blkid when enabled, otherwise falls back to native LVM checks for MD, swap, and LUKS.
- Reads Linux queue/topology attributes such as alignment offset, minimum/optimal IO size, discard limits, rotational flag, and DAX/pmem status.

## Important Control Flow
`create_dev_types` reads the block-device section of `/proc/devices`, records special majors, flags SCSI-like majors, and sets max partition counts by matching `dev_known_types[]`. Device type config entries can override or supplement built-ins.

Partition detection starts with `_is_partitionable`; it treats DM, MD, NVMe whole devices, and loop devices with `loop/partscan` as partitionable even when normal major/minor math is insufficient. `_has_partition_table` reads sector zero for MSDOS partition entries and GPT PMBR; `_has_gpt_partition_table` then reads GPT header and partition entries, counting only nonzero type GUID entries.

`dev_get_primary_dev` returns `1` when the input is already a whole/primary device and `2` when it identifies a partition's parent. NVMe bypasses major/minor arithmetic because blkext numbering does not encode parent/partition in the same way as classic disk majors.

`wipe_known_signatures` chooses the blkid implementation based on `allocation/use_blkid_wiping` and compile-time support. The blkid path repeatedly probes, prompts or skips based on flags, zeroes reported magic bytes, then steps back to verify wiped signatures.

## Dependencies
Depends on LVM device I/O helpers (`dev_read_bytes`, `dev_write_zeros`, direct block-size reads), devmapper UUID helpers, command context config, sysfs path helpers, optional libblkid, optional libudev, and external signature recognizers declared in `dev-type.h` such as MD, swap, LUKS, and DASD checks.

## Risk Notes
- Partition-table detection reads raw on-disk structures and deliberately ignores GPT PMBR alone; changes must preserve this distinction.
- Sysfs fallback paths rely on Linux `/sys/dev/block/<maj>:<min>` layout and symlink structure.
- Blkid signature wiping can be destructive; prompt/exclusion/no-prompt flags are the safety boundary.
- Topology attributes are returned in sectors after shifting byte values; invalid non-4K multiples are normalized for minimum/optimal IO size.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-type.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-type.h -->
# File Research: sources/block-storage/lvm2/lib/device/dev-type.h

## Purpose
Declares the device type, partitioning, signature detection, signature wiping, topology, and filesystem-probing interfaces implemented by `dev-type.c` and sibling device modules.

## Main Types and Constants
- `NUMBER_OF_MAJORS` is fixed at 4096, matching the 12-bit major-number space used by this code.
- `PARTITION_SCSI_DEVICE` marks majors treated as SCSI-like.
- `struct dev_type_def` stores max partition count and flags per major.
- `struct dev_types` caches known major numbers for MD, blkext, DRBD, device-mapper, EMC PowerPath, VxDMP, DASD, loop, and the full per-major table.
- Signature type flags (`TYPE_LVM1_MEMBER`, `TYPE_LVM2_MEMBER`, `TYPE_DM_SNAPSHOT_COW`) control wipe exclusions/no-prompt behavior.

## Exported API Surface
The header exposes creation of `struct dev_types`, subsystem classification, raw signature recognizers, multipath and LV DM UUID helpers, partition checks, primary-device resolution, topology reads, blkid filesystem queries, and active-LV holder detection.

## Dependencies
Includes `device.h`, metadata exports, label APIs, and platform major/minor helpers. It forward-declares `struct fs_info` so blkid filesystem functions can be declared without including `filesystem.h`.

## Risk Notes
This header is broad cross-module API. Changing idempotency, return values, or units for helpers like `dev_get_primary_dev`, `dev_is_partitioned`, or topology functions affects filters, scanning, PV creation, and lvresize paths.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev-type.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev_util.c -->
# File Research: sources/block-storage/lvm2/lib/device/dev_util.c

## Purpose
Provides small list utility functions for LVM device lists. It contains no device I/O or scanning logic; it manipulates `dm_list` containers that hold `struct device_list` or `struct device_id_list` entries.

## Main Functions
- `device_id_list_remove` removes the first `device_id_list` entry whose `dev` pointer matches.
- `device_id_list_find_dev` returns the matching `device_id_list` entry.
- `device_list_remove` removes the first `device_list` entry whose `dev` pointer matches.
- `device_list_find_dev` returns the matching `device_list` entry.
- `device_list_add` allocates a `struct device_list` from a `dm_pool`, assigns `dev`, and appends it to the list.

## Dependencies
Uses `dm_list` iteration macros, `dm_pool_alloc`, and the list wrapper structs from `device.h`.

## Risk Notes
Matching is pointer identity, not dev_t or path equality. Callers must ensure that the compared `struct device *` values come from the same dev-cache/device object universe.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/dev_util.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/device-types.h -->
# File Research: sources/block-storage/lvm2/lib/device/device-types.h

## Purpose
Declares the static known-device-type table format used by `dev-type.c` to interpret `/proc/devices` block major names.

## Main Contents
- `DEV_KNOWN_NAME_LEN` is 15, bounding the embedded name field.
- `dev_known_type_t` contains a block-device major name prefix, max partition count/granularity, and a description string.
- `extern const dev_known_type_t dev_known_types[]` declares the table defined in `dev-type.c`.

## Dependencies
Only requires `<stdint.h>`.

## Risk Notes
Names are stored in a fixed-size array. New built-in names must fit `DEV_KNOWN_NAME_LEN`, and ordering matters for prefix cases such as `mdp` before `md`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/device-types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/device.h -->
# File Research: sources/block-storage/lvm2/lib/device/device.h

## Purpose
Defines LVM2's in-memory device object model and the core device I/O API. This header is the shared contract for device cache entries, persistent device IDs, WWIDs, external device info, list wrappers, and low-level read/open/close operations.

## Main Data Structures
- Device flags describe open state, O_DIRECT state, cache membership, scan results, MD/NVMe identity, device-ID matching, and whether a preferred ID should be updated.
- `struct dev_ext` wraps optional external device information sources, currently `DEV_EXT_UDEV`.
- Device ID type constants cover sysfs WWID/serial, multipath UUID, MD UUID, loop backing file, crypt UUID, LV UUID, devname, SCSI WWID forms, and NVMe EUI64/NGUID/UUID.
- `struct dev_wwid` stores parsed SCSI/NVMe WWIDs on `dev->wwids`.
- `struct dev_id` stores one typed ID on `dev->ids`; `dev->id` points to the selected ID currently used.
- `struct dev_use` represents one devices-file entry, including matched device pointer, partition number, id type/name, devname, and PVID.
- `struct device` is the primary object containing aliases, IDs, WWIDs, dev_t, file descriptors, block sizes, cached size/end, flags, external info, duplicate preference reason, LV IDs, and PV PVID.
- `dev_io_reason_t` annotates I/O by purpose, such as signatures, labels, metadata headers/content, LV content, and logging.

## Exported API Surface
Declares external-info helpers, device size sequencing, direct block-size/size/readahead/discard operations, open/close variants, fd/name accessors, flush, multipath initialization, VPD/WWID parsing helpers, device list utilities, and `strdup_pvid`.

## Dependencies
Depends on libdevmapper list/pool/types and LVM `id.h`. Many APIs are implemented across the broader `lib/device` tree, not only in this group.

## Risk Notes
`struct device` is shared widely and uses pointer identity. Flags encode scan state and matching state that filters and label scanning depend on. ID strings and PVID buffers are handled with fixed LVM ID lengths, so allocation and termination rules matter.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/device.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/device_id.c -->
# File Research: sources/block-storage/lvm2/lib/device/device_id.c

## Purpose
Implements persistent device-ID handling for LVM's `system.devices` mechanism. It reads, writes, locks, validates, repairs, and searches device-file entries that map stable identifiers and PVIDs to actual block devices.

## Main Responsibilities
- Maintains devices-file version state, lock fd/path state, and temporary `searched_devnames` state used to suppress repeated expensive devname searches.
- Normalizes PVID strings with `strdup_pvid` so buffers are always `ID_LEN + 1`.
- Reads sysfs and DM identifiers for many ID types: sysfs WWID, sysfs serial, multipath UUID, crypt UUID, LV UUID, MD UUID, loop backing file, devname, SCSI WWIDs, and NVMe WWIDs.
- Chooses a preferred ID type in `device_id_system_read_preferred`: DM UUIDs for DM devices, loop backing file for loops, MD UUID for MD, then WWID/VPD serial, then devname fallback.
- Parses `system.devices` into `cmd->use_devices`, including `PRODUCT_UUID`, `HOSTNAME`, `REFRESH_UNTIL`, `VERSION`, hash comments, IDTYPE, IDNAME, DEVNAME, PVID, and PART fields.
- Writes `system.devices` atomically through a temporary file, version bump, hash generation, directory fsync, and optional backup retention.
- Adds or updates devices-file entries in `device_id_add`, handling duplicate PVIDs, duplicate device IDs, existing entries for the same dev, and partition entries.
- Matches devices-file entries to dev-cache objects in `device_ids_match`, with stable ID types matched before `IDTYPE=devname`.
- Validates post-scan PVIDs and devnames in `device_ids_validate`, repairing wrong PVID/devname fields, stale WWIDs, duplicate devname entries, and misplaced devname matches.
- Handles duplicate serial-number ambiguity in `device_ids_check_serial` by reading PVIDs from all devices sharing suspect serials and rematching by PVID.
- Searches for missing PVIDs in `device_ids_search`, used for renamed devname devices, refresh after machine identity change, and `lvmdevices --refresh`.
- Provides flock-based shared/exclusive devices-file locking.

## Important Control Flow
The intended command sequence is documented in the file: read devices file, scan dev-cache, match IDs to devices, label-scan matched devices, then validate PVIDs against on-disk labels.

`_match_du_to_dev` is the core matcher. It rejects incompatible major numbers and wrong partition numbers, handles DM devname aliases, normalizes old underscore-heavy sysfs IDs, repairs old swapped DM ID types, caches negative and positive ID reads on `dev->ids`, and can match a sys_wwid entry against extra VPD/NVMe WWIDs if sysfs output has changed.

`device_ids_validate` treats stable ID entries as authoritative by ID and PVID as a validation field. For `IDTYPE=devname`, PVID is the authoritative identity because devnames can move. Wrongly matched devname devices are detached and may be removed from lvmcache.

`device_ids_search` builds a list of missing PVIDs and a filtered list of unmatched system devices, optionally skipping devices that have stable IDs in `search_for_devnames=auto` mode. It reads labels from candidates, detects duplicate PVIDs, updates matching `dev_use` entries with either new devnames or new preferred IDs, and returns newly found devices for label scanning.

## Dependencies
Depends on command context settings, dev-cache iteration, filters, label/PVID reads, lvmcache updates, DM UUID helpers, VPD parsing, NVMe WWID collection, CRC helpers, device-file config, flock locking, and sysfs access helpers.

## Risk Notes
- This file is a policy hotspot: changing preferred ID ordering or matching fallback behavior changes which devices LVM accepts.
- `IDTYPE=devname` is intentionally less trusted and repaired by PVID; stable IDs are mostly trusted but serials get special duplicate handling.
- Devices-file writes must preserve version/hash/backup/lock semantics to avoid races between commands.
- Refresh behavior can intentionally reassign PVID entries to devices with new IDs after host/product identity changes, but careless broad searching can select stale clones.
- Many caches store negative reads to avoid repeated sysfs probing; callers must clear/rebuild state when device identity can change.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/device_id.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/device_id.h -->
# File Research: sources/block-storage/lvm2/lib/device/device_id.h

## Purpose
Declares the public interface for persistent device-ID and `system.devices` management implemented in `device_id.c`, plus WWID parsing and sysfs ID helpers used by other device modules.

## Main API Groups
- Memory cleanup for `dev_use`, `dev_id`, and whole lists.
- ID type conversion and metadata export helpers.
- Devices-file lifecycle: read, write, existence, touch, lock/unlock, init/exit, version check.
- Devices-file updates for PV removal, LV removal, VG UUID changes, add/update device entries, and validation/search flows.
- Lookup helpers for `dev_use` entries by devno, device pointer, PVID, devname, or typed device ID.
- System ID reads/find/list APIs for a specific device or ID.
- Sysfs block reads with partition-to-primary fallback.
- SCSI/NVMe WWID type conversion, WWID list cleanup/addition, VPD/NVMe/sysfs WWID reads, and stale PV metadata ID checking.

## Dependencies
Includes command context and `device.h`. Several declarations are implemented in this group (`device_id.c`) while NVMe read support is implemented in `nvme.c`.

## Risk Notes
This header exposes high-level policy functions used during scanning and writeback. Return values often distinguish "not found", "update needed", and "hard failure" through side effects and output parameters, so callers must follow the intended sequencing.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/device_id.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/filesystem.c -->
# File Research: sources/block-storage/lvm2/lib/device/filesystem.c

## Purpose
Implements filesystem discovery and helper-script orchestration for `lvresize --resizefs` style operations, including mounted filesystem detection, btrfs multi-device handling, LUKS/dm-crypt layers, and mounted-LV rename safety checks.

## Main Responsibilities
- Resolves the lvresize filesystem helper path from `LVRESIZE_FS_HELPER_PATH` or `global/lvresize_fs_helper_executable`.
- Finds dm-crypt holder devices above an LV by scanning `/sys/dev/block/<lv>/holders`.
- Reports whether an LV has an active crypt holder through `lv_crypt_is_active`.
- Finds mount points for normal filesystems through `/etc/mtab`, matching either mount directory `st_dev` or btrfs device `st_rdev`.
- Handles mounted btrfs by walking `/sys/fs/btrfs/<uuid>/devices` and matching each device to the LV dev_t.
- Populates `struct fs_info` with blkid data, mount state, filesystem path, crypt-layer metadata, and XFS mounted geometry corrections.
- Detects unsafe mount-state/name mismatches after LV rename by comparing `/etc/mtab`, `/proc/mounts`, `/dev/mapper/<vg-lv>`, and resolved realpaths.
- Invokes the helper executable for crypt resize, filesystem reduce, and filesystem extend operations.

## Important Control Flow
`fs_get_info` builds the LV path, stats it, gets initial blkid info, and returns `nofs` if no filesystem exists. If the LV contains `crypto_LUKS`, it locates the active crypt holder, opens it, reads its size, probes filesystem info from the crypt device, marks `needs_crypt`, records crypt dev_t and data offset, and treats the crypt device as the filesystem device.

Mounted btrfs cannot be matched only via mount directory `st_dev`, so `_btrfs_get_mnt` uses btrfs sysfs devices and then calls `_fs_get_mnt` to find the shared mount point. Mounted XFS updates `fs_last_byte` using `fs_xfs_update_size_mounted` because blkid's `FSLASTBLOCK` can be wrong for mounted XFS.

`fs_reduce_script` and `fs_extend_script` construct argv arrays for `lvresize_fs_helper`, adding flags for fstype, LV path, new size, mount dir, unmount/mount/fsck/remount requirements, and optional crypt resize. They do not perform filesystem-specific operations directly.

## Dependencies
Depends on blkid wrappers from `dev-type.c`, `struct fs_info` from `filesystem.h`, device-mapper path helpers, crypt table offset helper, mount table APIs, sysfs paths, and `exec_cmd`.

## Risk Notes
- Crypt holder detection assumes a single relevant `dm-*` holder and does not verify the holder DM UUID as crypt.
- LV rename detection is conservative; inconsistencies between mtab/proc paths abort resizing to avoid filesystem utility failures.
- Helper argv capacity is fixed by `FS_CMD_MAX_ARGS`; adding flags requires preserving bounds.
- btrfs multi-device matching treats one mount entry as shared across devices and requires both device presence and mount point discovery.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/filesystem.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/filesystem.h -->
# File Research: sources/block-storage/lvm2/lib/device/filesystem.h

## Purpose
Declares filesystem resize/discovery data structures and APIs used by LVM lvresize code.

## Main Types
`struct fs_info` stores target size, filesystem type, mount directory, filesystem UUID, actual filesystem device path, filesystem block size, last filesystem byte, crypt offset/dev_t/size, and state bits for no filesystem, mounted/unmounted, resize direction, fsck, unmount/mount, and crypt handling.

## Exported API Surface
Declares `fs_get_info`, filesystem extend/reduce helper invocations, crypt resize helper invocation, LV rename/mount-state safety check, active-crypt check, and mounted-XFS size correction.

## Dependencies
Uses `device.h`, Linux `PATH_MAX`, and forward declarations for command context and logical volumes.

## Risk Notes
`fs_info` mixes detected state and planned operation flags. Callers must initialize it and set resize intent fields consistently before invoking helper scripts.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/filesystem.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/filesystem_xfs.c -->
# File Research: sources/block-storage/lvm2/lib/device/filesystem_xfs.c

## Purpose
Provides the mounted-XFS size correction used by `filesystem.c` when blkid may report inaccurate `FSLASTBLOCK` for mounted XFS filesystems.

## Main Behavior
`fs_xfs_update_size_mounted` opens the XFS mount directory, issues `XFS_IOC_FSGEOMETRY`, and replaces `fsi->fs_last_byte` with `geo.blocksize * geo.datablocks`.

## Portability Handling
If `<xfs/xfs.h>` is available, the file uses the system XFS definitions. Otherwise, it defines the ioctl number and a minimal compatible `struct xfs_fsop_geom` containing the fields needed by LVM.

## Dependencies
Depends on `filesystem.h`, LVM logging, `open`, `ioctl`, and `close`.

## Risk Notes
The fallback struct assumes stable basic XFS geometry layout. Failure to open or query the mount directory leaves XFS size correction unavailable and causes `fs_get_info` to fail for the mounted-XFS correction path.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/filesystem_xfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/nvme.c -->
# File Research: sources/block-storage/lvm2/lib/device/nvme.c

## Purpose
Implements optional libnvme support for reading NVMe namespace identifiers and persistent reservation information. When `NVME_SUPPORT` is absent, it provides no-op/failing stubs with the same public API.

## Main Responsibilities
- Reads NVMe namespace IDs and identify data from an opened block device.
- Extracts NGUID, EUI64, and UUID identifiers and stores them as LVM `dev_wwid` entries with standard prefixes.
- Reads namespace descriptor lists for NVMe 1.3+ controllers to collect additional identifiers.
- Translates NVMe reservation types to LVM persistent-reservation types.
- Reads reservation reports to identify reservation type and, where applicable, holder key.
- Searches registered reservation keys by exact key, host-id suffix, or returns all keys/counts.

## Important Control Flow
`dev_read_nvme_wwids` marks `DEV_ADDED_NVME_WWIDS`, opens `dev_name(dev)`, gets the NSID, reads namespace identify data, saves nonzero NGUID/EUI64, checks controller version before descriptor reads, then walks `NVME_IDENTIFY_DATA_SIZE` descriptor data by descriptor length. Identifiers are formatted as `uuid.<uuid>`, `eui.<32 hex>` for NGUID, or `eui.<16 hex>` for EUI64.

Reservation readers allocate an 8192-byte report buffer, call `nvme_resv_report` with extended data status, clamp reported registration count to buffer capacity, and then inspect registered keys and holder status.

## Dependencies
Depends on `device.h`, `device_id.h`, persistent reservation definitions from `persist.h`, endian helpers, aligned allocation, and optional `<libnvme.h>`.

## Risk Notes
- Identifier formatting is part of device-ID matching compatibility; changes can invalidate existing `system.devices` entries.
- Descriptor iteration trusts `cur->nidl` for progress after each descriptor; invalid device/kernel data must not cause infinite loops.
- Reservation report parsing uses a fixed-size buffer for up to 127 keys and clamps excessive registration counts.
- Stub builds silently provide no NVMe WWID enrichment and no reservation support.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/online.c -->
# File Research: sources/block-storage/lvm2/lib/device/online.c

## Purpose
Manages transient `/run` online-state files used by pvscan/autoactivation to record online PVs and VGs. These files are not persistent metadata; they coordinate activation behavior and avoid losing context between udev-triggered scans.

## File Formats and Directories
PV online files live under `PVS_ONLINE_DIR` with filename equal to the PVID. Contents begin with `<major>:<minor>\n` and may include `vg:<vgname>\n` and `dev:<devname>\n`. VG online files live under `VGS_ONLINE_DIR`. Lookup files under `PVS_LOOKUP_DIR` map a VG to PVIDs when PV online files lack VG names.

## Main Functions
- `online_pvid_file_read` parses a PV online file, validates optional VG name and devname fields, and returns dev numbers.
- `get_pvs_online` lists PV online files, optionally filtered by VG name.
- `online_vg_file_create` and `online_vg_file_remove` create/remove VG online markers.
- `online_pvid_file_create` writes a PV online file atomically with `O_EXCL`, detects duplicate PVIDs when an existing file names a different devno, and logs pvscan-aware errors.
- `online_pvid_file_exists` checks whether a PVID file exists.
- `get_pvs_lookup` reads a VG lookup file and resolves listed PVIDs through PV online files.
- `online_dir_setup` creates the required run directories.
- `online_lookup_file_remove` removes a VG lookup file.
- `online_vgremove` removes VG and PV online files for a removed VG.

## Dependencies
Depends on defaults for online directory paths, `struct device`, PVID/VG name lengths, `validate_name`, and pvscan-aware logging macros declared in `online.h`.

## Risk Notes
- Online files are intentionally not fsynced because they are transient `/run` state.
- Duplicate PVID detection prevents autoactivation from blindly accepting a second device with the same PVID.
- Optional `dev:` is required to start with `/dev/`; optional `vg:` must pass LVM name validation.
- `online_vg_file_remove` removes the VG marker when any PV goes offline so a complete VG can be activated again later.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/online.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/online.h -->
# File Research: sources/block-storage/lvm2/lib/device/online.h

## Purpose
Declares pvscan online-state structures, logging wrappers, and APIs for transient PV/VG online files.

## Main Contents
- `struct pv_online` stores list linkage, optional matched device pointer, devno, PVID, VG name, and devname from online files.
- `log_print_pvscan` and `log_error_pvscan` avoid duplicate `pvscan[pid]` prefixes when output is already going to udev/journal style output.
- Function declarations cover PV online file read/create/exists, VG online create/remove, directory setup, PV online listing, VG lookup listing, list cleanup, lookup-file removal, and VG removal cleanup.

## Dependencies
Includes command context and device definitions for ID/name lengths and device objects.

## Risk Notes
The logging macros depend on `cmd->udevoutput`; callers outside pvscan-like contexts should ensure the command context is valid.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/online.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/device/parse_vpd.c -->
# File Research: sources/block-storage/lvm2/lib/device/parse_vpd.c

## Purpose
Parses and normalizes SCSI VPD page data into LVM device WWID/serial strings. This supports stable device IDs and multipath/WWID matching.

## Main Functions
- `format_general_id` trims leading/trailing spaces, replaces individual internal spaces with underscores, and skips quotes, non-ASCII, and non-printable characters.
- `format_t10_id` performs similar cleanup for T10 IDs but collapses a run of spaces into a single underscore.
- `_to_hex` converts binary identifier bytes to lowercase hex.
- `parse_vpd_ids` walks VPD page 0x83 designators and adds T10, EUI, NAA, or SCSI-name-string IDs to a `dev_wwid` list.
- `parse_vpd_serial` parses VPD page 0x80 serial data, strips surrounding whitespace, bounds length, and writes a NUL-terminated serial.

## Important Control Flow
`parse_vpd_ids` starts after the four-byte VPD header and advances by `d[3] + 4` for each designator. It recognizes designator types 0x1 (T10 vendor ID), 0x2 (EUI-64/12/16-byte EUI), 0x3 (NAA 8/16-byte), and 0x8 (SCSI name string). SCSI name strings beginning with `eui.` or `naa.` are lowercased and categorized as EUI/NAA; other SCSI name strings are stored with type 8 for multipath checking but are not standard device-ID types.

## Dependencies
Depends on `device.h` and `device_id.h` for `DEV_WWID_SIZE` and `dev_add_scsi_wwid`.

## Risk Notes
- Output normalization must remain compatible with existing `system.devices` IDNAME values.
- The parser clamps overlong T10/name designators to the available buffer but relies on well-formed page iteration lengths.
- `parse_vpd_serial` reads length from bytes 2 and 3 and trims using `in + 4`; callers must pass enough VPD data for that header.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/device/parse_vpd.c -->