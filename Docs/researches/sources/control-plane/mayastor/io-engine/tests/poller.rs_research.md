# sources/control-plane/mayastor/io-engine/tests/poller.rs

Purpose: tests SPDK poller lifecycle: drop before polling, repeated invocation, pause/resume/stop, callback-local mutable state, and execution on a non-master core.

Important APIs/types/functions: `PollerBuilder`, `Reactors`, `MayastorEnvironment`, `MayastorCliArgs`, `Cores`, `AtomicCell`, `parking_lot::Mutex`, and helper `test_fn`.

Control flow: the test initializes a two-core environment, builds and drops a poller before polling, verifies no callback ran, then builds another poller and polls the master 64 times. It pauses and resumes while checking the global count, stops the poller and checks no further increments, creates a poller with captured local state, and finally creates a data-bearing poller on core 1 whose callback asserts `Cores::current() == 1`.

State and persistence behavior: no persistence. State is poller registration, pause/stop flags, callback data, global count, and core affinity.

Dependencies and integration points: `spdk_rs::PollerBuilder`, io-engine reactor abstraction, and core affinity.

Risks: the core-1 poller depends on a short sleep being enough to run at least once.

Test signals: exact count values after poll batches, no increments while paused/stopped, core-1 callback count greater than zero, and clean environment stop.
