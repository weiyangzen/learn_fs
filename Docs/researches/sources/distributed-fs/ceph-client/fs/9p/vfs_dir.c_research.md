<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dir.c -->
# sources/distributed-fs/ceph-client/fs/9p/vfs_dir.c

## Purpose
`vfs_dir.c` implements directory iteration for legacy 9P stat streams and 9P2000.L dirent streams.

## Important APIs, types, and functions
It defines private `struct p9_rdir`, helpers `dt_type` and `v9fs_alloc_rdir_buf`, readdir implementations `v9fs_dir_readdir` and `v9fs_dir_readdir_dotl`, and file operation tables `v9fs_dir_operations` and `v9fs_dir_operations_dotl`.

## Control flow
Directory open reuses `v9fs_file_open`. Iteration allocates a per-fid buffer, fills it with `p9_client_read` or `p9_client_readdir` when consumed, decodes entries with `p9stat_read` or `p9dirent_read`, emits them to the VFS, and advances `ctx->pos` according to protocol encoding.

## State and persistence
Per-directory fid state includes the reusable `rdir` buffer with head/tail offsets. Directory contents persist only on the remote server.

## Dependencies and integration points
It depends on p9 stat/dirent parsers, p9 client read/readdir, VFS `dir_context`, and shared file open/release.

## Risks and test signals
Risks include corrupt directory records, ctx position handling differences, buffer sizing from msize, and memory retained on fid until release. Test signals include large directories, partial dirent buffers, dotl and legacy servers, seekdir/telldir behavior, and malformed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/9p/vfs_dir.c -->
