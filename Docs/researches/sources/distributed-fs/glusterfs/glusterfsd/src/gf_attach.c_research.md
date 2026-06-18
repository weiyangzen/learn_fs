# sources/distributed-fs/glusterfs/glusterfsd/src/gf_attach.c

Purpose: Command-line helper that connects to a running glusterfsd brick-operation Unix-domain socket and sends an attach or detach request.

Important APIs and functions: Defines `gf_attach_actors` and `gf_attach_prog` for the `GD_BRICK_PROGRAM`. `my_callback()` records RPC status and wakes the main thread. `send_brick_req()` builds a `gd1_mgmt_brick_op_req`, XDR-serializes it into an iobuf, waits for RPC connection, submits `GLUSTERD_BRICK_ATTACH` or `GLUSTERD_BRICK_TERMINATE`, then waits for callback completion. `sanitize_args()` validates socket/volfile/brick-path types. `main()` parses `-d`, initializes a minimal `glfs_t`, builds RPC transport options, starts `rpc_clnt`, and calls `send_brick_req()`.

Control flow: Attach mode is `gf_attach uds_path volfile_path`; detach mode is `gf_attach -d uds_path brick_path`. The tool validates arguments before creating RPC state. It waits up to 60 seconds for connection and 120 seconds for reply. Success prints `OK`; RPC errors or timeouts return `EXIT_FAILURE`.

State and persistence: Uses global `done` and `rpc_status` guarded by a mutex/condition variable. It does not persist files; it only reads path metadata and sends one RPC.

Dependencies and integration: Depends on libgfapi initialization for a Gluster context, RPC client APIs, iobuf/iobref memory, XDR generated types from glusterd, and Unix socket transport options. It integrates with handlers in `glusterfsd-mgmt.c`.

Risks: Global completion state means the process is single-request only. Some early failure paths return without unrefing all allocated objects. The wait loops rely on condition variables and can block until timeout if notification is missed. `sanitize_args()` switches on full `argc`, so option parsing assumptions are coupled to exact CLI forms.

Test signals: Useful tests would cover invalid path type rejection, attach/detach request serialization against a fake RPC server, connection timeout, reply timeout, and server-side error propagation. No direct tests are present in this subset.
