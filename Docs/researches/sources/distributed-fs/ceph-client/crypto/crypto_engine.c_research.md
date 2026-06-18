<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_engine.c -->
# sources/distributed-fs/ceph-client/crypto/crypto_engine.c

## Purpose

`crypto_engine.c` provides the framework for hardware crypto drivers that process async Crypto API requests through a software queue and a kthread request pump. It abstracts queueing, start/stop, request transfer, finalization, and engine algorithm registration helpers.

## Important APIs, Types, and Flow

`crypto_transfer_*_request_to_engine()` helpers enqueue AEAD, akcipher, ahash, KPP, and skcipher requests into the engine queue. `crypto_pump_requests()` is the core scheduler: under `queue_lock` it checks running/busy state, dequeues a request and backlog, marks `cur_req` when retry is unsupported, calls the algorithm `op.do_one_request()`, handles errors, requeues `-ENOSPC` when retry is supported, notifies backlog with `-EINPROGRESS`, and loops when retry support allows multiple outstanding hardware requests.

`crypto_finalize_*_request()` completes hardware requests, clears `cur_req` when needed, calls `crypto_request_complete()` in softirq context, and requeues pump work. `crypto_engine_start()` marks the engine running and schedules the pump. `crypto_engine_stop()` waits up to about ten seconds for queue/busy drain before returning `-EBUSY` or stopping. Allocation creates a device-managed engine, initializes queue and lock, starts a kthread worker, and optionally sets realtime scheduling.

Registration helpers validate `op.do_one_request` and register/unregister engine-backed AEAD, ahash, akcipher, KPP, and skcipher algorithms, including array rollback helpers.

## State, Dependencies, and Integration

Engine state includes queue, spinlock, kworker, pump work, running/busy flags, retry support, current request, device pointer, and private data. Dependencies are internal crypto algorithm types, kthread workers, device-managed allocation, scheduler policy, and softirq completion assumptions.

## Risks and Test Signals

Risks include request ordering on retry, stop races, lock context, callbacks outside softirq expectations, drivers failing to finalize current requests, and queue overflow. Test signals are hardware-driver selftests for enqueue/drain, `-ENOSPC` retry, stop while busy, registration rollback, realtime worker creation, and request completion ordering with backlog notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_engine.c -->
