<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-state-overlay.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-state-overlay.c

## Purpose
Implements hidden `ostree admin state-overlay`, called by `ostree-state-overlay@.service` to mount persistent overlayfs state over a deployment path and prune stale upperdir data when the lower deployment changes.

## Important APIs and Types
Defines overlay directory names under `/var/ostree/state-overlays`, xattr `user.ostree.deploymentcsum`, and overlayfs opaque xattr `trusted.overlay.opaque`. Helpers include `ensure_overlay_dirs`, `lgetxattrat_allow_nodata`, `is_opaque_dir`, `prune_upperdir_recurse`, `prune_upperdir`, `mount_overlay`, `get_overlay_deployment_checksum`, and `set_overlay_deployment_checksum`.

## Control Flow
The command parses unlocked superuser context, requires `NAME MOUNTPATH`, verifies a booted deployment, creates/open overlay `upper` and `work` dirs, reads the stored deployment checksum, and if it differs from the booted deployment checksum, prunes upper entries that now shadow lower entries and stores the new checksum. It then mounts overlayfs with the mount path as lowerdir and the named upper/work dirs.

## State and Persistence
Creates and mutates `/var/ostree/state-overlays/<name>`, including upper/work directories and a deployment checksum xattr on the upper dir. It removes obsolete upperdir files/directories during pruning and creates a live overlayfs mount.

## Dependencies and Integration Points
Uses Linux overlayfs, xattrs, mount syscall, libglnx fd/xattr/shutil helpers, sysroot booted deployment state, and systemd state-overlay units.

## Risks
Pruning is destructive and must correctly distinguish real state files from entries shadowing lowerdir content. Opaque directories and whiteouts require correct xattr/d_type handling. The xattr helper intentionally handles ENODATA races, but relies on `/proc/self/fd`. Mount options are stringified paths and require correct permissions and kernel overlayfs behavior.

## Test Signals
Integration tests need overlay creation, checksum change pruning, opaque directory behavior, whiteout pruning, ENODATA/ERANGE xattr races, mount failure errors, and preservation of upper-only state files.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-state-overlay.c -->
