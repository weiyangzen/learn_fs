# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_03.sh

## Purpose
This test validates batch I/O with fewer userspace server threads than hardware queues: one thread servicing four queues.

## Important APIs, Types, and Functions
It uses `_have_feature "BATCH_IO"`, `_have_program fio`, `_create_backfile`, `_add_ublk_dev -t loop -q 4 --nthreads 1 -b`, and fio read/write workload.

## Control Flow
The script skips without batch or fio, creates a 512 MiB backing file, adds a four-queue loop device with one batch thread, runs fio with four jobs, then cleans up.

## State and Persistence
Temporary backing file and ublk device state are removed by cleanup.

## Dependencies and Integration Points
It depends on `ublk_batch_setup_map()` assigning multiple queues to one thread and on loop target correctness.

## Risks
This stresses per-thread commit buffers for multiple queues and can expose queue index/buffer index bugs.

## Test Signals
Pass means one batch thread can service four queues under fio read/write load.
