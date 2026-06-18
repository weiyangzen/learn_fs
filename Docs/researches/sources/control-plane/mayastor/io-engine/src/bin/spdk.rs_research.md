<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/spdk.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/spdk.rs

### Purpose
`spdk.rs` is a minimal wrapper around `spdk_app_start` for testing SPDK with a given configuration when the full io-engine stack is unnecessary.

### Important APIs, Types, And Functions
The binary prepares C argv values, initializes `spdk_app_opts`, calls `spdk_app_parse_args`, sets app name and shutdown callback, and starts the SPDK app with `app_start_cb`. `spdk_shutdown_cb` unregisters optional delay support and stops the SPDK app.

### Control Flow
`main` converts Rust args to `CString`, builds a null-terminated C argv array, initializes SPDK options, lets SPDK parse standard app args, installs shutdown callback, starts the app, finalizes SPDK, and returns an I/O error on nonzero status. `app_start_cb` registers artificial delay support when `MAYASTOR_DELAY` is set.

### State, Persistence, And Dependencies
The binary owns a standalone SPDK app lifecycle and any SPDK resources configured by arguments. It depends on `spdk_rs::libspdk`, libc-compatible argument handling, and the repository `delay` module. It stores no repository state.

### Risks And Test Signals
The app name CString is leaked into SPDK with `into_raw`, appropriate for process lifetime but notable. Argument parsing and callbacks are unsafe FFI boundaries. Tests should cover SPDK argument parsing failures, successful start/stop, `MAYASTOR_DELAY` behavior, shutdown callback cleanup, and nonzero SPDK return codes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/spdk.rs -->
