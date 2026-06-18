# sources/distributed-fs/ceph/src/osd/ECSwitch.h

Purpose: `ECSwitch.h` defines a temporary PGBackend wrapper that selects between legacy EC (`ECLegacy::ECBackendL`) and optimized EC (`ECBackend`) based on the pool's `allows_ecoptimizations()` flag.

Important APIs and types: `ECSwitch` inherits `PGBackend` and owns both backend implementations. It forwards recovery, messaging, transaction submission, reads, scrubbing, size conversion, encode/decode helpers, attr handling, and OMAP methods to the selected backend. Nested `ECRecPred` and `ECReadPred` delegate recoverability/readability predicates to the selected backend.

Control flow: most methods branch on `is_optimized()`. Some transition-sensitive methods use `is_optimized_unchecked()` to tolerate pool-flag changes around `on_change`. `on_change` forwards to the currently active backend and then updates `is_optimized_actual`, permitting a one-way transition into optimized mode while asserting optimized pools remain optimized afterward.

State and persistence: `ECSwitch` itself persists no object state. It routes calls that may mutate durable state, including `submit_transaction`, recovery operations, ObjectStore OMAP reads, and journal cleanup. It also controls whether legacy hinfo metadata is required.

Dependencies and integration: includes `PGBackend.h`, `ECBackendL.h`, and `ECBackend.h`. It is constructed with PG listener, collection handle, ObjectStore, erasure-code plugin, stripe width, and optimized extent-cache LRU.

Risks: both backends are alive, but only one should be authoritative for a pool state. Forwarding gaps can produce behavior differences. Methods unsupported by legacy abort or return `-EOPNOTSUPP`; callers must handle this. OMAP journal methods assert optimized mode, so calling them for legacy pools is fatal.

Test signals: tests should cover pool optimization transitions, each forwarded read/write/recovery path in both modes, legacy unsupported sync-read behavior, hinfo filtering, optimized OMAP journal hooks, and predicate behavior before/after `on_change`.
