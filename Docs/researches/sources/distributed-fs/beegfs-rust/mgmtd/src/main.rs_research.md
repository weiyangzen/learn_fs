<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/main.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/main.rs

Purpose: binary entry point for the management daemon. It handles process setup, configuration, logging, initialization/import mode, auth/NIC discovery, Tokio runtime construction, license library loading, startup, systemd readiness, shutdown signals, and panic logging.

Important APIs/types/functions: `main()` maps errors to exit code 1. `inner_main()` performs runtime setup. `init_db()` creates a new DB in memory, migrates/seeds/imports, then atomically backs it up to a new on-disk file. `panic_handler()` logs backtraces. `wait_for_shutdown_signal()` waits for SIGINT/SIGTERM.

Control flow: config is parsed first, optional daemonization happens before logger init, then init/import/upgrade modes can exit early. Normal startup requires existing DB, reads auth secret unless disabled, queries NICs, creates Tokio runtime with configured blocking threads, loads license library, starts `mgmtd::start()`, notifies systemd, and waits for shutdown.

State and persistence: creates DB files only in init/import mode, using `File::create_new()` and cleanup on backup failure. Reads auth file and license library/cert paths. Writes daemon PID file through `daemonize`.

Dependencies and integration points: consumes `config`, `db`, `license`, shared NIC/journald/auth helpers, Tokio Unix signals, systemd notification, and library `start()`.

Risks: daemonization before logging can obscure failures except daemonization itself. License library loading is unsafe by design. Init/import writes to disk only after in-memory success, reducing partial DB risk. Unix signal code is platform-specific.

Test signals: no direct tests. Integration tests should cover init DB with/without v7 import, existing-file failure, auth file errors, logger modes, and upgrade early exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/main.rs -->
