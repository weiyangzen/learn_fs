# sources/cloud-native/composefs/tools/cfs-fuse.c

## Purpose
`cfs-fuse.c` implements an experimental read-only FUSE low-level server for mounting composefs EROFS images from userspace. It maps a composefs image, interprets EROFS metadata directly, resolves redirected file payloads from an object `basedir`, and exposes lookup, directory, symlink, xattr, read, and seek operations through `fuse_lowlevel_ops`.

## Important APIs, Types, And Functions
The global image state includes `erofs_data`, `erofs_data_size`, `erofs_root_nid`, `erofs_super`, `cfs_header`, `erofs_metadata`, `erofs_xattrdata`, build timestamps, ACL enablement, and `basedir_fd`. `struct cfs_data` carries parsed FUSE options: `source`, `basedir`, and `noacl`.

Key helpers translate between FUSE inode numbers and EROFS nids (`cfs_nid_from_ino`, `cfs_ino_from_nid`), fetch inodes (`cfs_get_erofs_inode`), decode inode metadata (`cfs_stat`, `erofs_inode_get_mode`, `erofs_inode_get_info`), detect overlay whiteouts (`erofs_inode_is_whiteout`), compare non-null-terminated directory names (`memcmp2`), and rewrite/filter xattrs (`cfs_xattr_rewrite`, `do_getxattr`).

FUSE callbacks are assembled in `cfs_oper`: `cfs_init`, `cfs_lookup`, `cfs_getattr`, `cfs_opendir`, `cfs_readdir`, `cfs_readdir_plus`, `cfs_readlink`, `cfs_listxattr`, `cfs_getxattr`, `cfs_open`, `cfs_release`, `cfs_read`, and `cfs_lseek`.

## Control Flow
`main` parses FUSE command-line options, forces `ro,default_permissions`, opens and mmaps `source`, opens `basedir` with `O_PATH`, validates composefs and EROFS magic values, initializes global metadata pointers from the superblock, creates and mounts a FUSE session, daemonizes if requested, and enters either single-threaded or multithreaded FUSE loops.

Directory lookup and readdir operate directly on EROFS dirent blocks. `cfs_lookup` binary-searches sorted directory blocks, searches an inline tail block when present, filters whiteouts, and replies with `fuse_entry_param`. `_cfs_readdir` walks blocks from the requested offset and uses either `fuse_add_direntry` or `fuse_add_direntry_plus`.

File open checks write flags, reads trusted `overlay.redirect`, strips leading slashes, and opens the redirected object beneath `basedir_fd`. If there is no redirect, reads are served from inline/flat EROFS data via `cfs_read_inline`; otherwise `cfs_read` replies using FUSE fd-splice data.

## State And Persistence
Runtime state is global, process-local, and read-only after initialization except for FUSE request handling. The image is memory-mapped `MAP_PRIVATE`; redirected payloads are opened per file handle and closed in `release`. No persistent state is written. Cache hints (`keep_cache`, `cache_readdir`, long attr/entry timeouts) rely on immutable image semantics.

## Dependencies And Integration Points
This file depends on libfuse3 low-level APIs, Linux mount/fsverity/loop headers, EROFS composefs internal structures, and libcomposefs utility endian helpers. It integrates with composefs image files produced by `mkcomposefs`, object stores referenced by overlay redirect xattrs, and mount consumers expecting normal POSIX read-only filesystem behavior.

## Risks
`cfs_get_erofs_inode` has a TODO for bounds checking, so malformed images can point outside mapped metadata. Many dirent/xattr walks trust on-disk lengths. `cfs_read_inline` ignores the read offset when assigning `iov_base`, which is a correctness risk for inline flat reads. Fs-verity verification for redirected objects is explicitly TODO. Global state plus multithreaded FUSE is mostly read-only but assumes immutable mappings and stable `basedir_fd`.

## Test Signals
Useful tests are mount smoke tests over generated composefs images, lookup/readdir/readdirplus with tailpacked directories, xattr filtering and ACL-disabled behavior, whiteout hiding, symlink reads, inline file reads with nonzero offsets, redirected object reads, and malformed image fuzzing for bounds and length handling. The Meson target only builds this tool when `fuse3_dep` is found.
