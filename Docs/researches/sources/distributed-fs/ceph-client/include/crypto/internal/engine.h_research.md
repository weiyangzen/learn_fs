# sources/distributed-fs/ceph-client/include/crypto/internal/engine.h

Purpose: declares internal helpers for crypto engine based drivers that queue asynchronous requests onto hardware or threaded engines.

Important APIs, types, and flow: `crypto_engine_alloc_init_and_set()` creates and initializes an engine with a request queue length, optional retry support, processor callback, prepare/unprepare callbacks, per-algorithm private pointer, and feature flags. `crypto_engine_start()` and `crypto_engine_stop()` control request processing.

State and persistence: engine state is runtime queue/worker/device state owned by the implementation returned from allocation. No persistent state is represented in this header.

Dependencies and integration: depends on public crypto engine types and is used by hardware crypto drivers to integrate with the common crypto request queue and completion model.

Risks and test signals: risks include start/stop races, retry livelock, lost completions, and prepare/unprepare imbalance around hardware DMA setup. Signals include hardware-driver crypto self-tests, queue-depth stress, module removal while requests are pending, suspend/resume, and fault injection in prepare/process paths.
