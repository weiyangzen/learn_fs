## sources/distributed-fs/ceph/src/rgw/rgw_main.cc

Purpose: executable entry point for the `radosgw` daemon.

Important APIs/functions: `usage()` prints daemon options; `C_InitTimeout` fails startup after `rgw_init_timeout`; `godown_alarm()` exits on alarm; `main()` performs global initialization, service setup, signal registration, frontend startup, wait-for-shutdown, and orderly teardown.

Control flow: `main()` redirects stderr to stdout for FCGI compatibility, sets default config values, parses usage, calls `rgw_global_init()` with deferred privilege drop, constructs `rgw::AppMain`, initializes keyring/frontends/NUMA, daemonizes if configured, starts an initialization timer, finishes common init, registers async signal handlers, initializes storage and subsystems, starts frontends, waits for shutdown, then unregisters signal handlers and calls `AppMain::shutdown()`.

State and persistence: persistent service state is owned by `AppMain` and SAL/RADOS subsystems. This file controls process-level signal and timer state.

Dependencies/integration: integrates global Ceph init, Linux keyring secret handling, RGW signals, storage, ops logging, Lua, KMS cache, dedup when compiled, and frontend service startup.

Risks and test signals: startup failure paths must cancel/shutdown the init timer. Stderr redirection affects diagnostics. Signal registration order matters for clean shutdown. Tests are mostly integration/system-level: invalid storage config, daemonize path, init timeout, frontend init failure, and graceful SIGTERM/SIGINT shutdown.
