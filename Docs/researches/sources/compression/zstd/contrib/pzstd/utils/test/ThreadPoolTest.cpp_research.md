<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ThreadPoolTest.cpp -->
# sources/compression/zstd/contrib/pzstd/utils/test/ThreadPoolTest.cpp

## Purpose
This file tests `ThreadPool` task execution and shutdown behavior.

## Important APIs, Types, And Functions
It uses `ThreadPool::add`, atomics, sleeps, and result vectors in tests for ordering, all-jobs-finished, and add-job-while-joining behavior.

## Control Flow
Tests enqueue multiple tasks, let the pool destructor join workers, then inspect completed counters/results. One test attempts to enqueue after destruction has begun to document behavior.

## State And Persistence
State is local vectors and atomics. No files are written.

## Dependencies And Integration Points
It depends on GoogleTest and `utils/ThreadPool.h`. It validates the worker executor used by pzstd compression and decompression.

## Risks
Timing-sensitive tests can be flaky across slow or heavily loaded systems.

## Test Signals
Passing tests support that queued work drains and worker threads join cleanly.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/test/ThreadPoolTest.cpp -->
