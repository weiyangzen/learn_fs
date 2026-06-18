<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_priv_hash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_priv_hash.c

## Purpose
This test validates the `PR_FUTEX_HASH` prctl interface for private futex hash bucket sizing, automatic initialization/scaling, manual settings, and global-hash fallback.

## Important APIs, Types, And Functions
Important helpers are `futex_hash_slots_set()`, `futex_hash_slots_get()`, `futex_hash_slots_set_verify()`, `futex_hash_slots_set_must_fail()`, `thread_return_fn()`, `thread_lock_fn()`, `create_max_threads()`, `join_max_threads()`, and `futex_dummy_op()`. It uses `pthread_mutex` with `PTHREAD_PRIO_INHERIT` to force futex operations.

## Control Flow
The test observes initial slot count, creates a thread to trigger private hash initialization, optionally checks automatic growth on systems with more than 16 CPUs, verifies accepted manual power-of-two slot counts, rejects invalid values, confirms manual settings disable auto-resize, then requests global hash with slot count 0 and verifies later private settings fail.

## State And Persistence
It changes process-level futex hash configuration via `prctl()`, creates many threads, and uses global counter/lock/barrier state. The prctl state persists for the process.

## Dependencies And Integration Points
It depends on kernel support for `PR_FUTEX_HASH`, pthread PI mutexes, RCU-delayed private hash replacement behavior, and kselftest harness.

## Risks
Auto-scaling is timing-sensitive; the retry loop uses timed mutex operations to wait for RCU grace periods. Systems with <=16 CPUs skip that part. Unsupported prctl will fail early.

## Test Signals
Pass signals include positive slot count after first thread, optional increased slots on large systems, exact get-after-set values, rejection of bad sizes, stable manual size after more threads, and permanent global hash state after setting 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/futex/functional/futex_priv_hash.c -->
