# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/buffered.h

Purpose: Public declarations for buffered VFS IO.

Key APIs and behavior:
- Defines `struct bch_writepage_io` wrapping inode pointer and trailing `bch_write_op`.
- Declares single-folio read, VFS read_folio, writepages, readahead, write_begin/write_end, and write_iter.
- Adapts `write_begin`/`write_end` prototypes for kernel version 6.17+.

Integration:
- Implemented by `buffered.c`.
- Guarded by `NO_BCACHEFS_FS`.
- Includes write type definitions.

Risks and invariants:
- `bch_writepage_io` requires `op` to remain last for container/bioset allocation layout.
