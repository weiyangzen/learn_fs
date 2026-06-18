# File Research: sources/cow-pools/nilfs-utils/sbin/Makefile.am

## Scope

Builds top-level NILFS system binaries and descends into the mount helper directory.

## Build Behavior

- `SUBDIRS = mount` includes mount/umount helper builds.
- Core system binaries are `mkfs.nilfs2` and `nilfs_cleanerd`; additional sbin programs are `nilfs-clean`, `nilfs-resize`, and `nilfs-tune`.
- `mkfs.nilfs2` builds from `mkfs.c`, `bitops.c`, and headers, and links blkid, uuid, crc32, mount-check, and feature libraries.
- `nilfs_cleanerd` builds from `cleanerd.c` and `cldconfig.c`, links POSIX message queues when needed, uuid, and static NILFS GC support.
- Other tools link against `libnilfs` plus cleaner/parser/mount-check/feature/GC libraries as appropriate.
- `fix-conflicting-dirs` removes directories whose names conflict with binary outputs.
- Optional `CREATE_COMPAT_SBIN_LINK` hooks create/remove compatibility symlinks in `$(exec_prefix)/sbin`.

## Dependencies And Risks

The Makefile encodes library ownership and install compatibility behavior. The `rm -rf "$$p"` helper is intentionally scoped to program-name conflicts in the build directory but is destructive if an unexpected directory shares a target binary name.
