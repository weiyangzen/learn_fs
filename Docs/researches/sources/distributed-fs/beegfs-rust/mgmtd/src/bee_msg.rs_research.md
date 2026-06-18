<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg.rs

**Purpose:** Central BeeMsg dispatcher for the management service's classic BeeGFS protocol endpoint.

**Important APIs/types/functions:** Declares handler traits `HandleNoResponse` and `HandleWithResponse`, `PreShutdownError`, public `dispatch_request`, `handle_unspecified_msg`, and `fail_on_pre_shutdown`. Imports and registers handler modules for ack/auth, nodes, targets, buddy groups, storage pools, capacity pools, quota, and miscellaneous messages.

**Control flow:** `dispatch_request` matches `req.header().msg_id()` through a macro. For matching messages it deserializes the body, logs it, calls the message's `handle`, and either sends the typed response or logs no-response completion. Response handlers convert `PreShutdownError` into `GenericResponse { code: TRY_AGAIN }`; other errors log and send the handler's `error_response`. Unknown messages receive a generic TRY_AGAIN "Unhandled msg".

**State and persistence behavior:** Stores no state; delegates to handlers via `App`. Its error policy affects wire-visible behavior during shutdown and handler failures.

**Dependencies and integration points:** Integrates `shared::conn::msg_dispatch::Request`, `shared::bee_msg` message IDs, serialization traits, SQLite helpers, app runtime, and all submodule handlers.

**Risks:** Adding a new handler requires both trait impl and macro registration. Non-response handler errors are logged but not returned to peers. Default error responses can hide failure details from callers. Pre-shutdown conversion only happens for response-bearing messages.

**Test signals:** Dispatch tests should cover correct message routing, response/no-response behavior, unknown messages, deserialization context, generic pre-shutdown TRY_AGAIN, and handler error fallback responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg.rs -->
