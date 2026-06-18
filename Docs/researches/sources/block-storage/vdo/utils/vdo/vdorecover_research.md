# File Research: sources/block-storage/vdo/utils/vdo/vdorecover

## Purpose

`vdorecover` is a Bash recovery helper for running space reclamation against a VDO device that is full or otherwise needs controlled cleanup. It builds device-mapper snapshots under and above the VDO target, runs `fstrim` or prompts for manual deletion, then merges snapshot changes back.

## Command-Line Interface

Usage:

```text
./vdo_recover {path to vdo device}
```

It accepts `--help` or `-h`.

The script requires root (`EUID == 0`) and a running device-mapper target of type `vdo`.

## Main Flow

Top-level flow:

1. Read `VDO_DEVICE=$1`.
2. Validate argument and root privileges.
3. Iterate `dmsetup ls --target vdo`.
4. Match basename of supplied device path to VDO volume name.
5. Refuse to run if the VDO device appears mounted directly.
6. Install `_cleanup` trap.
7. Save original VDO dm table.
8. Run `_recoveryProcess`.
9. Clear trap and exit.

`_recoveryProcess()`:

1. Initializes `LOOPBACK_DIR`, defaulting to a temp dir.
2. Calls `_insertSnapUnderVDO`.
3. Calls `_addSnapAboveVDO`.
4. Calls `_repointUpperDevicesOrMountVDO`.
5. Merges data snapshot.
6. Merges backing snapshot.
7. Prints completion with final used percentage.

## Snapshot Operations

`_insertSnapUnderVDO()`:

- Extracts VDO backing device from VDO table.
- Replaces active VDO target temporarily with an error target.
- Creates a snapshot under the VDO backing.
- Reloads VDO to point at the under-VDO snapshot.

`_addSnapAboveVDO()`:

- Creates a snapshot over the VDO device itself.

`_snap()`:

- Creates `<device>-origin` as `snapshot-origin`.
- Creates a loopback COW file through `_mkloop()`.
- Creates `<device>-snap` as a `snapshot` target.

`_mergeSnapshot()`:

- Converts a snapshot table to `snapshot-merge`.
- Waits for merge to complete.
- Removes merge and snap devices.

## Reclaim and Manual Cleanup

`_fstrim()`:

- Checks snapshot status capacity.
- Runs `_fstrimAndPrompt()` when there is room in the snapshot.

`_fstrimAndPrompt()`:

- Runs `fstrim` if a mount point is provided.
- Reads VDO usage from `vdostats $VDO_VOLUME_NAME`.
- If usage remains `100`, prompts the user to delete files and continue.

`_repointUpperDevicesOrMountVDO()`:

- Detects devices depending on the VDO.
- If a dependent device exists:
  - Saves its original table.
  - Reloads it to point at the VDO snapshot.
  - Prompts/attempts trim through the dependent mount.
  - Restores the original table.
- Otherwise:
  - Mounts the VDO snapshot in a temp directory.
  - Runs fstrim.
  - Unmounts it.

## Cleanup

`_cleanup()` attempts to:

- Unmount temporary mount point.
- Restore dependent device table.
- Remove dm snapshot/merge/origin devices.
- Detach loop devices.
- Remove temporary loopback files.
- Disable then restore original VDO table if needed.

## Dependencies

External commands used include:

- `dmsetup`
- `blockdev`
- `losetup`
- `truncate`
- `df`
- `mktemp`
- `mount`
- `umount`
- `rmdir`
- `fstrim`
- `vdostats`
- `awk`, `grep`, `sed`, `cut`, `basename`, `rm`, `sleep`

## Notable Behaviors and Risks

- The script uses `set -e`, but many cleanup commands are guarded with `|| true`.
- There is a likely test bug in `_mkloop()`:
  ```bash
  if [[ TMPFS -lt LO_DEV_SIZE ]]; then
  ```
  This compares literal strings/empty variables rather than `$TMPFS` and `$LO_DEV_SIZE`.
- Temporary file size uses `truncate -s ${LO_DEV_SIZE}M`, while `LO_DEV_SIZE` is derived from sectors unless `TMPFILESZ` is supplied; units may be confusing.
- Parsing `dmsetup` output with whitespace-sensitive shell pipelines can be brittle for unusual names.
- The script is destructive if pointed at the wrong VDO target; it manipulates live dm tables and snapshots.
