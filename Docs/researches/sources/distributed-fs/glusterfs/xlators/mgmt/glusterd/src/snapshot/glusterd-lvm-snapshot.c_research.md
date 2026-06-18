# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/snapshot/glusterd-lvm-snapshot.c

## Purpose

`glusterd-lvm-snapshot.c` implements the LVM snapshot backend for glusterd. It detects thin-provisioned LVM bricks, creates and clones logical-volume snapshots, reports backend details, removes snapshots, mounts and unmounts snapshot bricks, restores by activating the snapshot, derives snapshot brick paths, and exports these operations through `lvm_snap_ops`.

## Important APIs and Functions

- `glusterd_lvm_probe(char *brick_path)` detects whether the brick is on a thin-provisioned LV by resolving the brick mount device and running `/sbin/lvs --noheadings -o pool_lv <device>`.
- `glusterd_lvm_snapshot_device(char *brick_path, char *snapname)` derives `/dev/<vg>/<snapname>` by querying the brick device's `vg_name`.
- `glusterd_lvm_snapshot_create_clone(...)` is the shared implementation for snapshot create and clone. It resolves the origin device, checks whether `lvcreate --help` supports `--setactivationskip`, creates the snapshot with `lvcreate -s`, and then updates the filesystem label.
- `glusterd_lvm_snapshot_create(...)` and `glusterd_lvm_snapshot_clone(...)` are thin wrappers around the shared create/clone helper.
- `glusterd_lvm_brick_details(...)` runs `lvs <snap_device> --noheading -o vg_name,data_percent,lv_size --separator :` and writes `<prefix>.vgname`, `<prefix>.data`, and `<prefix>.lvsize` into a response dictionary.
- `glusterd_lvm_snapshot_remove(...)` removes an LV snapshot with `lvremove -f`, treating an absent device path as a successful no-op for removal.
- `glusterd_lvm_snapshot_activate(...)` creates the snapshot brick mount path, checks whether it is already mounted, and mounts the snapshot device. For XFS it appends `nouuid` if the existing mount options do not already include it.
- `glusterd_lvm_snapshot_deactivate(...)` force-unmounts the snapshot brick path with `_PATH_UMOUNT -f`.
- `glusterd_lvm_snapshot_restore(...)` currently restores by activating/mounting the snapshot and does not update `retain_origin_path`.
- `glusterd_lvm_snap_clone_brick_path(...)` formats a cloned/restored brick path under `snap_mount_dir/<snap_clone_volume_id>/brickN`.
- `lvm_snap_ops` binds these functions to the generic `struct glusterd_snap_ops` interface.

## Control Flow

The generic glusterd snapshot layer chooses this backend when LVM probing succeeds or when a volume's stored `snap_plugin` is `LVM`. Create and clone paths build a per-brick LV name as `<snap_volume_id>_<brick_num>` or `<clone_volume_id>_<brick_num>`. For non-clone snapshot creation the origin is the mounted origin brick device; for clone operations it may be derived from an already stored `device_path`, or rebuilt from the snap brick's `origin_path`.

Command execution goes through Gluster's `runner_t` helper. Query commands redirect stdout into a pipe and parse the first line; mutating commands run synchronously and return their exit status. Activation computes the mount directory from `snap_brickinfo->path`, creates it, inspects mount entries to avoid duplicate mounts, derives or reuses the snapshot device path, adjusts mount options, and invokes `mount`.

## State and Persistence Behavior

This file does not write glusterd store files directly, but it consumes and mutates state that is persisted elsewhere in glusterd. Important persisted inputs include `glusterd_brickinfo_t` fields such as `origin_path`, `device_path`, `fstype`, `mnt_opts`, `path`, `hostname`, and per-volume snapshot IDs. Snapshot device names are deterministic from stored volume IDs and brick numbers unless `device_path` is already present, preserving compatibility with older snapshot records.

Runtime state changes happen in the host LVM and mount namespaces: `lvcreate` creates snapshot logical volumes, `lvremove` destroys them, `mount` exposes them at the snapshot brick path, `umount` tears down the mount, and `glusterd_update_fs_label()` attempts to avoid duplicate filesystem labels after snapshot creation.

## Dependencies and Integration Points

The backend depends on glusterd utilities for mount-device lookup, mount-path lookup, command availability, mount-option inspection, mount-entry lookup, recursive directory creation, and filesystem-label updates. It depends on LVM command constants from `lvm-defaults.h`, `/sbin/lvs`, `lvcreate`, `lvremove`, POSIX mount table support, `dict_t`, `runner_t`, and Gluster logging/message IDs. It integrates with the common snapshot layer through `struct glusterd_snap_ops`, selected by `glusterd_snapshot_plugin_by_name()` and snapshot probing utilities.

## Risks and Edge Cases

- Host command behavior is part of correctness. Missing LVM tools, changed `lvs` output, localized output, or permission failures can cause false negatives or partial snapshot state.
- `glusterd_lvm_snapshot_create_clone()` logs that filesystem-label update failure should not fail snapshot creation, but it returns the label update result. That contradicts the comment and can convert a successful `lvcreate` into a reported failure.
- `glusterd_lvm_snapshot_deactivate()` returns immediately when the path is not mounted and leaks `snap_brick_mount_path`.
- Several output parsers only read the first line and trim/parse with minimal validation. Unexpected whitespace or empty values can become malformed device names or dictionary values.
- Mount option manipulation uses fixed-size buffers and `strcat`; very long existing mount options can overflow `mnt_opts`.
- `glusterd_lvm_brick_details()` uses `dict_set_dynstr()` ownership semantics but does not null local `value` pointers after successful insertion, making later error cleanup sensitive to double-free or leak behavior.
- Removal treats a missing device as success, which is useful for idempotent cleanup but can mask an incorrectly derived snapshot device path.
- Create/clone compatibility branches around `device_path` and `origin_path` are fragile because older snapshots may not have all fields populated.

## Test Signals

High-value tests should stub `runner_t` calls for `lvs`, `lvcreate --help`, `lvcreate`, `lvremove`, `mount`, and `umount`; cover thin and non-thin probe output; validate snapshot device naming from VG and snapshot IDs; verify `--setactivationskip n` inclusion only when supported; check XFS `nouuid` mount option addition; exercise missing-device removal; test path and mount-option length boundaries; and assert that label-update failure semantics match the intended behavior. Integration tests need real or containerized LVM thin volumes to validate end-to-end snapshot create, mount, clone, remove, and restore behavior.
