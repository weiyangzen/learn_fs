# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-common.c

## Purpose

`server-common.c` contains response post-processing helpers for the version 4 server protocol path. These functions translate backend callback results into generated `gfx_*` RPC response structures and keep server-side inode/fd tables synchronized with successful namespace and fd operations.

## Important APIs, types, and functions

The helpers include simple translators such as `server4_post_readlink()`, `server4_post_statfs()`, `server4_post_readv()`, `server4_post_seek()`, `server4_post_lease()`, and `server4_post_rchecksum()`. Metadata helpers `server4_post_common_iatt()`, `server4_post_common_2iatt()`, `server4_post_common_3iatt()`, and `server4_post_common_3iatt_noinode()` serialize iatts and optionally link inodes. Directory helpers delegate to `serialize_rsp_dirent_v2()` and `serialize_rsp_direntp_v2()`. Namespace-mutating helpers update the inode table: `server4_post_entry_remove()` unlinks and forgets, `server4_post_rename()` handles destination replacement and `inode_rename()`, `server4_post_lookup()` links looked-up inodes and handles namespace marker xdata, and `server4_post_link()` links hardlinks. `server4_post_open()` and `server4_post_create()` bind fds and allocate server-side fd numbers in the per-client `server_ctx_t` fdtable.

## Control flow

Version-specific FOP callbacks call these helpers after successful backend operations and before `server_submit_reply()`. The helpers perform protocol conversion with `gfx_stat_from_iattx()`, `gf_statfs_from_statfs()`, `gf_proto_flock_from_flock()`, and related conversion routines. Open/create helpers obtain `server_ctx_get(frame->root->client, this)` and allocate remote fd numbers using `gf_fd_unused_get()`.

## State and persistence behavior

The file mutates in-memory inode and fd state. Successful create/link/lookup/rename/remove operations update the server inode table so later client GFID/name resolution can be cache-assisted. Open/create bind and reference fds, then store them in a per-client fdtable. Subdirectory mounts rewrite the apparent root gfid/inode number to the conventional root gfid for responses to the client.

## Dependencies and integration points

This file depends on generated `glusterfs3`/`glusterfs4` XDR types, inode/fd table APIs, `server_ctx_get()`, dirent serialization helpers, and server state from `server.h`. It is integrated by `server-rpc-fops_v2.c` callback paths.

## Risks and test signals

The riskiest behavior is inode table correctness after rename, create, link, lookup, and remove, especially destination replacement and subdir-mount root rewriting. Fd reference and fdtable allocation must stay balanced with release/cleanup paths. Tests should cover create/open remote fd allocation, rename over existing entries, directory unlink forget behavior, subdir mounts reporting root gfid as `000...001`, readdir/readdirp serialization cleanup, and lock type conversion in `server4_post_lk()`.
