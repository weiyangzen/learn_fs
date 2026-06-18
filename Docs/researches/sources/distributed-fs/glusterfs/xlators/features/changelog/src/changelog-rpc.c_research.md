# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.c

## Purpose
Implements the brick-side changelog RPC server that accepts probe filter requests from libgfchangelog clients, creates reverse client records, and manages event-dispatch worker threads and cleanup.

## APIs, Types, and Functions
Public functions are `changelog_init_rpc_listener()`, `changelog_destroy_rpc_listner()`, and `changelog_cleanup_rpc_threads()`. Internal helpers include `changelog_init_rpc_threads()`, `changelog_cleanup_dispatchers()`, `changelog_rpcsvc_notify()`, `changelog_process_cleanup_event()`, `changelog_rpc_clnt_init()`, `changelog_rpc_clnt_cleanup()`, and `changelog_handle_probe()`. It defines `changelog_svc_prog` with actor `CHANGELOG_RPC_PROBE_FILTER`.

## Control Flow, State, and Persistence
Initialization sets up `priv->connections`, pending/active/wait queues, connector thread, dispatcher threads, and a Unix socket listener derived from the brick path. On probe, the server XDR-decodes `changelog_probe_req`, allocates `changelog_rpc_clnt_t` with the requested reverse socket and filter, and queues it for `changelog_ev_connector()`. RPC service notify tracks accepted listeners/transports and disconnects; when listener and client counts reach zero during cleanup, it notifies parent down, unlinks the socket, unregisters notify, destroys rxpool, and frees the rpc object.

## Dependencies and Integration
Depends on common RPC helpers, event-handle types, socket transport private data, Gluster atomics/list locks, and changelog xlator private state. Called from the main xlator initialization/reconfigure paths and feeds reverse dispatch in `changelog-ev-handle.c`.

## Risks and Test Signals
Risks include cleanup races among listener count, transport count, and client count; socket unlink timing; partial thread initialization cleanup; and XDR request strings copied by length without explicit NUL in lower layers. Test signals include probe success/failure, multiple clients with different filters, transport disconnect cleanup, brick cleanup with active reverse clients, dispatcher thread cancellation, and listener recreation on reconfigure.
