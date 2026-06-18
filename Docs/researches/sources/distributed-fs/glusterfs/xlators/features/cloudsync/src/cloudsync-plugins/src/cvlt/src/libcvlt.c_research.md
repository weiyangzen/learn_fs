# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.c

## Purpose
Implements the Commvault/openarchive cloudsync plugin, supporting both full recall/download and direct remote reads from an archive store.

## Important APIs, types, and functions
Exports `store_ops` with `cvlt_download`, `cvlt_read`, `cvlt_init`, `cvlt_reconfigure`, and `cvlt_fini`. `archive_t` stores dynamic library handle, request pool, iobuf pool, archive descriptor/method table, product/store IDs, and a trailer guard. `cvlt_extract_store_fops()` loads `libopenarchive.so` and obtains `get_archstore_methods()`. Request helpers allocate/destroy `cvlt_request_t`. `cvlt_download_complete()` posts a semaphore; `cvlt_readv_complete()` unwinds Gluster readv with an iobuf.

## Control flow
Initialization validates graph shape, allocates archive state, creates pools, loads archive methods, initializes the external store, and reads `cloudsync-store-id`/`cloudsync-product-id`. `cvlt_download()` builds source archive and destination Gluster store/file info from `cs_loc_xattr_t`, submits external `restore()`, waits on a semaphore, and returns success/failure to cloudsync recall. `cvlt_read()` validates offset/size, allocates an aligned iobuf, prepares request metadata and size xattrs, submits external `read()`, and returns asynchronously; completion constructs iovec/iobref, adjusts stat size, signals EOF via `ENOENT`, unwinds, and frees the request.

## State and persistence behavior
Runtime state is in `archive_t` and per-request pool objects. Persistent data resides in the external archive store and Gluster file/xattr state that cloudsync supplies. The plugin uses product/store IDs and archive UUID/path xattrs to locate remote objects.

## Dependencies and integration points
Depends on `libopenarchive.so`, `archivestore.h`, GlusterFS iobuf/mempool/locking/logging APIs, semaphores, and cloudsync common state. It is the only plugin here implementing `fop_remote_read`, enabling `cloudsync-remote-read`.

## Risks and test signals
Risks include blocking `sem_wait()` during restore, ABI mismatch with external archive methods, request-pool exhaustion, trailer guard misuse after memory corruption, EOF signaled through `ENOENT`, and async callback lifetime of `frame`/`local`. Source snapshot has duplicate `iov.iov_len = op_ret`. Tests should cover init without `libopenarchive.so`, restore success/failure, remote read at EOF and zero size, callback after failure, concurrent reads up to pool size, and reconfigure of product/store IDs.
