<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine.rs

### Purpose
`io-engine.rs` is the main io-engine data-plane binary. It initializes logging, environment, SPDK reactors, hugepage checks, feature toggles, persistent store, gRPC serving, registration, diagnostics, and process-level safety settings.

### Important APIs, Types, And Functions
Important functions are `start_tokio_runtime`, `hugepage_get_nr`, `hugepage_check`, and `main`. The `print_feature!` macro logs compile-time feature status. `PAGES_NEEDED` defines the hugepage threshold. The binary invokes `io_engine::CPS_INIT!()`.

### Control Flow
`main` parses `MayastorCliArgs`, initializes logging, configures `PR_SET_IO_FLUSHER`, optionally enables coredumps, handles diagnostics commands early, checks hugepages, logs io_uring and NVMe multipath support, initializes `MayastorEnvironment`, starts the Tokio side runtime, marks reactors running, and polls the primary reactor. `start_tokio_runtime` applies env-driven feature flags for partial rebuild, reset, LVM, snapshot rebuild, channel debug, RDMA, diskpool encryption, and blobstore unmap; initializes resource locks; optionally connects persistent store; spawns device and reactor monitors; runs the gRPC server; and optionally runs registration. A joined future failure raises `SIGUSR1`.

### State, Persistence, And Dependencies
The binary controls process-wide state: environment variables, global atomic feature flags, SPDK blobstore behavior, resource lock manager, persistent store connection, gRPC server state, registration, reactor state, and event generation. Dependencies include `io_engine` core modules, `events_api`, `futures`, `sysfs`, `signal_hook`, `spdk_rs`, logger, persistent store, and version info.

### Risks And Test Signals
Hugepage insufficiency exits only in non-debug builds. Some feature switches are environment variables, making behavior dependent on deployment environment. `ms.event(Start).generate()` occurs after reactor polling/fini, which is worth verifying against expected lifecycle semantics. Tests and validation should cover CLI parsing, diagnostics early exit, hugepage paths absent/present, env flag effects, persistent store retry settings, gRPC startup failures, registration failures, and internal abort exit.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine.rs -->
