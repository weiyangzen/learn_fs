<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cryptd.c -->
# sources/distributed-fs/ceph-client/crypto/cryptd.c

## Purpose

`cryptd.c` implements the software async crypto daemon template `cryptd(...)`. It wraps synchronous skcipher, shash, and AEAD algorithms so callers can use async request semantics backed by per-CPU workqueues.

## Important APIs, Types, and Flow

The module creates a per-CPU `cryptd_queue` of `crypto_queue` objects protected by local BH locks and serviced by a per-CPU workqueue. `cryptd_enqueue_request()` enqueues on the current CPU, schedules work, and increments a transform refcount when applicable. `cryptd_queue_worker()` dequeues one request, completes backlog with `-EINPROGRESS`, completes the active request with status 0 to invoke the wrapper continuation, and reschedules if more requests remain.

Template creation dispatches by requested type to `cryptd_create_skcipher()`, `cryptd_create_hash()`, or `cryptd_create_aead()`. Each creates an instance named like the child but with driver `cryptd(child-driver)`, priority child + 50, async flag, child spawn, and wrapper callbacks. Runtime callbacks save the original completion, enqueue the parent request, prepare an embedded child request in worker context, run the synchronous child operation with MAY_SLEEP, then complete the original request. Hash wrappers adapt shash operations to ahash requests and support export/import.

Public helpers `cryptd_alloc_aead()`, `cryptd_aead_child()`, `cryptd_aead_queued()`, and `cryptd_free_aead()` manage refcounted AEAD wrappers.

## State, Dependencies, and Integration

Persistent module state is `cryptd_wq` and the global per-CPU queue. Instance state stores child spawns and queue pointer. Tfm state stores child transforms and refcounts. Dependencies include crypto template internals, workqueues, local locks, refcounts, and softirq-safe completion behavior.

## Risks and Test Signals

Risks include queue-depth `-ENOSPC`, CPU-local locking, transform free while queued work remains, callback restoration, handling `-EINPROGRESS`, and hash descriptor export/import state. Test signals are async crypto selftests under load, backlog notifications, module unload with empty queues, refcounted AEAD allocation/free, and equivalence with direct synchronous child algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cryptd.c -->
