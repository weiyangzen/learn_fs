<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/app/test.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/app/test.rs

**Purpose:** Test implementation of `App` for BeeMsg handler and management-unit tests.

**Important APIs/types/functions:** `TestApp` contains test `Connections`, `StaticInfo`, and `TestData` guarded by `Mutex`. `TestData` records notifications and optional boxed request handler. Helpers include `new`, `with_config`, `set_request_handler`, `has_sent_notification`, `sent_notifications`, and macro `assert_eq_db!`. Re-exports `TestRequest`.

**Control flow:** `with_config` sets up a test database with seed data, configures localhost NICs, and installs a hashed auth secret. Trait transaction methods forward to test SQLite connections. `request` invokes a user-provided dynamic handler and downcasts the response or returns default. `send_notifications` records message IDs and node type recipients.

**State and persistence behavior:** Persists test database changes in an in-memory/temp test database and records notifications in process memory. Run-state and address replacement are no-ops; license checks return permissive dummy data.

**Dependencies and integration points:** Used by handler tests under `bee_msg/*`. Depends on DB test setup, shared NIC query, auth secret hashing, and BeeMsg `MsgId`.

**Risks:** The mock is intentionally incomplete: pre-shutdown is always false, license checks always succeed, request responses default unless configured, and network address replacement is ignored. Tests relying on those behaviors may miss runtime edge cases.

**Test signals:** Existing async handler tests compile and pass; add mock behavior when new handlers require pre-shutdown, licensing failure, or network side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/app/test.rs -->
