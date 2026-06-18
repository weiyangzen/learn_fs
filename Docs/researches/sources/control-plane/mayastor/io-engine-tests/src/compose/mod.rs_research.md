<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/mod.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/compose/mod.rs

Purpose: Provides `MayastorTest`, an in-process io-engine test harness, while re-exporting the external `composer` crate for container-based integration tests.

Important APIs/types: `MayastorTest<'a>` owns CLI args, optional log level, a reactor handle, and a thread handle. Constructors initialize logging/CPS, create a bounded channel, spawn a named `ms-test` thread, initialize `MayastorEnvironment`, set the primary mthread current, and send the reactor back. `spawn()` schedules futures on the reactor and awaits their result. `start_grpc()` initializes resource locks and runs the gRPC server. `Drop` sends `mayastor_env_stop(0)` and joins the thread.

Control flow: tests create the harness, then call `spawn()` to execute io-engine futures on the correct reactor thread. Shutdown is asynchronous but triggered synchronously on drop.

State and dependencies: owns global Mayastor runtime, logger, CPS init, resource lock manager, and `/var/run/dpdk` assumptions through callers.

Risks and test signals: global runtime state means multiple harnesses can interfere if not serialized. Drop unwraps join unless panicking. Healthy tests show reactor startup, future completion through `spawn`, and clean environment stop.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/compose/mod.rs -->
