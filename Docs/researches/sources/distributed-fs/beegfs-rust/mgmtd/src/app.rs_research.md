<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/app.rs -->
## sources/distributed-fs/beegfs-rust/mgmtd/src/app.rs

**Purpose:** Defines the internal `App` trait abstraction used by management tasks and BeeMsg handlers to access config, database transactions, BeeMsg communication, run state, and licensing without depending on concrete runtime handles.

**Important APIs/types/functions:** Exports `RuntimeApp`; conditionally exports `test`. `App` requires `Debug + Clone + Send + 'static` and methods `static_info`, `read_tx`, `write_tx`, `write_tx_no_sync`, `db_conn`, `request`, `send_notifications`, `replace_node_addrs`, `is_pre_shutdown`, `notify_client_pulled_state`, `load_and_verify_license_cert`, `get_license_cert_data`, `get_licensed_machines`, and `verify_licensed_feature`.

**Control flow:** Handler modules accept `&impl App`, run database closures asynchronously, send messages/notifications through trait methods, and check shutdown/license state through the same interface.

**State and persistence behavior:** The trait mediates access to SQLite transactions and connection state but stores no data itself. It separates read, synced write, no-sync write, and raw connection access.

**Dependencies and integration points:** Integrates `StaticInfo`, `LicenseVerifier`, protobuf license result types, BeeMsg serialization traits, rusqlite, shared node IDs/types, and runtime/test implementations.

**Risks:** The trait is broad; changes ripple through runtime and test mocks. `write_tx_no_sync` is intentionally weaker durability and must be used only where acceptable. Generic async trait methods rely on Rust's async-in-trait support and can complicate trait object use.

**Test signals:** Compile all handler modules against both `RuntimeApp` and `TestApp`; unit tests using `crate::app::test` validate trait completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/app.rs -->
