# sources/distributed-fs/ceph-client/fs/nfs/fscache.h

Purpose: declares the NFS fscache/netfs interface and provides compile-time stubs when filesystem cache support is disabled.

Important APIs and types: defines `struct nfs_fscache_inode_auxdata`, the coherency record persisted with cached inode data; `struct nfs_netfs_io_data`, the bridge object used to terminate netfs subrequests once all NFS RPC fragments complete; inline refcount helpers `nfs_netfs_get` and `nfs_netfs_put`; `nfs_netfs_inode_init`; exported fscache routines; netfs read entry points; folio release and invalidation helpers; fscache state string helper; and setters that pass netfs state between pageio descriptors and pgio headers.

Control flow: when `CONFIG_NFS_FSCACHE` is enabled, callers initialize netfs state in each NFS inode, acquire/release superblock and inode cookies, use/unuse cookies on open/close, and route read_folio/readahead through netfs. `nfs_netfs_put` is the key completion gate: the final reference clamps transferred bytes to the requested subrequest length, stores the error, calls `netfs_read_subreq_terminated`, and frees the bridge object. When disabled, functions become no-ops or `-ENOBUFS` returns while preserving call sites.

State and persistence behavior: auxdata mirrors inode mtime/ctime and NFSv4 change_attr into fscache coherency metadata. Invalidation is non-sleeping and passes auxdata plus current i_size. The enabled path records cookie state in `NFS_I(inode)->netfs`; disabled stubs intentionally persist nothing.

Dependencies and integration points: includes swap, NFS mount/version headers, fscache, and iversion. It references `nfs_netfs_ops` implemented in `fscache.c`, NFS server/client version data, and netfs/fscache folio release APIs. It is used from inode allocation/clear, open/close, cache invalidation, and pageio read paths.

Risks: the header encodes different behavior under configuration flags, so build coverage must include both enabled and disabled fscache. Completion clamping in `nfs_netfs_put` protects against pageio overread warnings; regressions here would show as netfs accounting errors. `nfs_fscache_release_folio` waits on deprecated private state only when allowed by reclaim context.

Test signals: allmodconfig and fscache-disabled builds, netfs subrequest split/completion refcounts, invalidation auxdata for NFSv3 vs NFSv4, folio release under kswapd and non-`__GFP_FS`, and pageio propagation of `pg_netfs` between descriptor and header.
