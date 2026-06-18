# sources/distributed-fs/ceph-client/include/crypto/engine.h

Purpose: crypto hardware engine queue/registration API for offloaded AEAD, hash, akcipher, KPP, and skcipher algorithms.

Important APIs/types/functions: `struct crypto_engine_op`, engine algorithm wrapper structs for each algorithm class, transfer helpers, finalize helpers, start/stop/allocation/exit functions, and register/unregister helpers for single and array algorithm providers.

Control flow: providers wrap algorithm callbacks with a `do_one_request` engine operation, register engine algorithms, transfer incoming crypto requests to the engine queue, and call finalize helpers when hardware/software processing completes.

State and persistence: opaque `struct crypto_engine` owns queues, worker state, retry behavior, and device association in implementation. Wrapper alg structs persist registration metadata and engine operation callbacks.

Dependencies and integration points: depends on AEAD, akcipher, hash, KPP, skcipher APIs, and device model. Used by hardware accelerator drivers.

Risks: finalize must be called exactly once per transferred request. Start/stop and unregister ordering must drain or reject queued work safely. Request type mismatches can corrupt container casts.

Test signals: hardware-driver selftests, crypto manager vectors through engine providers, queue full/retry tests, unregister-with-inflight tests, and runtime PM/error-path tests.
