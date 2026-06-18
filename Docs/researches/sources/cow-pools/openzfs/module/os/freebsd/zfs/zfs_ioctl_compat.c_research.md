# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/zfs_ioctl_compat.c

## Purpose

Implements FreeBSD legacy ZFS ioctl compatibility when `ZFS_LEGACY_SUPPORT` is enabled. It translates older FreeBSD ZFS ioctl command numbers and legacy `zfs_cmd_legacy_t` layouts to/from current OpenZFS ioctl numbers and `zfs_cmd_t`.

## Conditional Compilation

- Entire implementation is guarded by `#ifdef ZFS_LEGACY_SUPPORT`.
- If legacy support is not enabled, this file contributes no runtime code.

## Legacy Ioctl Numbering

- `enum zfs_ioc_legacy`
  - Defines legacy command ids beginning at zero.
  - Covers pool, vdev, objset, dataset, send/receive, delegation, jail, nextboot, checkpoint, initialize, and sync-related commands.
  - `ZFS_IOC_LEGACY_NONE` is `-1` and marks unsupported/no direct mapping.

## Mapping Tables

- `zfs_ioctl_legacy_to_ozfs_[]`
  - Maps legacy ordinal request numbers to current OpenZFS `ZFS_IOC_*` values.
  - Comments document mismatches where historical FreeBSD numbering diverged from OpenZFS.
- `zfs_ioctl_ozfs_to_legacy_common_[]`
  - Maps common current OpenZFS commands back to legacy command ids.
  - Unsupported newer commands map to `ZFS_IOC_LEGACY_NONE`.
- `zfs_ioctl_ozfs_to_legacy_platform_[]`
  - Maps platform-specific commands after `ZFS_IOC_PLATFORM`.
  - Supports legacy `NEXTBOOT`, `JAIL`, and `UNJAIL`; event and bootenv commands are unsupported.

## Translation Functions

- `zfs_ioctl_legacy_to_ozfs(int request)`
  - Bounds-checks against the legacy-to-current table.
  - Returns `-1` if out of range.
  - Otherwise returns current `ZFS_IOC_*`.
- `zfs_ioctl_ozfs_to_legacy(int request)`
  - Rejects `request >= ZFS_IOC_LAST`.
  - For platform commands, subtracts `ZFS_IOC_PLATFORM + 1` and indexes the platform table.
  - For common commands, bounds-checks against the common table.
  - Returns `-1` for unmapped/out-of-range commands.

## Command Structure Conversion

- `zfs_cmd_legacy_to_ozfs(zfs_cmd_legacy_t *src, zfs_cmd_t *dst)`
  - Copies prefix fields up to `zc_objset_stats`.
  - Copies object-set stats explicitly.
  - Copies the record/field span from legacy begin record through current send object area.
  - Copies trailing fields after `zc_sendobj`, adjusted by an 8-byte layout difference.
  - Maps `zc_jailid` to `zc_zoneid`.
- `zfs_cmd_ozfs_to_legacy(zfs_cmd_t *src, zfs_cmd_legacy_t *dst)`
  - Performs the reverse structural copy.
  - Embeds current begin record into legacy `drr_u.drr_begin`.
  - Clears legacy `drr_payloadlen` and `drr_type`.
  - Copies inject/send fields.
  - Forces `zc_resumable = B_FALSE`.
  - Maps `zc_zoneid` back to `zc_jailid`.

## Important Notes

- The conversions are layout-sensitive and depend on `offsetof()` spans rather than field-by-field semantic conversion.
- The file handles ABI compatibility only; actual ioctl execution is elsewhere.
- Unsupported ioctls are represented by `-1` or `ZFS_IOC_LEGACY_NONE`.
