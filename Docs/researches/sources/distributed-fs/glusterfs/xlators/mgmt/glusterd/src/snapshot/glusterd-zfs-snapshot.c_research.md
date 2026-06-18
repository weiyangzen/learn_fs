# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/snapshot/glusterd-zfs-snapshot.c

## Purpose

`glusterd-zfs-snapshot.c` implements the ZFS snapshot backend for glusterd. It detects ZFS-backed bricks, creates ZFS snapshots, creates clone datasets from snapshots, reports minimal backend detail fields, destroys snapshots, treats activation/deactivation as no-ops because ZFS exposes snapshots through `.zfs`, restores by cloning and setting a mountpoint, computes brick paths, and exports the backend as `zfs_snap_ops`.

## Important APIs and Functions

- `glusterd_zfs_dataset(char *brick_path, char **pool_name)` runs `zfs list -Ho name <brick_path>` and returns the dataset name through `pool_name`.
- `glusterd_zfs_probe(char *brick_path)` verifies the ZFS command is available, finds the brick root, reads the mount table entry, and returns true when the mount type begins with `zfs`.
- `glusterd_zfs_snapshot_create_or_clone(...)` builds `<dataset>@<snap_volume_id>_<brick_num>` for snapshots and `<dataset>/<clone_volume_id>_<brick_num>` for clones, then runs `zfs snapshot` or `zfs clone`.
- `glusterd_zfs_snapshot_create(...)` and `glusterd_zfs_snapshot_clone(...)` wrap the shared create/clone helper.
- `glusterd_zfs_brick_details(...)` stores the dataset as `<prefix>.vgname` and uses `"-"` placeholders for `<prefix>.data` and `<prefix>.lvsize` to match the generic snapshot status schema used by LVM.
- `glusterd_zfs_snapshot_remove(...)` destroys `<dataset>@<snap_volume_id>_<brick_num>` with `zfs destroy`.
- `glusterd_zfs_snapshot_activate(...)` and `glusterd_zfs_snapshot_deactivate(...)` return success without host changes.
- `glusterd_zfs_snapshot_restore(...)` clones the snapshot to `<dataset>/<snap_volume_id>_<brick_num>` and sets `mountpoint=<snap_mount_dir>/<snap_volume_id>/brick<brick_num>`.
- `glusterd_zfs_snap_clone_brick_path(...)` derives brick paths for clone, restore, and ordinary snapshot access through either a clone dataset mountpoint or `.zfs/snapshot`.
- `zfs_snap_ops` registers the backend with the common snapshot interface.

## Control Flow

The backend is selected by probe or by stored `snap_plugin` name. Probe first ensures `/sbin/zfs` exists, then validates the brick's mounted filesystem type. Create, clone, remove, details, and restore all begin by resolving a dataset name from the brick origin path. Snapshot names use the generic glusterd volume ID plus brick number convention. Unlike LVM, ZFS ordinary snapshot access does not require a mount call; brick paths can point under the origin dataset's `.zfs/snapshot/<snapshot>/...` tree. Restore is different: it creates a clone dataset and assigns a mountpoint under the global `snap_mount_dir`.

## State and Persistence Behavior

This file does not write glusterd store metadata. It relies on persisted brick metadata (`origin_path`, `path`, IDs, brick number, and snapshot plugin) and mutates the host ZFS dataset namespace. Snapshot persistence is therefore in ZFS datasets and snapshots: `zfs snapshot` creates durable snapshots, `zfs clone` creates durable clone datasets, `zfs destroy` removes snapshots, and `zfs set mountpoint=...` persists the restore clone mountpoint. Path generation must remain stable because glusterd store/restart code later reuses the backend to activate, restore, or remove the same snapshot.

## Dependencies and Integration Points

The backend depends on Gluster utilities for command availability, brick root discovery, mount table lookup, memory allocation, dictionary updates, and command running. It uses `runner_t`, `dict_t`, `mntent`, and Gluster logging. It integrates with `glusterd-snapshot-utils.c`, which exposes `lvm_snap_ops` and `zfs_snap_ops` through `glusterd_snapshot_plugin_by_name()` and probes available backends.

## Risks and Edge Cases

- `glusterd_zfs_dataset()` stores the dataset in a local stack buffer and assigns `*pool_name = strtok(dataset, "\n")`. That returns a pointer into a dead stack frame after the function returns, so callers use invalid memory. The function should duplicate the dataset string or receive an output buffer.
- The probe checks command availability at `/sbin/zfs` but dataset lookup invokes `"zfs"` rather than `ZFS_COMMAND`, so path behavior can differ between probe and execution.
- `strncmp("zfs", entry->mnt_type, 5)` compares five bytes including the trailing NUL in the literal; it works for exact `"zfs"` but is stricter than the surrounding wording suggests.
- Snapshot, clone, and restore naming uses fixed `NAME_MAX` buffers. Long dataset names plus generated IDs can fail or truncate.
- Activation and deactivation are no-ops. That matches `.zfs` snapshot access, but callers must not assume no-op activation proves the snapshot path is visible if ZFS `.zfs` visibility is disabled.
- `glusterd_zfs_snap_clone_brick_path()` checks `len >= sizeof(brick_path)`, but `brick_path` is a local `PATH_MAX` buffer that is not the destination; it should compare against `sizeof(brickinfo->path)`.
- Restore creates a clone dataset but does not roll back or replace the origin dataset directly. Higher layers must understand that restore path semantics are clone-and-mount based.

## Test Signals

Unit tests should mock `zfs list`, `zfs snapshot`, `zfs clone`, `zfs destroy`, and `zfs set`; verify dataset string ownership; test probe behavior with missing command, missing mount entry, and non-ZFS mount type; validate generated snapshot/clone names; exercise long dataset and brick-dir inputs; and check clone, restore, and `.zfs/snapshot` brick path formatting. Integration tests need a real ZFS pool/dataset with `.zfs` visibility settings covered.
