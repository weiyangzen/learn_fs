# File Research: sources/cow-pools/nilfs-utils/sbin/mount/umount_libmount.c

## Scope

Libmount-based implementation of `umount.nilfs2`, coordinating libmount unmount/finalization with NILFS cleaner daemon attributes.

## APIs And Behavior

- Initializes a libmount context, parses `-f`, `-l`, `-n`, `-v`, `-r`, and `-V`, sets fstype to `nilfs2`, and disables helper recursion.
- Force is accepted but warned as ignored; lazy and read-only remount behavior are delegated to libmount context flags.
- Rejects non-root unmounts in the current implementation.
- `nilfs_prepare_umount()` calls `mnt_context_prepare_umount()`, then parses stored NILFS attributes from the selected mount entry.
- `nilfs_do_umount_one()` pings and shuts down cleanerd if a stored `gcpid` exists, runs `mnt_context_do_umount()`, and if read-only remount fallback leaves the filesystem mounted, restarts cleanerd and updates attributes.
- `nilfs_umount_one()` finalizes successful fake or real unmounts and reports normalized errno diagnostics.
- Main loops over all mountpoint arguments and returns success, failure, or some-ok exit status.

## State And Dependencies

`struct nilfs_umount_info` stores libmount context and old NILFS attributes. Dependencies include libmount, cleaner-exec APIs, and `mount_attrs.c`.

## Risks And Invariants

Stored attributes are required to find the cleaner PID; incomplete utab/mtab attributes can make cleanerd uncontrollable. As with the legacy implementation, the daemon is stopped before unmount and must be restarted if the unmount degrades to a still-mounted read-only state.
