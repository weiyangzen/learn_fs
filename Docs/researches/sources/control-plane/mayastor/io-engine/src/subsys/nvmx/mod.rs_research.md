# sources/control-plane/mayastor/io-engine/src/subsys/nvmx/mod.rs

Purpose: registers a Mayastor SPDK subsystem that creates per-reactor admin-queue polling threads for NVMx controllers and exposes lookup helpers for those threads.

Important APIs/types/functions: `NvmxSubsystem` owns a leaked/raw `spdk_subsystem`. `ADMINQ_POLL_THREADS` is a `OnceCell<HashMap<u32, u64>>` mapping reactor core IDs to `spdk_rs::Thread` IDs. `init` creates one `Thread` named `nvmx_poll_adminq_{core}` per reactor, stores the map, and advances SPDK init. `adminq_thread_id` and `adminq_thread` expose lookups. `fini` only advances SPDK fini. `register` calls `spdk_add_subsystem`.

Control flow: SPDK calls `init`; Mayastor iterates reactors, allocates adminq threads on the corresponding core, stores thread IDs once, then calls `spdk_subsystem_init_next(0)`. Callers can later resolve a core to a thread ID or `Thread` object. Fini logs and immediately continues.

State and persistence: state is process-local in `ADMINQ_POLL_THREADS`. The threads are not explicitly deleted in `fini`, as noted by the source comment. No persistent state.

Dependencies and integration points: uses SPDK subsystem registration, `crate::core::Reactors`, and `spdk_rs::Thread`. Consumers in NVMx controller code can use `adminq_thread` to schedule admin queue polling on a core-affine thread.

Risks and edge cases: `Thread::new(...).expect(...)` panics if allocation fails. Calling `adminq_thread_id` before init initializes the `OnceCell` to an empty map, which would prevent the real init map from being stored later; normal SPDK ordering should avoid this, but it is a subtle footgun. Fini does not reclaim threads.

Test signals: no direct tests in this subset; coverage is indirect through any NVMx controller paths not visible here. The absence of direct assertions means init ordering and early lookup behavior are important residual risks.
