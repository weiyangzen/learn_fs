# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.c

## Purpose
Provides shared RPC client/server utilities used by both the brick-side changelog xlator and libgfchangelog.

## APIs, Types, and Functions
Client helpers are `changelog_rpc_poller()`, `changelog_rpc_client_init()`, `changelog_rpc_sumbit_req()`, and `changelog_invoke_rpc()`. Server helpers are `__changelog_rpc_serialize_reply()`, `changelog_rpc_sumbit_reply()`, `changelog_rpc_server_init()`, and `changelog_rpc_server_destroy()`.

## Control Flow, State, and Persistence
Client initialization builds Unix transport options, creates an RPC client, registers notify callbacks, and starts it. Request submission optionally XDR-serializes a request into an iobuf/iobref and submits it with extra payload vectors. `changelog_invoke_rpc()` creates a call frame, invokes the procedure-table function, and destroys the stack. Server initialization builds Unix listener options, initializes `rpcsvc`, registers notify, creates listeners, and registers each supplied program. Reply submission serializes an XDR reply and sends optional payloads. No persistent files are written except Unix socket files created by RPC transport setup and removed by callers/destroy paths.

## Dependencies and Integration
Depends on Gluster RPC client/server APIs, Unix transport option builders, iobuf/iobref pools, XDR helpers, and message IDs. It is included by `changelog-rpc.c`, `changelog-ev-handle.c`, `gf-changelog-rpc.c`, and `gf-changelog-reborp.c`.

## Risks and Test Signals
Risks include typo-preserved API name `sumbit`, iobuf/iobref ownership mistakes, freeing `rpcsvc_t` differently during brick multiplex cleanup, missing socket unlink in common destroy, and call-frame lifecycle assumptions. Test signals include request/reply serialization failures, client notify registration failure, listener/program registration failure, payload plus XDR requests, and cleanup under active transport disconnect.
