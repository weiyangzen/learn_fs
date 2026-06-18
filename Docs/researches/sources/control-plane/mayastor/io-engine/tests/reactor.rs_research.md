# sources/control-plane/mayastor/io-engine/tests/reactor.rs

Purpose: validates reactor startup/shutdown state, CPU pinning of reactor futures, and unaffinitized thread placement outside the reactor CPU mask.

Important APIs/types/functions: `MayastorEnvironment`, `MayastorCliArgs`, `Reactors`, `ReactorState`, `Cores`, `Mthread`, `mayastor_env_stop`, and `AtomicUsize`.

Control flow: `reactor_start_stop` starts a two-core Mayastor environment, checks every reactor is `Delayed` or `Running`, sends a future to each reactor that asserts `Cores::current()` equals `sched_getcpu`, and polls the master until a wait counter reaches zero. It then spawns unaffinitized OS threads, waits, stops the environment, and joins the threads.

State and persistence behavior: no persistence. State is reactor state, current core identity, and thread affinity behavior.

Dependencies and integration points: SPDK reactor environment, Linux `sched_getcpu`, io-engine `Mthread`, and reactor future scheduling.

Risks: requires at least two CPUs and assumes unaffinitized threads run outside the reactor mask; uses a `static mut` wait counter wrapper.

Test signals: allowed reactor states, correct CPU pinning for all reactor futures, wait counter completion, unaffinitized thread CPU assertions, and clean shutdown.
