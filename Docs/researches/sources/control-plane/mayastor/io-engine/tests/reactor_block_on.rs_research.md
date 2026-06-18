# sources/control-plane/mayastor/io-engine/tests/reactor_block_on.rs

Purpose: regression test for nested `Reactor::block_on` and scheduling a future from inside a blocked reactor context.

Important APIs/types/functions: `MayastorEnvironment`, `MayastorCliArgs`, `Reactor::block_on`, `Reactors::master().send_future`, `mayastor_env_stop`, and `AtomicCell`.

Control flow: the test initializes an environment, enters an outer `Reactor::block_on`, confirms the global counter is zero, sets it to one, queues a master future expecting the counter to be two, then enters a nested `Reactor::block_on` that observes one and sets two. After the outer block, the environment stops and the final count is checked.

State and persistence behavior: no persistence. State is the global counter and ordering between nested blocking and queued future execution.

Dependencies and integration points: in-process SPDK environment and reactor executor.

Risks: narrow regression; scheduling order changes would intentionally fail it.

Test signals: nested block completes without deadlock, queued future observes the nested update, and final count is two.
