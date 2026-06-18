<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test_task.rs -->
# sources/control-plane/mayastor/io-engine-tests/src/test_task.rs

Purpose: Serializes special SPDK test tasks onto one designated OS thread for tests using the `spdk_test` macro.

Important APIs/types: `TestTask` packages a oneshot sender and boxed closure. `MAIN_THREAD` is a `OnceCell<Sender<TestTask>>`. `run_single_thread_test_task(f)` initializes a bounded channel and background thread on first use, sends the closure, and awaits the oneshot completion. `main_loop()` receives tasks forever, runs the closure, and signals completion.

Control flow: callers remain in async Tokio tests while the actual closure runs on the dedicated thread. Channel capacity one serializes submissions.

State and dependencies: owns a process-global background thread for the lifetime of the process. Depends on crossbeam channels and Tokio oneshot.

Risks and test signals: panics inside task closures can terminate the background thread and break later tests. There is no shutdown path. Successful annotated tests prove channel send, closure execution, and oneshot completion.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/src/test_task.rs -->
