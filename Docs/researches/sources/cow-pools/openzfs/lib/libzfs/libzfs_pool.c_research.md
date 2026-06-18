# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_pool.c

## Read Coverage
Read completely: 6,012 lines, 158,834 bytes.

## Purpose
`libzfs_pool.c` is the main userspace `libzfs` implementation for ZFS pool management. It provides the public and internal helpers used by `zpool` and other libzfs consumers to inspect pool state, validate and set pool/vdev properties, create/import/export/destroy pools, mutate vdev topology, run maintenance operations, read pool history/events/errors, and translate low-level kernel/libzfs_core failures into user-facing libzfs errors.

The file is a bridge between CLI-facing semantics and kernel interfaces: it builds `zfs_cmd_t` and nvlist payloads, calls `zfs_ioctl()` or `lzc_*()` APIs, then formats status, names, and diagnostics for callers.

## Major Responsibilities
- Pool property retrieval and formatting through `zpool_get_all_props()`, `zpool_get_prop_int()`, `zpool_get_prop()`, `zpool_get_userprop()`, and `zpool_expand_proplist()`.
- Pool and vdev property validation through `zpool_valid_proplist()`, including creation/import-only restrictions, readonly/set-once handling, feature properties, user properties, `bootfs`, `altroot`, `cachefile`, `compatibility`, `comment`, `readonly`, `multihost`, and vdev property mode.
- Pool lifecycle operations: `zpool_create()`, `zpool_destroy()`, `zpool_import()`, `zpool_import_props()`, `zpool_export()`, `zpool_export_force()`, `zpool_checkpoint()`, `zpool_discard_checkpoint()`, `zpool_upgrade()`, `zpool_reguid()`, `zpool_reopen_one()`, and `zpool_sync_one()`.
- Maintenance operations: initialize/uninitialize, TRIM, scrub/error scrub/resilver scan, DDT/BRT prefetch, DDT prune, wait, clear, and rewind/recovery explanation.
- Vdev lookup and mutation: find vdevs by GUID/path/type/physical path, online/offline/fault/degrade/remove/attach/detach/split, derive display names, collect leaves, and manage vdev properties.
- Event/history/error-log interfaces: pool command history, zevent iteration/clear/seek, persistent error-log retrieval, and object-to-path translation.

## Key Data and Interfaces
- Uses `zpool_handle_t` as the primary pool object, holding `zpool_hdl`, pool name, state, cached config, previous config, cached props, and requested property names.
- Uses `zfs_cmd_t` for ioctl calls such as `ZFS_IOC_POOL_GET_PROPS`, `ZFS_IOC_POOL_CREATE`, `ZFS_IOC_POOL_IMPORT`, `ZFS_IOC_VDEV_SET_STATE`, `ZFS_IOC_VDEV_ATTACH`, `ZFS_IOC_VDEV_REMOVE`, `ZFS_IOC_CLEAR`, `ZFS_IOC_ERROR_LOG`, and event/history ioctls.
- Uses libzfs_core entry points for newer or structured operations: `lzc_pool_checkpoint()`, `lzc_pool_checkpoint_discard()`, `lzc_pool_prefetch()`, `lzc_initialize()`, `lzc_trim()`, `lzc_scrub()`, `lzc_wait()`, `lzc_wait_tag()`, `lzc_sync()`, `lzc_reopen()`, `lzc_set_bootenv()`, `lzc_get_bootenv()`, `lzc_get_vdev_prop()`, `lzc_set_vdev_prop()`, and `lzc_ddt_prune()`.
- Heavy use of nvlist contracts with keys from `ZPOOL_CONFIG_*`, `ZPROP_*`, `ZPOOL_VDEV_PROPS_*`, and feature metadata from `spa_feature_table`.

## Control Flow Highlights
- Property fetches lazily populate `zhp->zpool_props`; `zpool_get_prop()` special-cases unavailable pools so name, health, GUID, and select string properties can still be displayed.
- Property validation normalizes string inputs into kernel-ready numeric/string nvlist entries and rejects properties whose scope does not match the operation mode.
- Pool creation validates pool and root filesystem properties, optionally creates encryption wrapping-key hidden arguments, writes config/source nvlists into `zfs_cmd_t`, and maps kernel errno values to specific libzfs diagnostics.
- Import builds optional property nvlist, supports renaming, handles rewind/dry-run policies, prints unsupported-feature and MMP diagnostics, and checks that the imported pool can be opened afterward.
- Vdev lookup recursively searches the vdev tree plus spare and L2ARC arrays; it supports GUIDs, paths with whole-disk partition handling, physical paths, and generated top-level names like `mirror-0`, `raidz2-1`, and dRAID names.
- Initialize and TRIM convert requested vdev paths to GUID nvlists, call lzc APIs, translate per-vdev errlists back to path-oriented errors, and optionally wait for completion.
- Scan logic first tries `lzc_scrub()` with structured arguments, falls back to older `ZFS_IOC_POOL_SCAN` when unavailable, and has detailed `EBUSY` handling for normal scrub, error scrub, paused states, and resilver.
- Vdev attach handles replacement, rebuild, dRAID, raidz expansion, spare replacement constraints, ashift mismatch, and kernel feature availability before/after ioctl.
- Pool split builds a new root vdev tree from one child of each mirror, preserves special/dedup allocation bias for dry runs, inserts holes for log/hole positions, validates user-selected devices, and calls `ZFS_IOC_VDEV_SPLIT`.
- Compatibility loading parses feature-set files from system and data compatibility directories, ANDs selected feature sets together, distinguishes hard errors for local invalid tokens from warnings for distribution invalid tokens, and supports `off`/empty/all and `legacy` special cases.

## Important Functions
- `zpool_valid_proplist()` is the central validation funnel for pool creation, import, property setting, and vdev property setting.
- `zpool_import_props()` contains most import error diagnostics and recovery/rewind messaging.
- `vdev_to_nvlist_iter()` and `__zpool_find_vdev()` define the vdev addressing model used by most vdev operations.
- `zpool_vdev_name()` defines user-visible vdev naming, including environment-variable overrides for path/GUID/follow-links naming.
- `zpool_get_vdev_prop_value()` mirrors pool property formatting for vdev properties and contains property-specific formatting rules.
- `zpool_load_compat()` implements compatibility-file parsing for pool feature gating.

## Error Handling and Diagnostics
The file consistently builds operation-specific `errbuf` messages and reports via `zfs_error()`, `zfs_error_fmt()`, `zpool_standard_error()`, and `zpool_standard_error_fmt()`. Many errno paths are deliberately translated into more precise libzfs errors, for example:
- `EBUSY`, `EOVERFLOW`, `ENXIO`, `ERANGE`, `EDOM`, and `EINVAL` during pool create/add.
- unsupported features and readonly import options during import.
- no replicas, unplayed logs, spare/L2ARC misuse, rebuild unsupported, raidz expansion unsupported, and ashift mismatch during vdev mutation.
- per-vdev initialize/TRIM errors from returned errlists.

## Integration Points
- Depends on OpenZFS kernel ioctl ABI and libzfs_core ABI.
- Depends on nvpair/nvlist allocation helpers, `fnvlist_*`, `zcmd_*` helpers, and libzfs error state.
- Integrates with dataset/property validation via `zfs_valid_proplist()` and crypto setup via `zfs_crypto_create()`.
- Uses platform-specific device/path helpers such as `zfs_resolve_shortname()`, `zpool_relabel_disk()`, `zfs_strip_path()`, `zfs_strip_partition()`, and mount detection.
- Uses feature metadata and compatibility constants from OpenZFS feature tables.

## Invariants and Assumptions
- Callers usually pass already-validated vdev configuration trees for create/add/attach paths, but this file still validates operation-specific constraints.
- Returned nvlist ownership is explicit and most public APIs either free temporary nvlists before returning or transfer ownership through output parameters.
- Pool names are validated differently for open versus create/import so existing pools with now-reserved names can still be opened.
- Vdev properties require resolving a user-visible vdev name to a GUID before calling lzc property APIs.
- Many operations assume `zhp->zpool_config` contains `ZPOOL_CONFIG_VDEV_TREE` and required vdev stats/config keys.

## Risks and Edge Cases
- This file has a large amount of errno-specific behavior; kernel ABI changes can silently degrade diagnostics or change user-visible command behavior.
- Several operations allocate multiple nested nvlists and early-return on memory errors; leak safety depends on each path preserving the existing cleanup pattern.
- Vdev name parsing is subtle, especially for whole disks, short names, raidz parity names, dRAID names, and generated type-id names.
- Compatibility-file parsing uses `mmap()` and in-place tokenization; malformed file size/newline/token cases are intentionally rejected or warned depending on source directory.
- Some paths use environment variables to alter display names, so tests for vdev output must account for `ZPOOL_VDEV_NAME_PATH`, `ZPOOL_VDEV_NAME_GUID`, and `ZPOOL_VDEV_NAME_FOLLOW_LINKS`.
- `zpool_set_guid()` only frees command nvlists on the explicit-guid path; this matches current setup but is easy to regress if source nvlists are added for the null-guid case.

## Testing Signals
Good coverage for this file should include:
- Pool property formatting for literal and human-readable forms, unavailable pools, feature props, user props, and dedup/cache size special cases.
- Property validation failures for readonly/set-once/import/create-only properties, invalid `bootfs`, invalid `cachefile`, bad comments, invalid compatibility files, and unsupported features.
- Import diagnostics for unsupported features, MMP active/no-hostid, missing devices, dry-run rewind, and rename errors.
- Vdev lookup by GUID, path, short path, physical path, top-level generated names, raidz/dRAID variants, spares, L2ARC, logs, and parent lookup.
- Vdev attach/detach/remove/online/offline/fault behavior across disks, mirrors, raidz, dRAID spares, replacing/spare configs, L2ARC, and logs.
- Initialize/TRIM per-vdev errlist translation and wait behavior.
- Scrub/error scrub/resilver state conflict handling.
- History, event, error-log, bootenv, compatibility, wait, sync, checkpoint, and DDT prune wrappers.

## Overall Assessment
This is a core libzfs orchestration file rather than an algorithmic storage implementation. Its main complexity is contract management: validating user input, preserving nvlist/ioctl ABI shape, mapping user-visible vdev names to stable GUIDs, and translating kernel/libzfs_core results into precise `zpool` behavior. Changes here have broad CLI and API blast radius and should be tested against both success paths and detailed diagnostic/error paths.
