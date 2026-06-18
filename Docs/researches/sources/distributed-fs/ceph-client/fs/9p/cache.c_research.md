<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.c -->
# sources/distributed-fs/ceph-client/fs/9p/cache.c

## Purpose
`cache.c` integrates 9p with FS-Cache for persistent read caching of regular files.

## Important APIs, types, and functions
It implements `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie`.

## Control flow
Session setup builds a volume key from device name and cachetag/aname, sanitizes slashes, and acquires an FS-Cache volume. Inode setup for regular files derives cookie keys from qid path/version, acquires an fscache cookie, and marks the mapping for release callbacks.

## State and persistence
State includes session `fscache` volume pointers and netfs inode cache cookies. Cached file data is persisted by the FS-Cache backend according to its policy; the 9p client stores only references.

## Dependencies and integration points
It depends on FS-Cache, netfs inode state, qid metadata, and mount cache options.

## Risks and test signals
Risks include duplicate volume keys, stale data when qid version is unreliable, non-regular inode cookies, and cache resize/relinquish ordering. Test signals include `cache=fscache`, duplicate cache tags, qid version changes, file truncation, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.c -->
