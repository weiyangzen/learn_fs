<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.h -->
# sources/distributed-fs/ceph-client/fs/9p/cache.h

## Purpose
`cache.h` declares FS-Cache helpers for 9p and supplies stubs when cache support is not compiled.

## Important APIs, types, and functions
It declares `v9fs_cache_session_get_cookie` and `v9fs_cache_inode_get_cookie` under `CONFIG_9P_FSCACHE`; otherwise `v9fs_cache_inode_get_cookie` is an inline no-op.

## Control flow
No standalone control flow. Call sites can unconditionally call inode cookie setup while cache-disabled builds compile to no-op behavior.

## State and persistence
No state is defined in the header.

## Dependencies and integration points
It connects `v9fs.c`, inode setup, and optional `cache.c` without scattering config conditionals.

## Risks and test signals
Risks are missing stubs for session functions or incorrect conditional call sites. Test signals include cache-enabled/disabled builds and mount option handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/cache.h -->
