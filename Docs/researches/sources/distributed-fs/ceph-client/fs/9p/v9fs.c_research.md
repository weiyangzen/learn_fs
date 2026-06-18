<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.c -->
# sources/distributed-fs/ceph-client/fs/9p/v9fs.c

## Purpose
`v9fs.c` provides 9p module initialization, mount option parsing, session creation/teardown, sysfs cache listing, and inode-cache setup.

## Important APIs, types, and functions
Important APIs are `v9fs_param_spec`, `v9fs_parse_param`, `v9fs_show_options`, `v9fs_session_init`, `v9fs_session_close`, `v9fs_session_cancel`, and `v9fs_session_begin_cancel`. Module lifecycle is `init_v9fs`/`exit_v9fs`; inode cache helpers manage `v9fs_inode_cache`.

## Control flow
Mount parsing fills `v9fs_context` session/client/transport option structs. Session init creates a p9 client, derives protocol/access flags, applies options, attaches a root fid, optionally acquires an FS-Cache session, and registers the session. Module init creates the inode slab, sysfs `fs/9p`, and registers the filesystem.

## State and persistence
Runtime state includes the global session list, sysfs kobject, inode slab cache, session flags/options, p9 client pointer, and optional fscache volume. No filesystem data is stored locally except optional FS-Cache contents.

## Dependencies and integration points
It depends on fs_context parsing, net/9p transports, p9 client creation/attach/disconnect, netfs inode storage, sysfs, and FS-Cache.

## Risks and test signals
Risks include ignored unknown mount options, transport module ref leaks, access mode fallback surprises, cachetag collisions, session-list locking, and teardown while requests are pending. Test signals include mount option matrix, unsupported transports, protocol versions, sysfs cache listing, failed attach cleanup, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/v9fs.c -->
