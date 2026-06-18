## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/mgmt-pmap.c

Purpose: implements a minimal RPC client request used by brick processes to sign out from glusterd's portmap service.

Important APIs: `clnt_pmap_signout_prog` describes the Gluster portmap RPC program/procedure. `rpc_clnt_mgmt_pmap_signout` builds and submits a `pmap_signout_req`. `mgmt_pmap_signout_cbk` decodes `pmap_signout_rsp` and destroys the call frame.

Control flow: signout creates a frame, validates that brick port/name data exists, chooses a brick identifier with RDMA suffix handling, fills port and RDMA port, allocates an `iobref` and `iobuf`, serializes the request with `xdr_serialize_generic`, then submits via `rpc_clnt_submit` on `ctx->mgmt`. The callback treats transport failure or XDR failure as `EINVAL`, logs server-side operation failure, and destroys the stack frame.

State and persistence: no persistent local state. It sends management state to glusterd and consumes temporary iobuf/iobref/frame resources.

Dependencies and integration: depends on portmap XDR, the RPC client layer, `glusterfs_ctx_t` command arguments, and the management RPC client stored in `ctx->mgmt`.

Risks: error cleanup must balance `iobref`/`iobuf` refs with ownership transferred to submit. Failure after frame creation but before submit can leak the frame because only the callback destroys it on submitted requests. The debug log mentions "register" in a signout failure path, suggesting stale wording.

Test signals: signout request serialization tests, RDMA brick-name selection tests, callback decode failure tests, and management integration tests against a portmap server.
