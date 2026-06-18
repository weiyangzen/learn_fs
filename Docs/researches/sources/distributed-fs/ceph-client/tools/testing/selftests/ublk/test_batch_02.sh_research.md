# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_batch_02.sh

## Purpose
This test validates batch I/O with more userspace server threads than hardware queues: four threads servicing one queue.

## Important APIs, Types, and Functions
It uses `_have_feature "BATCH_IO"`, `_have_program fio`, `_create_backfile`, `_add_ublk_dev -t loop -q 1 --nthreads 4 -b`, and fio read/write workload.

## Control Flow
The script skips without batch or fio, creates a 512 MiB file, adds a one-queue loop device in batch mode with four threads, runs fio read/write with four jobs, records fio exit code, and cleans up.

## State and Persistence
It creates a temporary backing file and ublk device, both cleaned up after the test.

## Dependencies and Integration Points
It depends on `kublk` batch queue-to-thread mapping and fio.

## Risks
The scenario stresses N:M batch mapping, buffer indexes, and completion routing. Fio/environment failures surface as test failures.

## Test Signals
Pass means one queue can be serviced by multiple batch threads under fio load.
