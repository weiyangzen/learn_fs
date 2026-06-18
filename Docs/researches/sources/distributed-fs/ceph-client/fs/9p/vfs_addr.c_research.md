<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_addr.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_addr.c

## Purpose
`vfs_addr.c` implements 9p address-space operations using the netfs library for buffered reads, readahead, dirty folios, writeback, and direct I/O stubs.

## Important APIs, types, and functions
It defines `v9fs_req_ops` and `v9fs_addr_operations`. Core callbacks are `v9fs_init_request`, `v9fs_free_request`, `v9fs_issue_read`, `v9fs_begin_writeback`, and `v9fs_issue_write`.

## Control flow
Netfs initializes each request by selecting a fid from the file or inode, setting request size from client msize/iounit, and storing the fid as private data. Read/write subrequests call `p9_client_read` or `p9_client_write`, report progress/errors to netfs, and release fid refs when the request ends.

## State and persistence
Per-request state is the referenced fid and request size. Persistent data resides on the 9p server; local cached folios are governed by netfs and optional FS-Cache.

## Dependencies and integration points
It depends on netfs APIs, p9 client I/O, fid lookup, page cache, trace/netfs events, and cache policy bits set during open.

## Risks and test signals
Risks include missing writable fid during writeback, short I/O handling, EOF/tail clearing, fid lifetime, and iounit/msize sizing. Test signals include buffered reads/writes, readahead, mmap writeback, writeback with write-only opens, direct I/O, short server reads, and cache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_addr.c -->
