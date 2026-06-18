# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.c

## Scope

Legacy implementation of `mount.nilfs2`, using direct `mount(2)`, custom option parsing, and mtab updates while coordinating NILFS cleaner daemon lifecycle.

## APIs And Behavior

- Parses `-f`, `-v`, `-n`, `-t`, `-o`, `-r`, `-w`, and `-V`; converts options into mount flags and extra kernel options.
- Rejects unknown filesystem types and non-root helper execution.
- Checks `/etc/mtab` availability unless `-n`, verifies writable mounts do not target read-only devices, and installs SIGTERM/SIGINT handlers.
- `prepare_mount()` rejects mounting over an already mounted target, finds an existing read-write NILFS mount for the device, enforces single read-write mount semantics, and handles rw-to-ro/rw-to-rw remounts by stopping the recorded cleaner daemon.
- `do_mount_one()` removes user-facing `pp` and `nogc` from kernel option string, invokes `mount(2)`, and restarts cleanerd if a remount failed after stopping it.
- `update_mount_state()` starts cleanerd for read-write non-bind mounts unless `nogc` is set, records `gcpid` and `pp` in mtab options, and updates or appends the mtab entry.
- Optional SELinux warning reports when mounting an unlabeled filesystem on SELinux systems.

## State And Dependencies

Global mount flags (`verbose`, `readonly`, `readwrite`, `nomtab`, `fake`) are shared with legacy option helpers. Dependencies include `fstab.c`, `mount_opts.c`, `sundries.c`, `mount_mntent.c`, direct `mount(2)`, `BLKROGET`, and cleaner execution APIs.

## Risks And Invariants

Correct GC control depends on preserving/removing `gcpid`, `pp`, and `nogc` consistently in mtab. On remount, the code stops cleanerd before the syscall and attempts restart on failure. Multiple read-write mounts of the same NILFS device are explicitly forbidden, but read-only overlapping mounts are allowed.
