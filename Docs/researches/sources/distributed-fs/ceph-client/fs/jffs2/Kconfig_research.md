# sources/distributed-fs/ceph-client/fs/jffs2/Kconfig

## Purpose
This Kconfig file defines the build-time feature surface for JFFS2. It exposes the base `JFFS2_FS` filesystem option, debug verbosity, write-buffer support, summary nodes, extended attributes, POSIX ACLs, security labels, selectable compression backends, and default compression mode.

## Important options
`JFFS2_FS` is a tristate that depends on `MTD` and selects `CRC32`; it states that JFFS2 is for MTD flash devices rather than normal block devices. `JFFS2_FS_DEBUG` is an integer verbosity level. `JFFS2_FS_WRITEBUFFER` defaults to yes and supports NAND, NOR with transparent ECC, and DataFlash. `JFFS2_FS_WBUF_VERIFY` optionally reads back write-buffer writes. `JFFS2_SUMMARY` enables summary information for faster mounts.

`JFFS2_FS_XATTR` gates extended attributes. `JFFS2_FS_POSIX_ACL` depends on xattrs, defaults to yes when xattrs are enabled, and selects `FS_POSIX_ACL`. `JFFS2_FS_SECURITY` also depends on xattrs and defaults to yes for security labels. Compression options are hidden behind `JFFS2_COMPRESSION_OPTIONS`, with zlib and rtime defaulting to yes, LZO and Rubin defaulting to no, and a choice among none, priority, size, and favour-LZO compression modes.

## Control flow and integration
Kconfig selections are consumed by the JFFS2 Makefile and preprocessor conditionals. For example, enabling POSIX ACLs compiles `acl.o` and turns the `acl.h` declarations into real operations; disabling them makes the header macros return no ACL support. Enabling xattrs pulls in xattr handlers, while security labels and ACLs layer on top of xattrs. Compression selections control which compressor object files are linked and which runtime default mode is built in.

## State and persistence behavior
This file does not persist runtime state, but its options affect on-flash compatibility. Compression backend choices can determine whether an image written by one kernel can be read by another. Summary support affects whether images can include mount-acceleration summary records. Xattrs, ACLs, and security labels persist extra metadata as JFFS2 xattr nodes.

## Dependencies and risks
The primary dependency is `MTD`. ACL and security options depend on xattr support. Zlib and LZO select their kernel compression libraries. The help text warns that removing compressors can make existing filesystems unreadable and enabling experimental compressors can reduce compatibility with standard kernels or bootloaders. `JFFS2_FS_DEBUG` level 1 is useful for bug reports but higher verbosity can be noisy.

## Test signals
Build matrix coverage should include base JFFS2 as built-in and module, write-buffer on/off, summary on/off, xattr with ACL/security combinations, each compressor backend, and each compression mode choice. Runtime smoke tests should mount MTD-backed images using selected features and verify expected object files are present in the linked module.
