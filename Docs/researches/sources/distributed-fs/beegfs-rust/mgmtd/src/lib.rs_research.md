<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/lib.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/lib.rs

Purpose: library entry point for the BeeGFS management service. It wires static startup info, SQLite, BeeMsg networking, connection pool, timers, gRPC, license loading, and graceful shutdown control.

Important APIs/types/functions: `StaticInfo` holds immutable runtime config, auth secret, local NICs, and IPv6 choice. `start()` initializes the daemon and returns `RunControl`. `migrate_db_schema()` backs up and migrates SQLite. `RunControl::wait_for_shutdown()` drives pre-shutdown, client state-drain waiting, and final shutdown. `version_str()` exposes compile-time `VERSION`.

Control flow: startup leaks `StaticInfo` for `'static` sharing, binds UDP, builds outgoing connection pool, opens/migrates DB, refreshes management node/NIC rows, loads/verifies license and persists first trial serial, seeds connection-pool addresses from DB, starts TCP/UDP BeeMsg listeners, timers, and gRPC.

State and persistence: opens and migrates the SQLite DB, updates management node last contact/NICs, persists first trial serial, and reads node addresses into memory. Shutdown enters pre-shutdown before notifying clients to pull target state when buddy groups and clients exist.

Dependencies and integration points: central integration point for `app`, `db`, `license`, shared BeeMsg incoming/outgoing networking, run-state, timers, gRPC, and config.

Risks: `Box::leak` intentionally makes static info process-lifetime. License failures leave features unavailable but do not abort startup. Shutdown state-drain depends on clients reporting both meta and storage pulls before timeout or second signal.

Test signals: no direct tests here in this subset. Integration tests should cover migration, startup with/without license, auth secret propagation, connection-pool seeding, and shutdown client wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/lib.rs -->
