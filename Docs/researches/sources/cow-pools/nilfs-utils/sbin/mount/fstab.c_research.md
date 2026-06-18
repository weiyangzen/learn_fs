# File Research: sources/cow-pools/nilfs-utils/sbin/mount/fstab.c

## Scope

Legacy util-linux-derived fstab/mtab support for NILFS mount helpers: reading mount tables, finding entries, locking mtab, and updating mtab records.

## APIs And Behavior

- `mtab_does_not_exist()`, `mtab_is_writable()`, and internal symlink detection decide whether `/etc/mtab` can be updated.
- `mtab_head()` and `fstab_head()` lazily read `/etc/mtab` or `/proc/mounts`, and `/etc/fstab`, into circular doubly linked lists.
- Lookup helpers search by mountpoint/device, backward by directory/device, loop option, fstab spec/file, UUID, and label declarations.
- `lock_mtab()` creates a per-process link target, links it to the mtab lock path, then uses `fcntl` locking with a monotonic-clock timeout.
- Signal handlers are installed while locking so lock files are removed on fatal signals.
- `update_mtab()` rereads mtab under lock, removes an entry for umount, replaces options for remount, or appends a new entry, writes a temporary mtab, fixes mode/ownership, and renames it over the real mtab.

## State And Dependencies

The file uses global cached mount/fstab lists and lock state. It depends on custom `mount_mntent.c` parsing/writing, path constants, `xmalloc`, and `sundries` fatal/error helpers.

## Risks And Invariants

The lock-file protocol must always call `unlock_mtab()` through `atexit` or signal cleanup. The table cache is stale after update unless reread under lock as `update_mtab()` does. Symlinked mtab is deliberately treated as non-writable to avoid writing to `/proc/mounts`.
