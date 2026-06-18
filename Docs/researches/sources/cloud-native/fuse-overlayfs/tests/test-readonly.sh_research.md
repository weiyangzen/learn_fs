# sources/cloud-native/fuse-overlayfs/tests/test-readonly.sh

## Purpose
`tests/test-readonly.sh` validates lower-only readonly overlays and selected mount options for id mapping, squash modes, symlinks, special files, and volatile/fsync behavior.

## Important APIs, Types, And Functions
The script uses `fuse-overlayfs`, shell write operations expected to fail, `stat`, `chown`, symlink commands, `mkfifo`, optional `mknod`, and `sync`.

## Control Flow
Eight scenarios mount lower-only or writable overlays: readonly writes must fail while reads work; multiple lower layers merge; `squash_to_root` and `squash_to_uid/gid` alter visible ownership; `uidmapping`/`gidmapping` maps host ids; symlinks and special files are visible in readonly mode; volatile mode allows writes and tolerates sync behavior.

## State And Persistence
Temporary lower/upper/workdir/merged directories are created per scenario. Readonly scenarios should not persist upper changes because no upperdir exists; writable option tests create normal upper/workdir state.

## Dependencies And Integration Points
Exercises `upper_layer`/EROFS paths, metadata mapping in `rpl_stat_with_path`, symlink readlink, special-file type mapping, and fsync-disabled volatile behavior. Requires FUSE and optionally mknod privilege.

## Risks
Write-failure checks grep human-readable "read-only" messages, which can vary by locale/tool. Mapping tests require permission to chown prepared lower files. Volatile test accepts sync failure, so it only validates data remains readable before unmount.

## Test Signals
Pass indicates lower-only mounts reject mutation with readonly errors, multiple lowerdir merge works without upperdir, id/squash mapping affects visible stats, and symlink/special-file metadata remains intact.
