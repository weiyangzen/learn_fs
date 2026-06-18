# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs.pc.in

This is the pkg-config template for libzfs.

Fields:
- `Name: libzfs`
- `Description: LibZFS library`
- `Version: @VERSION@`
- `URL: https://github.com/openzfs/zfs`

Dependencies and flags:
- Public requirement: `libzfs_core`.
- Private requirements: configured libcrypto and zlib pkg-config dependencies.
- Cflags expose `${includedir}/libzfs` and `${includedir}/libspl`.
- Public libs: `-L${libdir} -lzfs -lnvpair`.
- Private libs: `-luutil -lm -pthread`.

Use:
- Downstream consumers use this template after configure substitution to compile and link against installed libzfs.
