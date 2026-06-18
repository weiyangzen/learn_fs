# File Research: sources/cow-pools/nilfs-utils/sbin/mount/fstab.h

## Scope

Declares legacy fstab/mtab data structures and helper functions.

## API Surface

- `struct mntentchn` links parsed `struct my_mntent` entries in circular lists.
- Exposes mtab writability/existence checks, lookup functions for mount and fstab entries, lock/unlock functions, and `update_mtab()`.

## Dependencies And Risks

The header depends on `mount_mntent.h`. Callers receive pointers into cached linked lists and must not free them directly except through implementation-managed paths.
