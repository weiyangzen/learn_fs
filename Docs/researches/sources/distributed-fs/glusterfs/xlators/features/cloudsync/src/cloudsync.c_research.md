# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync.c

## Purpose
Implements the cloudsync feature translator, which presents archived/remote files through GlusterFS by tracking object state xattrs, recalling data before local modification, and optionally serving reads directly from a remote plugin.

## Important APIs, types, and functions
Lifecycle APIs are `cs_init`, `cs_fini`, `cs_reconfigure`, `cs_notify`, and `cs_mem_acct_init`. Fops include manual implementations for `readdirp`, `truncate`, `setxattr`, `unlink`, `open`, `fstat`, `readv`, and generated fops for many others. Core helpers include `cs_local_init`, `locate_and_execute`, inodelk helpers, `cs_do_stat_check`, `cs_stat_check_cbk`, `cs_resume_postprocess`, `cs_download`, `cs_serve_readv`, inode context helpers, and `cs_common_cbk`.

## Control flow
Init allocates translator private state, local mem pool, loads an optional plugin by `cloudsync-storetype`, resolves `store_ops`, and initializes plugin config. Normal lookup/stat/open/fstat/read/write requests ask the child for `GF_CS_OBJECT_STATUS` so inode context can cache local/remote/downloading/error state. Data-modifying operations on remote/downloading files create a call stub, take an inodelk under `CS_LOCK_DOMAIN`, do a repair stat with object-status and archive-UUID requests, update remote path/xattr info, recall the file through plugin `dlfop`, unlock, and resume the original fop. If `cloudsync-remote-read` is enabled and a file remains `GF_CS_REMOTE`, readv uses plugin `rdfop` instead of recalling.

## State and persistence behavior
In-memory state includes `cs_private_t`, plugin config, per-inode `cs_inode_ctx_t`, and per-frame `cs_local_t`. Persistent behavior is mediated by lower translators and plugins through xattrs such as `GF_CS_OBJECT_STATUS`, `GF_CS_OBJECT_REMOTE`, `GF_CS_OBJECT_DOWNLOADING`, `GF_CS_OBJECT_REPAIR`, `GF_CS_XATTR_ARCHIVE_UUID`, and upload-complete markers. Downloads mark objects as downloading, write data, and remove remote/downloading xattrs.

## Dependencies and integration points
Depends on GlusterFS stack, call stubs, syncop fsetxattr/fremovexattr/ftruncate, dynamic loader, mem pools, inode context APIs, and cloudsync plugin shared objects. Integrates with generated fops, cloudsync-common cleanup, S3/CVLT plugins, and lower storage xattrs.

## Risks and test signals
Risks include plugin load failures treated as nonfatal no-plugin mode, null `priv->stores` on reconfigure, stale inode context, inodelk leaks on unusual errors, blocking downloads in fop path, direct remote-read callback lifetime, and xdata ownership. Source snapshot has brace/duplicate-token oddities in `cs_truncate_cbk`. Tests should cover local and remote states for read/write/truncate, upload-complete setxattr, remote-read enabled/disabled, plugin absent, plugin hook missing, repair stat failure, concurrent recalls, and xattr cleanup after successful/failed download.
