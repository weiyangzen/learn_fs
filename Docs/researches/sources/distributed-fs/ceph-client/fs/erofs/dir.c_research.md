<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/dir.c -->
# sources/distributed-fs/ceph-client/fs/erofs/dir.c

## Purpose
`dir.c` implements EROFS directory iteration and directory file operations.

## Important APIs, types, and functions
Important functions are `erofs_readdir` and `erofs_fill_dentries`. The exported table is `erofs_dir_fops`. It reads `struct erofs_dirent` records and emits VFS entries with inode numbers converted through `erofs_nid_to_ino64`.

## Control flow
`erofs_readdir` walks directory blocks from `ctx->pos`, performs readahead for large directories, reads each block with `erofs_bread`, validates the first `nameoff`, adjusts arbitrary starting positions, and delegates record emission. `erofs_fill_dentries` computes each name length from the next record's offset or trailing string length, validates length/range, emits the entry, and advances position. If the on-disk directory omits `.`, a synthetic dot entry is emitted after normal entries.

## State and persistence
No persistent state changes. Runtime state includes directory page cache, readahead state, and `ctx->pos`.

## Dependencies and integration points
It depends on EROFS metadata/page-cache reads, directory block format, VFS dir_context, ioctl forwarding, compat ioctl, and generic leases.

## Risks and test signals
Risks include corrupted `nameoff` values, invalid name lengths, position rounding bugs, dot-omitted synthetic entry handling, and large-directory readahead behavior. Test signals include sorted directory images, malformed directory blocks, resume offsets, directories omitting `.`, long names, fatal-signal interruption, and ioctl passthrough on directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/dir.c -->
