# Group Research: group_673_libblockdev_sources_virtualization_libblockdev_src_plugins_fs_ext_c__26e609dfb644

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ext.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/ext.c

Implements libblockdev filesystem plugin support for ext2, ext3, and ext4. The file is mostly a shared implementation with thin per-version wrappers.

Key entry points:
- `bd_fs_ext_is_tech_avail()` maps requested filesystem modes to required utilities: `mke2fs`, `e2fsck`, `tune2fs`, and `resize2fs`.
- `bd_fs_ext{2,3,4}_mkfs()` creates filesystems through `mke2fs -t extN`.
- `bd_fs_ext{2,3,4}_check()` runs `e2fsck -f -n`, optionally with `-C 1` progress output.
- `bd_fs_ext{2,3,4}_repair()` runs `e2fsck -f -p` or unsafe `-y`.
- `bd_fs_ext{2,3,4}_set_label()` and `_set_uuid()` use `tune2fs`.
- `bd_fs_ext{2,3,4}_get_info()` reads superblock data through libext2fs.
- `bd_fs_ext{2,3,4}_resize()` runs `resize2fs`.
- `bd_fs_ext{2,3,4}_get_min_size()` parses `resize2fs -P`.

Core mechanics:
- Shared helpers perform nearly all work, with ext2/ext3/ext4 wrappers reusing the same code paths.
- `extract_e2fsck_progress()` parses e2fsck progress lines with a cached `GRegex` and maps five e2fsck stages onto 0-100%.
- `ext_mkfs_options()` converts generic mkfs options into `mke2fs` arguments: label, UUID, dry run, no discard, force, plus caller-supplied extra args.
- `ext_get_info()` opens the filesystem with libext2fs flags including superblock-only and checksum-ignore behavior, then extracts label, UUID, state, block size, block count, and free block count.
- `ext_get_min_size()` multiplies the `resize2fs -P` minimum block count by the current filesystem block size.

Important invariants:
- Ext labels are capped at 16 characters.
- UUID format validation delegates to common `check_uuid()`.
- A `NULL` UUID for set-uuid means `tune2fs -U random`.
- Resize sizes are converted from bytes to 512-byte-sector syntax expected by `resize2fs`.
- e2fsck exit codes 1 and 2 are treated as successful repair outcomes; check exit code 4 means errors left uncorrected but not an execution failure.

Filesystem/block relevance:
- This file is the ext-family adapter between libblockdev’s stable API and the ext userspace toolchain plus libext2fs superblock access.

Notable risks:
- Progress parsing assumes e2fsck’s numeric `-C` output format.
- Minimum-size parsing depends on localized/string output beginning with `Estimated minimum size`.
- The generic dispatcher calls the ext4 wrappers for all ext2/ext3/ext4 runtime operations, relying on tool compatibility.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ext.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ext.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/ext.h

Declares the public ext2/ext3/ext4 API surface used by the libblockdev filesystem plugin.

Key contents:
- Defines shared `BDFSExtInfo` with `label`, `uuid`, `state`, `block_size`, `block_count`, and `free_blocks`.
- Typedefs `BDFSExt2Info`, `BDFSExt3Info`, and `BDFSExt4Info` to the same struct.
- Declares copy/free helpers for each typedef.
- Declares mkfs, check, repair, label, UUID, info, resize, and minimum-size APIs for ext2, ext3, and ext4.

Important invariants:
- The three ext family info types are ABI-distinct by name but structurally identical.
- Callers own returned info structs and must free them with the matching free helper.
- All operational functions accept `GError **` and return GLib-style success/failure values.

Filesystem/block relevance:
- This header exposes ext-family block filesystem management operations to generic dispatch and external users.

Notable risks:
- Because all ext info types alias one struct, future ext-version-specific fields would require ABI care.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/f2fs.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/f2fs.c

Implements F2FS support for libblockdev’s filesystem plugin.

Key entry points:
- `bd_fs_f2fs_is_tech_avail()` checks mode support and utility availability.
- `bd_fs_f2fs_mkfs()` runs `mkfs.f2fs`.
- `bd_fs_f2fs_check()` runs `fsck.f2fs --dry-run`.
- `bd_fs_f2fs_repair()` runs `fsck.f2fs -a`.
- `bd_fs_f2fs_get_info()` combines `dump.f2fs` parsing with common UUID/label probing.
- `bd_fs_f2fs_resize()` runs `resize.f2fs`, optionally in safe shrink mode.
- `bd_fs_f2fs_check_label()` enforces F2FS label length.

Core mechanics:
- Dependency checks include versioned checks for `fsck.f2fs >= 1.11.0` for check mode and `resize.f2fs >= 1.12.0` for safe shrink.
- `can_check_f2fs_version()` special-cases old tools whose version cannot be queried and reports them as too old.
- `bd_fs_f2fs_mkfs_options()` maps label, no-discard, and force to `mkfs.f2fs` options.
- `bd_fs_f2fs_get_info()` parses sector size, total filesystem sectors, and superblock feature bits from `dump.f2fs`.
- Resize refuses shrink without `safe=TRUE` because `resize.f2fs` may otherwise print an error but return success.

Important invariants:
- Setting label or UUID on an existing F2FS device is reported unsupported.
- F2FS resize sizes are in filesystem sectors, not bytes.
- Missing sector-size output is tolerated for `dump.f2fs` 1.15 by setting `sector_size` to 0.
- F2FS labels are capped at 512 characters.

Filesystem/block relevance:
- Provides F2FS creation, check/repair, metadata query, and resize support through the f2fs-tools command set.

Notable risks:
- Info parsing depends on exact `dump.f2fs` text prefixes.
- Safe shrink behavior depends on tool version detection.
- A zero sector size from older `dump.f2fs` output can prevent byte-to-sector conversion in generic resize paths.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/f2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/f2fs.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/f2fs.h

Declares F2FS feature flags, info data, and libblockdev F2FS operations.

Key contents:
- Defines `BDFSF2FSFeature` bit flags mirroring F2FS superblock feature bits such as encryption, zoned block support, quota, verity, and checksum features.
- Defines `BDFSF2FSInfo` with `label`, `uuid`, `sector_size`, `sector_count`, and `features`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, info, resize, and label validation APIs.

Important invariants:
- `sector_count` and resize sizes use F2FS sectors.
- The feature field is a raw bitmask exposed to callers.
- Existing-device label and UUID setters are intentionally absent.

Filesystem/block relevance:
- Exposes F2FS metadata and operation APIs to the generic filesystem layer.

Notable risks:
- Feature enum values must stay aligned with upstream `f2fs_fs.h`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/f2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/generic.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/generic.c

Implements generic filesystem plugin operations: supported-filesystem metadata, probing, wiping, dispatch to filesystem-specific modules, capability queries, mkfs option routing, mount-assisted operations, and freeze/thaw.

Key entry points:
- `bd_fs_supported_filesystems()` returns the filesystem names supported by this plugin.
- `bd_fs_wipe()` and `bd_fs_clean()` remove signatures with libblkid.
- `bd_fs_get_fstype()` probes the first filesystem signature using libblkid.
- `bd_fs_resize()`, `bd_fs_repair()`, `bd_fs_check()`, `bd_fs_set_label()`, and `bd_fs_set_uuid()` dispatch by explicit or detected filesystem type.
- `bd_fs_get_size()`, `bd_fs_get_free_space()`, and `bd_fs_get_min_size()` dispatch to filesystem-specific info/min-size APIs.
- `bd_fs_can_*()` functions report tool availability and feature support.
- `bd_fs_mkfs()` builds filesystem-specific mkfs extra args from `BDFSMkfsOptions`.
- `bd_fs_features()` returns static feature metadata.
- `bd_fs_freeze()` and `bd_fs_unfreeze()` issue `FIFREEZE` / `FITHAW` ioctls on mountpoints.

Core mechanics:
- Static `fs_features[]` records resize modes, mkfs option support, fsck support, configure support, ownership/partition-table semantics, partition IDs/GUIDs, and min/max size for each known filesystem.
- Static `fs_info[]` maps filesystem names to required utility names for mkfs, check, repair, resize, label, query, UUID, and min-size operations.
- `fstype_to_tech()` maps strings like `ext4`, `xfs`, `vfat`, `ntfs`, `f2fs`, `nilfs2`, `btrfs`, `udf`, and `exfat` into plugin tech IDs.
- `device_operation()` centralizes operation dispatch and reports unsupported operations with operation-specific wording.
- `fs_mount()` mounts devices to temporary directories when an operation requires a mounted filesystem, preserving existing mounts when already mounted.
- XFS quota flags are queried through `xfs_db` and translated into mount options when temporary-mounting XFS.
- XFS, NILFS2, and Btrfs have special mount-assisted resize/info/label paths.
- `query_fs_operation()` powers capability queries by checking static support and whether the required executable exists.

Important invariants:
- Generic mkfs is handled separately from `device_operation()`.
- Generic size/free/min-size functions return 0 on error and set `GError`.
- XFS resize input is converted from bytes to filesystem blocks before `xfs_growfs`.
- F2FS resize input is converted from bytes to filesystem sectors and shrink forces safe mode.
- Btrfs info and some operations require temporary mounting.
- Freeze/thaw first validates that the path is a mountpoint.

Filesystem/block relevance:
- This is the central policy and dispatch layer for the filesystem plugin. It links block-device probing, signature wiping, filesystem-specific tools, capability reporting, and mount-aware operations.

Notable risks:
- Static capability data can drift from filesystem-tool behavior.
- Several query paths depend on text output parsers in filesystem-specific modules.
- Temporary mount/unmount failures after successful operations can turn an otherwise successful operation into a reported failure.
- `bd_fs_get_fstype()` rejects non-filesystem signatures even when libblkid detects other useful block metadata.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/generic.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/generic.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/generic.h

Declares generic filesystem plugin APIs, mkfs option structures, feature flags, and capability-query functions.

Key contents:
- Declares signature wiping/cleaning and filesystem-type probing.
- Declares freeze/unfreeze APIs.
- Defines `BDFSMkfsOptionsFlags` and `BDFSMkfsOptions`.
- Declares generic mkfs, resize, repair, check, label, UUID, size, free-space, and min-size APIs.
- Defines resize, configure, fsck, and filesystem feature flag enums.
- Defines `BDFSFeatures`, including partition type metadata and min/max size.
- Declares capability functions such as `bd_fs_can_mkfs()`, `bd_fs_can_resize()`, and `bd_fs_can_get_info()`.

Important invariants:
- `BDFSMkfsOptions` includes reserved padding for ABI stability.
- Feature/capability flags are bitmasks consumed by callers to decide UI/API behavior.
- Generic operation functions accept an optional filesystem type; `NULL` means detect from the device.

Filesystem/block relevance:
- This is the public generic API surface for filesystem operations across supported local filesystems.

Notable risks:
- The declared generic API hides substantial per-filesystem differences, so callers must inspect feature/capability flags before assuming behavior.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/generic.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/mount.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/mount.c

Implements libblockdev mount/unmount helpers and mount table queries using libmount.

Key entry points:
- `bd_fs_mount()` mounts a device or fstab-specified entry.
- `bd_fs_unmount()` unmounts a device or mountpoint, with optional lazy/force flags.
- `bd_fs_get_mountpoint()` returns one mountpoint for a mounted device.
- `bd_fs_is_mountpoint()` checks whether a path is a mountpoint.

Core mechanics:
- `MountArgs` carries device, mountpoint, fstype, options, unmount spec, lazy, and force values.
- `do_mount()` builds a libmount context, sets source/target/fstype/options, performs the mount, then translates libmount/syscall/helper errors.
- `do_unmount()` builds a libmount context, enables lazy/force if requested, performs unmount, and translates errors.
- Separate old/new libmount error paths are compiled depending on `LIBMOUNT_NEW_ERR_API`.
- On old libmount, read-only fallback is implemented manually for some `EROFS`/`EACCES` cases.
- `run_as_user()` forks and runs mount/unmount in a child after changing real UID/GID, returning serialized error text through a pipe.
- `bd_fs_mount()` and `bd_fs_unmount()` parse supported extra args: `run_as_uid` and `run_as_gid`.

Important invariants:
- Mount requires at least a device or a mountpoint.
- UID/GID delegation requires the process to be effectively root.
- Unsupported extra args are rejected.
- Mount/unmount error codes are normalized to `BD_FS_ERROR` values, including auth and unknown filesystem cases.
- Mountpoint lookup uses parsed mtab with a libmount cache.

Filesystem/block relevance:
- This file is the filesystem plugin’s bridge to kernel mounts, needed directly by user APIs and indirectly by generic operations that require online filesystems.

Notable risks:
- Error behavior differs by libmount API version.
- Error propagation through child exit status is limited by `BD_FS_ERROR` code ranges and pipe serialization.
- `bd_fs_get_mountpoint()` returns only one mountpoint when a source is mounted multiple times.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/mount.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/mount.h

Declares the libblockdev mount helper API.

Key contents:
- `bd_fs_unmount()` for lazy/force unmounts with optional extra args.
- `bd_fs_mount()` for mounting by device and/or mountpoint with optional fstype/options/extra args.
- `bd_fs_get_mountpoint()` for source-to-target lookup.
- `bd_fs_is_mountpoint()` for mountpoint validation.

Filesystem/block relevance:
- Exposes mount operations and mount table queries to the generic filesystem plugin.

Notable risks:
- The compact API does not expose all libmount options directly; extensibility is via validated `BDExtraArg` keys.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/nilfs.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/nilfs.c

Implements NILFS2 support for libblockdev’s filesystem plugin.

Key entry points:
- `bd_fs_nilfs2_is_tech_avail()` checks supported modes and required utilities.
- `bd_fs_nilfs2_mkfs()` runs `mkfs.nilfs2 -q`.
- `bd_fs_nilfs2_set_label()` and `_set_uuid()` use `nilfs-tune`.
- `bd_fs_nilfs2_get_info()` parses `nilfs-tune -l`.
- `bd_fs_nilfs2_resize()` runs `nilfs-resize -y`.
- `bd_fs_nilfs2_check_label()` and `_check_uuid()` validate label/UUID values.

Core mechanics:
- Dependencies are `mkfs.nilfs2`, `nilfs-tune`, and `nilfs-resize`.
- Check and repair modes are explicitly unsupported.
- Mkfs options map label, dry run, no-discard, force, and extra args.
- A `NULL` UUID generates a UUID locally with libuuid, then passes it to `nilfs-tune -U`.
- Info parsing extracts block size, device size, and free block count from colon-prefixed `nilfs-tune` output, while UUID/label come from common probing.
- Resize accepts optional byte size and passes it directly to `nilfs-resize`.

Important invariants:
- NILFS2 labels are capped at 80 characters.
- NILFS2 resize is documented as requiring the filesystem to be mounted; generic code handles temporary mounting.
- No fsck/check/repair operation is provided.

Filesystem/block relevance:
- Provides user-space NILFS2 management through nilfs-utils tools, especially online resize and metadata query.

Notable risks:
- Info parsing depends on exact `nilfs-tune -l` line prefixes.
- Generated UUIDs depend on local libuuid behavior rather than nilfs-utils random generation.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/nilfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/nilfs.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/nilfs.h

Declares NILFS2 info data and operations.

Key contents:
- Defines `BDFSNILFS2Info` with `label`, `uuid`, `size`, `block_size`, and `free_blocks`.
- Declares copy/free helpers.
- Declares mkfs, label, UUID, info, and resize APIs.

Important invariants:
- Check and repair APIs are absent because NILFS2 support reports them unavailable.
- Returned info structs are caller-owned.

Filesystem/block relevance:
- Exposes NILFS2 filesystem management to generic dispatch and callers.

Notable risks:
- The API exposes total device size and free block count, but not a total block count field.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ntfs.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/ntfs.c

Implements NTFS support through ntfs-3g/ntfsprogs utilities.

Key entry points:
- `bd_fs_ntfs_is_tech_avail()` checks utility dependencies.
- `bd_fs_ntfs_mkfs()` runs `mkntfs -f -F`.
- `bd_fs_ntfs_check()` runs `ntfsfix -n`.
- `bd_fs_ntfs_repair()` runs `ntfsfix -d`.
- `bd_fs_ntfs_set_label()` uses `ntfslabel`.
- `bd_fs_ntfs_set_uuid()` changes NTFS serial number through `ntfslabel`.
- `bd_fs_ntfs_get_info()` parses `ntfsinfo -m`.
- `bd_fs_ntfs_resize()` and `_get_min_size()` use `ntfsresize`.

Core mechanics:
- Dependencies are `mkntfs`, `ntfsfix`, `ntfsresize`, `ntfslabel`, and `ntfsinfo`.
- Mkfs options support label and dry run plus extra args.
- Check treats `ntfsfix` exit code 1 as “recoverable errors detected” without reporting an execution error.
- UUID validation accepts 8- or 16-character hexadecimal NTFS serial formats.
- `bd_fs_ntfs_set_uuid()` uses `--new-serial`, `--new-serial=<16 hex>`, or `--new-half-serial=<8 hex>`.
- Info queries reject mounted devices before running `ntfsinfo`.
- Info parsing extracts cluster size, volume size in clusters, and free clusters, then converts to bytes.
- Minimum-size parsing reads `You might resize at ... bytes` from `ntfsresize --info`.

Important invariants:
- NTFS labels are capped at 128 characters.
- NTFS info requires the device not to be mounted.
- Resize size is passed in bytes to `ntfsresize -s`.

Filesystem/block relevance:
- Adapts NTFS creation, basic consistency handling, serial/label management, size/free-space query, and resizing for block devices.

Notable risks:
- `ntfsfix` is not a full Windows chkdsk replacement; the API names it repair/check but behavior is utility-limited.
- Output parsing depends on `ntfsinfo` and `ntfsresize` English text.
- Mounted-device detection depends on libblockdev mount lookup.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ntfs.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/ntfs.h

Declares NTFS info data and operations.

Key contents:
- Defines `BDFSNtfsInfo` with `label`, `uuid`, `size`, and `free_space`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, label, UUID, info, resize, and minimum-size APIs.

Important invariants:
- NTFS UUID refers to the volume serial number format, not an RFC UUID.
- Returned size/free-space values are byte counts.

Filesystem/block relevance:
- Exposes NTFS management functionality to the generic filesystem plugin.

Notable risks:
- There is a minor declaration formatting inconsistency in `bd_fs_ntfs_check_uuid ( const gchar *uuid, ...)`, but it is semantically harmless.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/udf.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/udf.c

Implements UDF filesystem support.

Key entry points:
- `bd_fs_udf_is_tech_avail()` checks support and dependencies.
- `bd_fs_udf_mkfs()` runs `mkudffs`.
- `bd_fs_udf_set_label()` uses `udflabel` and sets both logical volume identifier and volume identifier.
- `bd_fs_udf_set_uuid()` uses `udflabel --uuid`.
- `bd_fs_udf_get_info()` parses `udfinfo --utf8`.
- `bd_fs_udf_check_label()` and `_check_uuid()` validate UDF label and UUID formats.

Core mechanics:
- Dependencies are `mkudffs`, `udflabel`, and `udfinfo`.
- Check, repair, and resize are explicitly unsupported.
- `get_vid()` derives a valid UDF Volume Identifier from a label, truncating based on UDF character-width rules.
- Mkfs option generation maps label to `--lvid` plus derived `--vid`, UUID to `-u`, and preserves extra args.
- `bd_fs_udf_mkfs()` chooses block size from the caller or device logical block size via `BLKSSZGET`; defaults media type to `hd` and revision to `0x201`.
- Label validation distinguishes ASCII, valid UTF-8, and Unicode characters above U+00FF.
- UUID validation requires 16 lowercase hexadecimal characters.
- `parse_udf_vars()` parses `key=value` output from `udfinfo`, ignoring `start=` lines.
- Info extraction reads UDF revision, VID, LVID, block size, total blocks, free blocks, then adds UUID/label via common probing.

Important invariants:
- UDF logical volume labels can be up to 126 ASCII/compatible chars, but labels containing characters above U+00FF are limited to 63 chars.
- UDF VID is stricter than LVID and is truncated before being passed to tools.
- UUID randomization uses `udflabel --uuid=random`.
- No check/repair/resize path is advertised.

Filesystem/block relevance:
- Provides UDF creation, metadata labeling, UUID setting, and information query for optical/media-style and partition-table-capable filesystems.

Notable risks:
- UTF-8/VID truncation rules are subtle and may surprise callers expecting exact label round trips.
- `parse_udf_vars()` transfers split-string ownership into the hash table; changes here need careful memory handling.
- Info parsing depends on `udfinfo` key names.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/udf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/udf.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/udf.h

Declares UDF info data and operations.

Key contents:
- Defines `BDFSUdfInfo` with label, UUID, revision, logical volume ID, volume ID, block size, block count, and free blocks.
- Declares copy/free helpers.
- Declares mkfs, set/check label, set/check UUID, and get-info APIs.

Important invariants:
- UDF check, repair, and resize APIs are absent.
- UDF exposes both user-facing label/UUID and lower-level UDF identifiers.

Filesystem/block relevance:
- Exposes UDF metadata management and creation to the generic filesystem layer.

Notable risks:
- The UUID checker declaration has a harmless extra space before `const`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/udf.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/vfat.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/vfat.c

Implements VFAT/FAT filesystem support through dosfstools-style utilities.

Key entry points:
- `bd_fs_vfat_is_tech_avail()` checks required utilities and versioned UUID support.
- `bd_fs_vfat_mkfs()` runs `mkfs.vfat`.
- `bd_fs_vfat_check()` runs `fsck.vfat -n`.
- `bd_fs_vfat_repair()` runs `fsck.vfat -a`.
- `bd_fs_vfat_set_label()` and `_set_uuid()` use `fatlabel`.
- `bd_fs_vfat_get_info()` parses `fsck.vfat -nv`.
- `bd_fs_vfat_resize()` runs `vfat-resize`.

Core mechanics:
- Dependencies include `mkfs.vfat`, `fatlabel`, `fsck.vfat`, `vfat-resize`, and `fatlabel >= 4.2` for UUID setting.
- `_fix_uuid()` accepts udev-style volume IDs like `2E24-EC82` and converts them to 8 hex digits.
- Mkfs options uppercase labels, support volume ID, force, optional `--mbr=no` for newer `mkfs.vfat`, and extra args.
- Label setting uppercases non-empty labels and uses `--reset` for empty labels with newer fatlabel.
- Check treats exit code 1 as recoverable filesystem errors rather than command failure.
- Repair reruns fsck after exit code 1 to verify the filesystem is clean after correction.
- Info parsing extracts bytes per cluster and used/total cluster counts from fsck output, then computes free clusters.
- Resize passes an optional byte size to `vfat-resize`.

Important invariants:
- VFAT labels are at most 11 characters and must not contain `"*/:<>?\\|`.
- VFAT UUID/volume ID must fit in 32 bits and may be `NULL` for reset/random behavior depending on operation.
- FAT labels are normalized to uppercase by mkfs/set-label helpers.
- Generic feature metadata marks VFAT as partition-table-oriented and supports offline grow/shrink.

Filesystem/block relevance:
- Provides FAT-family creation, checking, repair, label/volume-ID management, size/free-space query, and resize behavior for block devices.

Notable risks:
- Info parsing assumes specific `fsck.vfat -nv` output formatting and device-prefix lines.
- Version-gated behavior around FAT partition tables and UUID changes depends on dosfstools output parsing.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/vfat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/vfat.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/vfat.h

Declares VFAT info data and operations.

Key contents:
- Defines `BDFSVfatInfo` with `label`, `uuid`, `cluster_size`, `cluster_count`, and `free_cluster_count`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, label, UUID, info, and resize APIs.

Important invariants:
- Size calculations are based on cluster size and cluster counts.
- UUID means FAT volume ID, not a standard UUID.

Filesystem/block relevance:
- Exposes VFAT management operations to generic dispatch.

Notable risks:
- Callers must account for FAT label uppercasing and short label limits.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/vfat.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/xfs.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/xfs.c

Implements XFS support through xfsprogs utilities.

Key entry points:
- `bd_fs_xfs_is_tech_avail()` checks XFS utility dependencies.
- `bd_fs_xfs_mkfs()` runs `mkfs.xfs`.
- `bd_fs_xfs_check()` runs `xfs_repair -n`.
- `bd_fs_xfs_repair()` runs `xfs_repair`.
- `bd_fs_xfs_set_label()` and `_set_uuid()` use `xfs_admin`.
- `bd_fs_xfs_get_info()` uses `xfs_spaceman info` for mounted filesystems or `xfs_db -r -c info` for unmounted devices.
- `bd_fs_xfs_resize()` runs `xfs_growfs`.

Core mechanics:
- Dependencies are `mkfs.xfs`, `xfs_db`, `xfs_repair`, `xfs_admin`, and `xfs_growfs`.
- Mkfs options map label, metadata UUID, dry run, no-discard, force, and extra args.
- Check treats a nonzero `xfs_repair -n` exit as “filesystem not clean” rather than a command error when the utility itself ran.
- Empty labels are passed to `xfs_admin -L --`.
- A `NULL` UUID maps to `xfs_admin -U generate`.
- Info first obtains UUID/label via common probing, then parses block size and block count from an XFS `data` line.
- Mounted filesystems use `xfs_spaceman` to avoid stale `xfs_db` data; unmounted filesystems use `xfs_db -r` to avoid write-side effects.
- Resize accepts size in filesystem blocks for `xfs_growfs -D`.

Important invariants:
- XFS labels are at most 12 characters and cannot contain spaces.
- XFS resize is grow-only and requires a mounted filesystem; generic code handles device-to-mountpoint conversion.
- UUID validation uses common UUID validation, with special tool-level values documented for set-uuid.

Filesystem/block relevance:
- Provides XFS creation, check/repair, metadata query, label/UUID management, and online grow support.

Notable risks:
- Info parsing depends on the exact `data = bsize=... blocks=...` output shape.
- `bd_fs_xfs_check()` comments note that mounted RW filesystems are always reported not clean.
- Capability metadata lists `xfs_db` for check, while implementation uses `xfs_repair -n`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/xfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/xfs.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/xfs.h

Declares XFS info data and operations.

Key contents:
- Defines `BDFSXfsInfo` with `label`, `uuid`, `block_size`, and `block_count`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, label, UUID, info, and resize APIs.

Important invariants:
- XFS resize takes a mountpoint and filesystem-block count, not a device byte size.
- Returned info values are sufficient for size calculation as `block_size * block_count`.

Filesystem/block relevance:
- Exposes XFS management operations to generic dispatch and mount-assisted resize handling.

Notable risks:
- Callers using this header directly must know that `bd_fs_xfs_resize()` expects a mounted path rather than a block device.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/xfs.h -->