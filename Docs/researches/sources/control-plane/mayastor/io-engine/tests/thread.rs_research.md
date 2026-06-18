# sources/control-plane/mayastor/io-engine/tests/thread.rs

Purpose: concurrency/runtime test verifying transitions between Mayastor reactor threads, Tokio runtime tasks, blocking tasks, and primary reactor dispatch.

Important APIs/types/functions: `mayastor_to_runtime`, `runtime_to_mayastor`, `running_on_thread`, and `thread_tokio` use `Cores`, `Mthread`, `Reactor::spawn_at_primary`, `runtime::spawn`, `runtime::spawn_blocking`, `bdev_create`, and `UntypedBdev::share_nvmf`.

Control flow: a Mayastor instance starts with reactor mask `0x3`. A malloc bdev is created on the primary reactor. A future sent from Mayastor asserts it is on the first core with an SPDK thread, spawns onto Tokio, asserts it has no Mayastor core/thread, sleeps, then dispatches back to the primary reactor to share the bdev. A blocking task asserts it also has no Mayastor core/thread.

State/persistence: transient bdev `malloc0` and runtime thread-local core/thread state.

Dependencies/integration: validates Mayastor runtime helpers, Tokio scheduling, SPDK thread affinity, and bdev sharing from cross-runtime callbacks.

Risks: timing is simple but thread-local assertions are brittle if runtime identity semantics change. The test assumes `malloc0` is created before the reactor callback uses it.

Test signals: passing test shows safe cross-runtime dispatch and correct absence/presence of SPDK thread context in each execution domain.
