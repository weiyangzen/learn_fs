# Research: sources/distributed-fs/glusterfs/xlators/protocol/server/src/server-rpc-fops_v2.c

Purpose:
This file implements the GlusterFS 4.x/v2 server-side file-operation RPC program. It is the protocol/server dispatch layer that decodes incoming `gfx_*_req` XDR messages, builds per-call `server_state_t`, resolves GFIDs/fds/names through the server resolver, winds into the bound child translator FOP, converts callback results into `gfx_*_rsp` XDR response structures, and submits replies back through `server_submit_reply`. It covers the full data-plane surface: lookup, namespace operations, inode/fd operations, locks, xattrs, directory reads, lease/upcall-related lock migration operations, `put`, `icreate`, `namelink`, and `copy_file_range`.

Important APIs, types, and functions:
- `rpc_receive_common()` is the shared request intake helper. It XDR-decodes `req->msg[0]`, returns the XDR header length when needed for payload slicing, obtains a call frame via `get_frame_from_request()`, sets `frame->root->op`, captures `CALL_STATE(frame)`, and rejects requests whose client is not bound or whose bound translator lacks an inode table.
- `set_resolve_gfid()` maps on-wire root GFIDs to a subdirectory mount root GFID when `client->subdir_mount` is active.
- Callback functions named `server4_*_cbk()` translate child FOP results to protocol responses; resume functions named `server4_*_resume()` validate resolver status and `STACK_WIND()` into `bound_xl->fops`; request actors named `server4_0_*()` decode XDR and call `resolve_and_resume()`.
- `server4_0_writev_vecsizer()` sizes write headers and xdata before opaque payload reads.
- `glusterfs4_0_fop_actors[]` and `glusterfs4_0_fop_prog` expose the RPC procedure table for `GLUSTER_FOP_VERSION_v2`.

Control flow:
The normal request path is decode, frame allocation, state population, resolve, resume, child FOP, callback, response serialization. Path operations fill `state->resolve` or `state->resolve2` with GFID/parent GFID/basename and a resolution policy. Fd operations set `state->resolve.fd_no` plus GFID. After `resolve_and_resume()` completes, the matching resume function either unwinds an error callback or winds into the child FOP.

State and persistence behavior:
The file does not persist data directly. Its mutable state is per-RPC `server_state_t`, client fdtable entries referenced by numeric fd handles, inode table updates caused by lookup/create/readdirp responses, and temporary XDR/dict/iobuf references. Open/create/opendir allocate `fd_t` objects and callbacks publish a server fd number. Release/releasedir bypass the normal resolver and drop fdtable entries with `gf_fd_put()`.

Dependencies and integration points:
This file depends on `server.h`, `server-helpers.h`, `server-common.h`, `rpc-common-xdr.h`, generated XDR types/functions, resolver code through `resolve_and_resume()`, child translator FOP vectors, and shared protocol conversion helpers.

Risks and edge cases:
Memory ownership is subtle across duplicated request strings, XDR dictionary arrays, lock-owner buffers, iobrefs, and frame-local state. Malformed XDR/xdata should destroy state cleanly. `GF_ASSERT(state->size == len)` in `writev` and `put` can make malformed payloads fatal in assertion-enabled builds. `server4_open_resume()` does not visibly check `fd_create()` for NULL before assigning flags. Namespace xattr and cross-namespace rename/link checks are security-sensitive.

Test signals:
Cover malformed XDR and xdata, subdir-mount root resolution, lookup revalidation ENOENT/inode forget, fd lifecycle, writev/put payload splitting, namespace xattr rejection, lock conversions, cross-namespace link/rename rejection, readdir size clamping, unsupported compound, and actor-table coverage.
