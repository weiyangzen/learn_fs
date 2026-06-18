<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/read_write.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/read_write.c

## Purpose
`read_write.c` provides direct lower-file read/write primitives and an eCryptfs page-by-page write helper used outside the normal buffered write path. It translates upper inode offsets to lower file operations and applies encryption and metadata-size maintenance when needed.

## Important APIs, types, and functions
Important exported functions are `ecryptfs_write_lower`, `ecryptfs_write_lower_page_segment`, `ecryptfs_write`, `ecryptfs_read_lower`, and `ecryptfs_read_lower_page_segment`. The file uses `struct ecryptfs_inode_info` for the lower file pointer and `struct ecryptfs_crypt_stat` to decide whether to encrypt pages and update metadata.

## Control flow
`ecryptfs_write_lower` uses `kernel_write` against the lower file and marks the upper inode dirty. Page-segment helpers map a folio with `kmap_local_folio`, compute a byte offset from page index plus in-page offset, and call the lower read/write primitive. `ecryptfs_write` walks the requested range one page at a time, begins at old EOF when filling holes, reads the upper mapping folio, zero-fills hole portions or fresh-page tails, copies caller data, marks the folio uptodate, then either encrypts it or writes plaintext to the lower file. If the write extends size, it updates `i_size` and encrypted metadata size.

## State and persistence
The persistent output is lower file data and, for encrypted inodes, updated header/xattr size metadata. Runtime state includes mapped folio contents, inode size, lower-file availability, and signal interruption via `fatal_signal_pending`.

## Dependencies and integration points
It depends on the VFS kernel read/write helpers, folio mapping APIs, eCryptfs crypto routines, and metadata writer from `mmap.c`. Callers include metadata setup, truncate/extend flows, and any path that needs to write arbitrary upper bytes through the eCryptfs transform.

## Risks and test signals
Risks include using `data_offset` rather than the current segment length for plaintext page-segment writes, interruption leaving partially written data, lower file pointer loss returning `-EIO`, and metadata update failure after data has been written. Test signals include unencrypted writes across multiple pages, encrypted writes with holes, signal-interrupted writes, lower write short/error returns, reads past EOF, and lower-file missing scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/read_write.c -->
