# File Research: sources/cow-pools/nilfs-utils/sbin/mount/umount.nilfs2.c

## Scope

Legacy implementation of `umount.nilfs2`, using direct `umount(2)`, custom mtab parsing/updating, optional read-only remount fallback, loop cleanup, and cleaner daemon shutdown/restart logic.

## APIs And Behavior

- Parses `-n`, `-l`, `-f`, `-v`, `-r`, and `-V`; force is ignored, lazy is reported unsupported.
- Rejects non-root unmounts in the current implementation.
- Resolves each mountpoint through mtab, verifies the mounted type is NILFS2, and delegates to `umount_one()`.
- Before unmounting a read-write NILFS mount, reads `pid=<gcpid>` from mtab, pings cleanerd, and asks it to shut down.
- On `EBUSY` with `-r`, attempts remount read-only and updates mtab options to `ro`.
- On `EBUSY` without `-r`, if cleanerd was alive and stopped, attempts to restart it and update `pid=` in mtab.
- On successful unmount, optionally clears loop devices recorded in old-style loop type or `loop=` option and removes the mtab entry.
- `complain()` maps common unmount errno values to user-facing diagnostics.

## State And Dependencies

Uses legacy fstab/mtab, mount option, mntent, sundries, and cleaner-exec helpers. `options` stores force/lazy/remount/suid flags.

## Risks And Invariants

Cleaner shutdown occurs before the unmount syscall for writable mounts, so failure paths must restart it when the filesystem remains mounted. Loop option parsing duplicates the option string but advances the pointer with `strtok`, leaking the original allocation in that branch. mtab updates are skipped for root and when `-n` is active.
