# sources/distributed-fs/ceph-client/fs/jffs2/os-linux.h

## Purpose

`os-linux.h` is the Linux adaptation layer for JFFS2. It maps generic JFFS2 inode and superblock concepts onto Linux VFS structures, provides time and mode conversions, defines no-op versus real write-buffer behavior depending on configuration, and declares Linux-specific JFFS2 entry points used across the filesystem.

## Important APIs, Types, And Functions

The key macros are `JFFS2_INODE_INFO()`, `JFFS2_SB_INFO()`, `OFNI_EDONI_2SFFJ()`, `OFNI_BS_2SFFJ()`, inode field accessors such as `JFFS2_F_I_SIZE()`, and time helpers such as `JFFS2_NOW()` and `JFFS2_CLAMP_TIME()`. `jffs2_init_inode_info()` initializes the per-inode JFFS2 state: highest version, fragment tree, metadata, dirents, symlink target, flags, and compression preference.

Configuration gates define write-buffered and non-write-buffered behavior. Without `CONFIG_JFFS2_FS_WRITEBUFFER`, flash reads/writes map directly to MTD operations, write-buffer flush/setup functions are no-ops, and `jffs2_can_mark_obsolete()` is disabled when summaries are enabled. With write-buffer support, this header declares `wbuf.c` APIs for buffered writes, OOB cleanmarkers, bad-block marking, delayed flushing, and NAND/DataFlash/NOR/UBI setup.

It also declares VFS operation tables and filesystem functions from `background.c`, `dir.c`, `file.c`, `fs.c`, `ioctl.c`, `symlink.c`, and `writev.c`.

## Control Flow

This header is not executable control flow by itself, but it shapes compile-time control flow throughout JFFS2. Callers invoke `jffs2_flash_write()`, `jffs2_flash_read()`, `jffs2_flush_wbuf_pad()`, and related helpers uniformly; preprocessor macros either route them to `wbuf.c` or to direct MTD functions. Mount, inode, and write paths include this layer indirectly through `nodelist.h` to avoid scattering Linux VFS details into generic JFFS2 logic.

## State And Persistence Behavior

`jffs2_init_inode_info()` sets volatile in-core inode state. The write-buffer macros control persistence semantics: direct-write builds may mark obsolete nodes in-place and write directly to MTD, while write-buffer builds must account for page-sized programming units, pending buffered data, OOB cleanmarkers, and media-specific setup/cleanup.

Time helpers clamp Linux `time64_t` values into the 32-bit on-medium timestamp fields used by JFFS2, preventing overflow in persisted raw inode fields.

## Dependencies And Integration Points

The file integrates Linux VFS (`struct inode`, `struct super_block`, `struct kstatfs`, operation tables), MTD (`mtd_read`, direct write wrappers), capabilities of the selected flash type, and optional summary support. It is included by JFFS2 implementation files through `nodelist.h`, making it a central ABI contract for the Linux port.

## Risks And Edge Cases

Macro behavior differs substantially by configuration. Tests that pass on direct NOR-like builds may miss write-buffer-only behavior, and summary-enabled direct-write builds intentionally disable physical obsolete marking. Time clamping can silently saturate values beyond `U32_MAX`. The reversed helper names (`OFNI_*`) are historical and easy to misuse, so call-site type expectations matter.

## Test Signals

Build matrix coverage should include write-buffer off, write-buffer on, summary on/off, xattr/ACL on/off, NAND/DataFlash/NOR/UBI setup paths, and remount/read-only behavior. Compile-time coverage is important because many APIs are macros in one configuration and real functions in another.
