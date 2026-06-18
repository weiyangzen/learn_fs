# sources/distributed-fs/ceph-client/init/initramfs.c

## Purpose
`initramfs.c` implements early rootfs population. It extracts built-in and external initramfs/initrd images into rootfs, manages optional initrd retention/freeing, exposes retained initrd data through sysfs, and exports `wait_for_initramfs()` so later boot code can synchronize with asynchronous extraction.

## Important APIs, Types, And Functions
- `unpack_to_rootfs(char *buf, unsigned long len)` is the central parser/decompressor. It accepts raw `newc` cpio streams or compressed streams detected by `decompress_method()`, writes files into rootfs, and returns `NULL` on success or a static error string.
- `reserve_initrd_mem()` validates and reserves physical initrd memory with memblock, converts it to virtual `initrd_start/initrd_end`, and disables invalid or overlapping initrd regions.
- `populate_rootfs()` is registered with `rootfs_initcall()` and schedules `do_populate_rootfs()` on an exclusive async domain unless `initramfs_async=false`.
- `wait_for_initramfs()` synchronizes against the async cookie and is exported with GPL visibility.
- `find_link()/free_hash()` track cpio hardlinks by `(major, minor, ino, file type)`.
- `do_name()`, `do_copy()`, `do_symlink()`, `do_header()`, and `flush_buffer()` are the finite-state-machine actions used while unpacking.

## Control Flow
The cpio extractor operates as a finite-state machine over `Start`, `Collect`, `GotHeader`, `SkipIt`, `GotName`, `CopyFile`, `GotSymlink`, and `Reset`. `write_buffer()` repeatedly invokes the current action until progress stops. `flush_buffer()` feeds decompressed bytes into the same state machine and validates archive boundaries.

`unpack_to_rootfs()` initializes transient buffers, then loops over the input. If the current location looks like an aligned `newc` header it parses directly; if it sees zero padding it skips it; otherwise it attempts decompression and feeds output through `flush_buffer()`. Directory mtimes and hardlink hash cleanup are finalized after the stream.

Rootfs population first unpacks the built-in archive, panicking on failure. If an external initrd exists and `CONFIG_INITRAMFS_FORCE` is not set, it tries to unpack it as initramfs. When that fails and block RAM support exists, `populate_initrd_image()` writes `/initrd.image`; otherwise it logs failure. The routine then calls `security_initramfs_populated()`, frees or retains initrd memory, resets global initrd pointers, and flushes delayed `fput()` work.

## State And Persistence
Most parser state is `__initdata`: current header fields, checksum state, byte offsets, parser buffers, hardlink table, pending directory mtimes, `message`, and async cookie. Persistent effects are filesystem objects created in rootfs, optional `/sys/firmware/initrd` binary attribute when `retain_initrd`/`keepinitrd` is used, and cleared `initrd_start/initrd_end` after extraction. If `CONFIG_INITRAMFS_PRESERVE_MTIME` is enabled, file and directory mtimes are restored from archive metadata; otherwise normal creation times apply.

## Dependencies And Integration Points
The file depends on VFS/init syscall wrappers (`init_mkdir`, `init_mknod`, `init_link`, `init_symlink`, `init_utimes`, `kernel_write`), decompressor infrastructure, memblock, initrd globals, kexec crash reservation, sysfs firmware kobject, security hooks, async init domains, and boot parameters (`retain_initrd`, `keepinitrd`, `initramfs_async=`). `kernel_init_freeable()` in `init/main.c` calls `wait_for_initramfs()` before opening `/dev/console` or running init.

## Risks And Edge Cases
Archive parsing is sensitive to padding, `PATH_MAX`, missing NUL terminators, checksum mismatches, and malformed compression boundaries. Hardlink metadata can leak if not freed after archives without a trailer; this file explicitly frees it after unpacking. `mtime` is parsed into `time64_t` from old cpio fields with a noted y2106 limit. Bad writes can leave partially created files. Retaining initrd exposes raw boot image bytes through sysfs and requires the reserved memory to remain valid.

## Test Signals
`initramfs_test.c` directly targets `unpack_to_rootfs()` for regular files, directories, data integrity, checksum handling, hardlinks without trailers, many entries, padded filenames, path-length boundaries, and missing filename NUL termination. Boot integration is also exercised indirectly by initcall ordering and by systems booting with/without external initrd.
