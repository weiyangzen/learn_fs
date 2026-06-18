# sources/distributed-fs/ceph-client/drivers/dma-buf/st-dma-fence.c

Purpose: selftests core dma-fence behavior: signaling, callbacks, status/error reporting, waits/timeouts, stub fences, and callback races.

Important APIs/types/functions: defines a simple mock fence ops table, `mock_fence()`, `struct simple_cb`, timer-backed wait helper, race-thread structures, and top-level `dma_fence()`.

Control flow: subtests create unsignaled mock fences, enable software signaling, and check one behavior at a time. Signaling verifies initial unsignaled state, idempotent signal, signaled flags, and ops clearing after signal. Callback tests cover add-before-signal, add-after-signal failure, removal before signal, and removal after callback execution. Status/error tests ensure errors are visible only after signal. Wait tests validate zero-timeout results and timer-driven completion. Stub tests check many references to the global signaled stub. Race tests run two kthreads exchanging RCU-published fences while signaling before or after callback attachment to stress `dma_fence_get_rcu_safe()` and callback completion ordering.

State and persistence behavior: all fences are temporary per subtest. Race test uses RCU pointer array state only for the duration of the subtest. The global stub fence state is owned by `dma-fence.c`.

Dependencies and integration points: depends on dma-fence core, kthreads, timers, RCU, scheduler waits, spinlocks, and the selftest harness.

Risks and test signals: race test duration is short and probabilistic, so it is a smoke test rather than exhaustive proof. Passing signals include callback visibility under memory barriers, no late callback invocation after failed add/removal, correct wait return values, no unsignaled stub fences, and no race-thread errors.
