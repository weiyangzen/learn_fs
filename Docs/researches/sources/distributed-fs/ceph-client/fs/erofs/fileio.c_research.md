<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fileio.c -->
# sources/distributed-fs/ceph-client/fs/erofs/fileio.c

## Purpose
`fileio.c` implements EROFS reads from filesystem image files, avoiding loop devices for file-backed images. It reads data through backing file `kiocb` operations while preserving EROFS folio completion semantics.

## Important APIs, types, and functions
Important types are `struct erofs_fileio_rq` and `struct erofs_fileio`. Important functions include `erofs_fileio_bio_alloc`, `erofs_fileio_submit_bio`, `erofs_fileio_scan_folio`, `erofs_fileio_read_folio`, `erofs_fileio_readahead`, and request allocation/completion helpers. It exports `erofs_fileio_aops`.

## Control flow
Scan initializes online folio tracking, maps file logical ranges with `erofs_map_blocks`, copies inline metadata directly, zero-fills holes, or batches mapped data into a backing-file read request. Requests use embedded bio vectors for page/offset/length accounting, then submit `vfs_iocb_iter_read` under the backing file credentials, optionally with `IOCB_DIRECT` when mount/direct and backing file support allow it. Completion checks short reads, ends online folio pieces or bio endio, uninitializes the bio, and drops request refs.

## State and persistence
Runtime state is request/bio/iocb refs, folio private counters, and backing file page cache or direct I/O state. The EROFS image and backing file are read-only from this path.

## Dependencies and integration points
It depends on EROFS block/device mapping, file-backed device info, VFS backing-file reads, credentials scoping, bio_vec helpers, and online folio completion in `data.c`.

## Risks and test signals
Risks include short-read handling, request refcount leaks, incorrect merging across device/physical discontinuities, `O_DIRECT` compatibility, and credential/path lifetime bugs. Test signals include file-backed mounts over regular files and block files, inline tails, holes, fragmented extents, readahead batching, direct I/O option, short read/error injection, and inode-sharing reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fileio.c -->
