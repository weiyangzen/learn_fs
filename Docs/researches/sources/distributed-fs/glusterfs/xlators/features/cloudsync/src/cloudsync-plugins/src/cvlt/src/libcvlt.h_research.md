# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/libcvlt.h

## Purpose
Declares CVLT plugin structures, operation enum, request state, archive private state, and plugin lifecycle/fop entry points.

## Important APIs, types, and functions
Defines `cvlt_op_t`, `cvlt_request_t`, and `archive_t`. `cvlt_request_t` carries read offsets, byte counts, iobuf/iobref, frame, operation result, semaphore, archive store/file info, and size xattrs. `archive_t` owns locks, xlator pointer, dynamic library handle, pools, archive descriptor, method table, product/store id, and trailer. Declares `cvlt_init`, `cvlt_reconfigure`, `cvlt_fini`, `cvlt_download`, and `cvlt_read`.

## Control flow
`libcvlt.c` allocates `archive_t` during plugin init and allocates `cvlt_request_t` per restore/read. Cloudsync invokes the declared fops through `store_ops`.

## State and persistence behavior
Models in-memory plugin and request state. Persistent remote identity is carried by archive store/file info references populated from xattrs.

## Dependencies and integration points
Depends on semaphores, Gluster compat errno, cloudsync common types, memory tags, and `archivestore.h`.

## Risks and test signals
The structs are internal but tied to async callback lifetime. Tests should validate request cleanup, iobref/iobuf refcounting, and store info validity after reconfigure.
