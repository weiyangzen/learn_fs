# sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-resolve.c

## Purpose

`server-resolve.c` resolves client-supplied protocol references into server-side `loc_t` and `fd_t` objects before FOPs are resumed. It supports resolution by fd number, anonymous fd/GFID, inode GFID, and parent GFID plus basename, with cache-only fast paths and backend lookup fallback.

## Important APIs, types, and functions

The public entry point is `resolve_and_resume(call_frame_t *frame, server_resume_fn_t fn)`, which stores the resume callback and starts resolving `state->resolve` and `state->resolve2`. `server_resolve_all()` sequences first and second resolve slots, then calls `server_resolve_done()` to print traces and invoke the resume function. `server_resolve()` dispatches by `fd_no`, `pargfid`, or `gfid`. `resolve_entry_simple()`, `resolve_inode_simple()`, and `resolve_anonfd_simple()` try inode/fd cache resolution. `resolve_gfid()` and `resolve_name()` perform backend lookups through `STACK_WIND()` when cache state is missing or stale. Their callbacks link inodes into the table, remove stale dentries on `RESOLVE_NOT`, wipe temporary locs, and continue resolution. `server_resolve_fd()` maps remote fd numbers through the per-client `server_ctx_t` fdtable and has special handling for `GF_ANON_FD_NO`.

## Control flow

FOP decoders populate `server_state_t` resolve descriptors. `resolve_and_resume()` starts with `state->resolve`, resolves it synchronously if the cache is decisive or asynchronously via backend lookup if needed, then repeats for `state->resolve2`. Once both are complete, the original FOP resume function runs against `frame->root->client->bound_xl`. `copy_file_range` uses the same fd resolver twice, relying on whether `state->fd` is already populated to place the second fd in `state->fd_out`.

## State and persistence behavior

Resolution mutates `state->loc`, `state->loc2`, `state->fd`, `state->fd_out`, temporary `resolve_loc` objects, and the bound xlator inode table. Successful lookup paths link and lookup inodes so future operations can resolve from cache. Anonymous fd resolution creates temporary anonymous fds from inodes. No durable persistence is involved.

## Dependencies and integration points

The file depends on inode table APIs, loc construction/wiping, backend lookup FOPs, dict copy/ref, server fdtable context, and server state definitions. It is used by server FOP request handlers before winding requests to lower xlators.

## Risks and test signals

Risks include stale inode cache behavior, parent type validation, basename path traversal via `/`, asynchronous lookup lifetime, anonymous fd creation, and dual-fd ambiguity for `copy_file_range`. The code correctly rejects basenames containing `/` and uses backend lookup for stale or indecisive cache states. Tests should cover GFID-only resolve, parent+basename resolve, missing parent ESTALE fallback, `RESOLVE_NOT` stale dentry removal, invalid basename rejection, normal fd lookup, bad fd EBADF, anonymous fd read/write with flags, subdir mount interactions through inode table state, and two-fd `copy_file_range` resolution.
