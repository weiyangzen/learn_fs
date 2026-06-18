# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/batch.c

## Purpose
This file implements `UBLK_F_BATCH_IO` support for the `kublk` userspace server. It manages batched prep/fetch/commit buffers, multishot fetch commands, command completion handling, and queue-to-thread mapping for batched ublk I/O.

## Important APIs, Types, and Functions
Buffer helpers include `ublk_get_commit_buf()`, `ublk_alloc_commit_buf()`, `ublk_free_commit_buf()`, `ublk_commit_elem_buf_size()`, and `ublk_commit_buf_size()`. Allocation paths are `ublk_batch_prepare()`, `ublk_batch_alloc_buf()`, and `ublk_batch_free_buf()`. I/O command paths include `ublk_batch_start_fetch()`, `ublk_batch_queue_prep_io_cmds()`, `ublk_batch_compl_cmd()`, `ublk_batch_prep_commit()`, `ublk_batch_complete_io()`, `ublk_batch_commit_io_cmds()`, and `ublk_batch_setup_map()`.

## Control Flow
At thread initialization, `ublk_batch_prepare()` computes per-thread queue count, commit element size, commit buffer counts, and command flags. `ublk_batch_alloc_buf()` allocates mlocked commit buffers and registered provided-buffer rings for fetch buffers. Startup prepares each mapped queue with `UBLK_U_IO_PREP_IO_CMDS` and posts two multishot `UBLK_U_IO_FETCH_IO_CMDS` per queue. CQEs either deliver fetched tags to target `queue_io`, complete prep/commit buffers, or restart fetch commands when buffers end.

## State and Persistence
State lives in `struct ublk_thread`: commit-buffer allocator, `batch_commit_buf` array, fetch buffers, buffer rings, command counters, and per-thread queue mapping. It is runtime-only and freed at thread teardown.

## Dependencies and Integration Points
It depends on `kublk.h`, liburing, ublk UAPI batch commands, queue target callbacks, and the allocator utilities. `kublk.c` calls these functions when `UBLK_F_BATCH_IO` is enabled.

## Risks
Batch mode has strict buffer-index and queue/thread mapping assumptions. Incorrect CQE sizes or duplicate fetched tags trigger assertions/logs. The mapping supports N:M threads/queues, but comments note some commit paths still assume constrained behavior. mlock failures are logged but not fatal.

## Test Signals
Batch shell tests exercise basic filesystem use, 4 threads/1 queue, and 1 thread/4 queues. Success indicates prep/fetch/commit command sequencing, buffer index calculation, and multishot fetch restart behavior are correct.
