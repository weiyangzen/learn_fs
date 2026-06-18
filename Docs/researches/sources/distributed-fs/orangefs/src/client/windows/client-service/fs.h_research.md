# sources/distributed-fs/orangefs/src/client/windows/client-service/fs.h

## Purpose
`fs.h` declares the service-side OrangeFS filesystem abstraction used by the Dokany layer. It presents path-based and object-ref-based operations over the OrangeFS system interface.

## Important APIs, Types, And Functions
It exposes initialization/finalization (`fs_initialize`, `fs_finalize`), mount lookup (`fs_get_mntent`, `fs_get_id`, `fs_get_name`), path conversion (`fs_resolve_path`), namespace operations (`fs_lookup`, `fs_create`, `fs_remove`, `fs_rename`, `fs_mkdir`), metadata operations (`fs_truncate`, `fs_getattr`, `fs_setattr`, `fs_get_diskfreespace`), IO (`fs_io`, `fs_io2`, plus read/write macros), flush, and directory paging (`fs_find_files`).

## Control Flow
The header is purely declarative. Callers initialize the library against a tab file, resolve Windows paths to OrangeFS paths, perform operations with a `PVFS_credential`, and finalize at service shutdown. The `fs_read`/`fs_write` macros route through lookup-based `fs_io`; `fs_read2`/`fs_write2` route through object-ref-based `fs_io2`.

## State And Persistence
The header does not define state, but its API implies persistent OrangeFS mutations through create/remove/rename/truncate/setattr/write/flush and process-global mount table state initialized by `fs_initialize`.

## Dependencies And Integration Points
It includes `pvfs2.h` and is consumed by `dokany-interface.c` and service initialization code. It also defines the seam where tests through Dokany indirectly reach OrangeFS system calls.

## Risks And Test Signals
The API uses mutable `char *` paths and caller-owned output buffers, so buffer size discipline is a caller responsibility. `PVFS_sys_attr` ownership is not obvious from declarations; implementation releases allocated fields internally in some cases. The object-ref IO API is essential for performance but requires cache invalidation to be correct. Tests exercise the API indirectly through mounted-drive behavior, not as unit tests.
