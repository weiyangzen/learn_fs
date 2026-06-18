# sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer_kunit_test.c

## Purpose
`printk_ringbuffer_kunit_test.c` is a KUnit stress test for lockless printk ringbuffer data integrity. It creates a private ringbuffer, starts per-CPU writer kthreads, and validates records from a reader thread for a configurable runtime.

## Important APIs, types, and functions
The test uses `DEFINE_PRINTKRB()`, `prb_init()`, `prb_rec_init_wr()`, `prb_reserve()`, `prb_commit()`, `prb_rec_init_rd()`, and `prb_read_valid()`. `struct prbtest_rbdata` is the embedded payload format with a size field and repeated-character text. `struct prbtest_data` tracks the KUnit instance, ringbuffer, and waitqueue. `prbtest_writer()` generates records, `prbtest_reader()` validates them, and `test_readerwriter()` orchestrates CPU selection and kthread startup.

## Control flow
The test snapshots online CPUs under the CPU hotplug read lock, chooses one CPU for the reader, and uses remaining CPUs for writers. Each writer repeatedly picks a random text size, reserves a record, fills an embedded size plus repeated byte pattern based on CPU/thread identity, commits it, and wakes the reader. The reader waits until a requested sequence can be read, checks monotonicity, validates size, terminator, and repeated content, then advances to the next sequence.

## State and persistence behavior
State is entirely test-local. The static test ringbuffer is reinitialized at test start because KUnit may rerun suites. KUnit cleanup actions free the cpumask and stop writer kthreads. A stack timer wakes the reader after `runtime_ms` by setting `TIF_NOTIFY_SIGNAL`, ending the wait loop.

## Dependencies and integration points
The file integrates KUnit resources/actions, CPU masks and hotplug locking, kthreads, timers, waitqueues, scheduler rescheduling, random number generation, and KUnit-only exported ringbuffer symbols via `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`.

## Risks and invariants
The test intentionally ignores reservation failure because it drives unbounded concurrent writers. That means it detects corruption and sequence problems, not throughput success. CPU hotplug changes after the snapshot can reduce ideal isolation but are treated as non-fatal. The reader loop depends on the wake timer to terminate, so timer cleanup must run reliably.

## Test signals
Failures are explicit `KUNIT_FAIL()` reports for bad sequence reads or malformed records. Useful stress signals include running on many CPUs, increasing `runtime_ms`, enabling KCSAN/lockdep, and seeing no malformed repeated strings despite descriptor/data wrap and concurrent overwrite.
