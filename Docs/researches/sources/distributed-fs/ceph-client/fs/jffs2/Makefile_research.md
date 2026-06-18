# sources/distributed-fs/ceph-client/fs/jffs2/Makefile

## Purpose
The Makefile maps JFFS2 Kconfig selections to the `jffs2.o` composite object. It defines the always-built core object list for `CONFIG_JFFS2_FS` and appends optional feature objects for write buffering, xattrs, security labels, ACLs, compressors, and summary support.

## Important build rules
`obj-$(CONFIG_JFFS2_FS) += jffs2.o` builds JFFS2 only when the main Kconfig option is enabled. The base `jffs2-y` list includes compression framework code, directory/file/ioctl operations, node management, allocation helpers, read/write/scan/GC paths, symlink/build/erase/background/fs/writev/super/debug code. Conditional additions include `wbuf.o`, `xattr.o xattr_trusted.o xattr_user.o`, `security.o`, `acl.o`, `compr_rubin.o`, `compr_rtime.o`, `compr_zlib.o`, `compr_lzo.o`, and `summary.o`.

## Control flow and integration
This file is the build-system bridge from `Kconfig` to source inclusion. It ensures `build.o` and `background.o` are part of the core filesystem, while `acl.c` is present only with `CONFIG_JFFS2_FS_POSIX_ACL`. Xattr support is required before ACL/security objects are meaningful because those features persist metadata through xattr nodes. Compression objects correspond to the Kconfig backend options.

## State and persistence behavior
The Makefile has no runtime state, but the linked object set controls supported on-flash formats and metadata. Omitting a compressor may prevent reading nodes compressed by that algorithm. Omitting summary support disables summary-node consumption/production. Omitting ACL/security removes support for persisted xattr classes.

## Dependencies, risks, and test signals
Risks are mostly configuration drift: adding a new source file or Kconfig option without updating this Makefile would silently exclude functionality. Build tests should cover `CONFIG_JFFS2_FS=m/y`, optional xattr/ACL/security combinations, all compressor toggles, summary support, and link verification that each enabled object is included in `jffs2.o`.
