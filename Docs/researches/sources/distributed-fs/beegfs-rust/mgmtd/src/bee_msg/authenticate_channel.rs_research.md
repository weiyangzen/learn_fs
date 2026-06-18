<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/authenticate_channel.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/authenticate_channel.rs

**Purpose:** Authenticates classic BeeMsg connections by comparing the peer-provided secret with the configured management secret.

**Important APIs/types/functions:** Implements `HandleNoResponse` for `AuthenticateChannel`; uses `app.static_info().auth_secret` and `req.authenticate_connection()`.

**Control flow:** If authentication is configured and the received hash matches, marks the request connection authenticated. Wrong secrets are logged as errors. If auth is disabled, attempts are logged at debug and ignored.

**State and persistence behavior:** Mutates connection/request authentication state via the `Request` object. No database persistence.

**Dependencies and integration points:** Relies on `StaticInfo` auth secret and `shared::conn::msg_dispatch::Request`. The test verifies a correct secret flips the `TestRequest` authentication flag.

**Risks:** Wrong authentication attempts return success at the handler level and depend on connection-layer enforcement elsewhere. Logging peer addresses for failed auth is useful but can be noisy under attack.

**Test signals:** Existing `authenticate_channel` test covers correct secret. Additional tests should cover wrong secret and auth-disabled behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/bee_msg/authenticate_channel.rs -->
