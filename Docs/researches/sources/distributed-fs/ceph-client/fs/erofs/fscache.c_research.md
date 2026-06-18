<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fscache.c -->
# sources/distributed-fs/ceph-client/fs/erofs/fscache.c

## Purpose
`fscache.c` implements deprecated fscache/cachefiles-backed on-demand EROFS access. It registers volumes/cookies, creates anonymous inodes for blobs, reads metadata and data through netfs cache operations, and supports shared domains for deduplicated blob access.

## Important APIs, types, and functions
Important types are `struct erofs_fscache_io`, `struct erofs_fscache_rq`, and `struct erofs_fscache_bio`. Important functions include `erofs_fscache_read_io_async`, metadata/data folio read and readahead helpers, `erofs_fscache_bio_alloc`, `erofs_fscache_submit_bio`, cookie/domain register/unregister helpers, `erofs_fscache_register_fs`, and `erofs_fscache_unregister_fs`. It exports `erofs_fscache_access_aops`.

## Control flow
Reads allocate request objects covering folio or readahead ranges, map logical data with `erofs_map_blocks`, copy inline metadata, zero holes, or resolve device cookies and issue on-demand fscache reads into xarray iterators. Completion marks folios uptodate or records errors and unlocks them. Registration creates or reuses fscache volumes, optionally creates shared domains backed by a pseudo mount, enforces primary blob uniqueness in shared domains, acquires cookies, calls `fscache_use_cookie`, and creates anonymous metadata inodes using fscache meta aops.

## State and persistence
Runtime state includes global domain/cookie lists, pseudo mount, fscache volumes/cookies, anonymous inodes, request refs, and cache resources. Persistent data is external cache content and the immutable EROFS blobs; this code does not modify filesystem images.

## Dependencies and integration points
It depends on fscache, cachefiles ondemand, netfs APIs, EROFS map/dev resolution, anonymous filesystem mounts, xarray iterators, and multi-device blob naming.

## Risks and test signals
Risks include domain/cookie refcount leaks, shared-domain name collisions, incomplete async read completion, folio unlock without uptodate on errors, pseudo mount lifetime, and deprecated API behavior. Test signals include fscache mounts with and without domains, duplicate fsid in a domain, metadata reads, data readahead, holes and inline data, external devices, cache read failures, and concurrent unregister during I/O teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fscache.c -->
