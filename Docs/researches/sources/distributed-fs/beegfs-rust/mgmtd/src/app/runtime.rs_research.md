<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/app/runtime.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/app/runtime.rs

**Purpose:** Concrete runtime implementation of `App` and BeeMsg request dispatch for the management service.

**Important APIs/types/functions:** `RuntimeApp(Arc<InnerAppHandles>)`, `InnerAppHandles` containing connection pool, SQLite connections, license verifier, static info, weak run-state handle, and shutdown client notification sender. Implements `Deref`, `DispatchRequest`, and `App`.

**Control flow:** `RuntimeApp::new` bundles handles into an `Arc`. `DispatchRequest::dispatch_request` delegates to `bee_msg::dispatch_request`. Transaction methods forward to `sqlite::Connections`. `request` forwards to outgoing BeeMsg `Pool`. `send_notifications` fetches nodes by type and broadcasts datagrams; per-type errors are logged and do not abort other notifications. `notify_client_pulled_state` sends an async mpsc notification only during pre-shutdown.

**State and persistence behavior:** Holds shared handles to connection pools and DB connections. Database operations persist through SQLite transactions. Network address updates mutate the outgoing connection pool's node address store.

**Dependencies and integration points:** Central integration point for BeeMsg dispatch, SQLite connection executor, run-state shutdown coordination, licensing, and outgoing notification transport.

**Risks:** Notification sending is best-effort; callers cannot observe failures. Spawning a task for shutdown notifications can drop errors silently. `Deref` exposes inner handles broadly, which is convenient but weakens encapsulation.

**Test signals:** Integration tests should verify notifications for registered node types, request/response through the connection pool, pre-shutdown client pull notification, and license verification delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/app/runtime.rs -->
