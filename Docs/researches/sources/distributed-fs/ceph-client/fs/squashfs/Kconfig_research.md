# sources/distributed-fs/ceph-client/fs/squashfs/Kconfig

## Purpose

This Kconfig file defines the kernel configuration surface for SquashFS 4.0, a compressed read-only block-backed filesystem. It enables the core `SQUASHFS` tristate, chooses the file data decompression strategy, chooses or compiles decompressor threading modes, selects optional xattr and compression backends, and exposes performance/memory tuning options such as 4 KiB device block size and fragment cache size.

## Important APIs, Types, and Functions

There are no C APIs here; the important symbols are `SQUASHFS`, `SQUASHFS_FILE_CACHE`, `SQUASHFS_FILE_DIRECT`, `SQUASHFS_DECOMP_SINGLE`, `SQUASHFS_DECOMP_MULTI`, `SQUASHFS_DECOMP_MULTI_PERCPU`, `SQUASHFS_CHOICE_DECOMP_BY_MOUNT`, `SQUASHFS_MOUNT_DECOMP_THREADS`, `SQUASHFS_XATTR`, `SQUASHFS_COMP_CACHE_FULL`, compression backend symbols (`SQUASHFS_ZLIB`, `SQUASHFS_LZ4`, `SQUASHFS_LZO`, `SQUASHFS_XZ`, `SQUASHFS_ZSTD`), `SQUASHFS_4K_DEVBLK_SIZE`, `SQUASHFS_EMBEDDED`, and `SQUASHFS_FRAGMENT_CACHE_SIZE`.

## Control Flow

The file controls build-time inclusion and mount-time behavior indirectly. The file decompression choice selects either `file_cache.o` or `file_direct.o`; threading choices select one or more `decompressor_*` implementations; compression symbols select wrappers and library dependencies. `threads=` parsing in `super.c` is only available when the relevant mount-choice symbols are enabled.

## State and Persistence Behavior

Kconfig choices become compiled kernel configuration, not runtime state. Persistent effects are the module contents, available compression formats, maximum mount parameter flexibility, and cache/thread behavior for all mounted SquashFS images built with this kernel.

## Dependencies and Integration Points

`SQUASHFS` depends on `BLOCK`. Compression symbols select kernel decompression libraries. `SQUASHFS_XATTR` gates `xattr.o` and `xattr_id.o`. `SQUASHFS_FRAGMENT_CACHE_SIZE` is consumed through `squashfs_fs.h` and `super.c`.

## Risks and Edge Cases

Misconfigured compression support makes valid images unmountable. Thread and direct-decompression choices trade memory footprint, latency, and lock contention. `SQUASHFS_COMP_CACHE_FULL` improves repeated compressed-block reads but expands page-cache pressure. Fragment cache values that are too small cause repeated decompression; too large wastes memory on embedded builds.

## Test Signals

Useful signals include allmodconfig/allyesconfig build coverage, boot/mount tests for each compression format, mount tests for `threads=single`, `threads=multi`, `threads=percpu`, numeric thread counts where enabled, and repeated-read benchmarks with `SQUASHFS_COMP_CACHE_FULL` both disabled and enabled.
