# sources/distributed-fs/orangefs/src/apps/kernel/linux/mount.pvfs2.c

## Purpose
`mount.pvfs2.c` is a legacy Linux mount helper, primarily for 2.4 kernels, that validates arguments, copies the PVFS device description into the mount options string for the kernel module, invokes `mount(2)`, and updates `/etc/mtab` when appropriate.

## Important APIs, Types, and Functions
`main()` orchestrates parsing, mountpoint canonicalization through `PINT_realpath()`, local directory validation with `stat()`, the `mount(dev, mntpnt, "pvfs2", flags, kern_options)` syscall, and mtab update. `parse_args()` handles a single `-o` option string, recognizes `ro` and `remount` to set `MS_RDONLY`/`MS_REMOUNT`, builds `orig_options`, `kern_options`, `mntpnt`, and `dev`, and rejects malformed argument counts. `do_mtab()` copies existing `/etc/mtab` entries into `/etc/mtab.pvfs2`, appends the new entry, renames it over `/etc/mtab`, and chmods the result. `usage()` prints command syntax.

## Control Flow
The helper requires at least a device URI and mount directory. After parsing, the mountpoint is resolved and verified as a directory. If `mount(2)` fails, the program exits without mtab changes. Remounts return after the syscall. If `/etc/mtab` is a symlink, it is left alone. Otherwise `do_mtab()` performs a rewrite/rename update.

## State and Persistence
Persistent effects are the kernel mount table and, when applicable, `/etc/mtab`. Temporary persistent state is `/etc/mtab.pvfs2`. Heap state includes duplicated device/options/mountpoint strings. The helper does not store config elsewhere.

## Dependencies and Integration Points
It depends on libc mount/mtab APIs, Linux mount flags, OrangeFS `PVFS_NAME_MAX`, `PVFS_perror()`, and `PINT_realpath()`. It is included only in certain kernel app builds through `module.mk.in` and exists to satisfy kernel-module expectations around where the device string appears.

## Risks and Edge Cases
`do_mtab()` calls `endmntent()` on possibly NULL streams in error paths. The mtab rewrite is not locked, so concurrent mount helpers can race and lose entries. Fixed `mopts[256]` rejects long option strings but still uses `strcpy()` after the length check. `kern_options` concatenation assumes one device URI and one options string; embedded commas in device-like data are not supported. On mount success followed by mtab update failure, the filesystem remains mounted but mtab may be stale. Memory allocated before some parse failures is not always freed.

## Test Signals
Unit-test `parse_args()` for no options, `ro`, `remount`, duplicate `-o`, long options, and malformed positional counts. Integration tests should use a safe mount namespace or mocked `mount(2)` to verify `kern_options` and flags. Mtab tests should cover symlink `/etc/mtab`, rewrite failure, concurrent updates, and remount no-update behavior.
