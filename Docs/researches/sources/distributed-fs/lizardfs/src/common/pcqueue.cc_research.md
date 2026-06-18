<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.cc -->
# sources/distributed-fs/lizardfs/src/common/pcqueue.cc

## Purpose
Implements a C-style pthread producer/consumer queue with optional byte-size capacity. The source was read completely for this report.

## Important APIs, Types, And Functions
`queue_new/delete/isempty/elements/isfull/sizeleft/put/tryput/get/tryget` manage `qentry` linked-list nodes under a mutex with wait-free and wait-full condition variables.

## Control Flow
Producers allocate an entry, block or fail if adding `leng` would exceed `maxsize`, append to the tail, and signal consumers. Consumers block or fail when empty, pop the head, update byte size, and signal producers.

## State And Persistence Behavior
Runtime heap state is the queue struct, linked entries, counters, mutex, and condition variables. Payload ownership is transferred to callers/deleter by convention.

## Dependencies And Integration Points
Depends on pthreads, project assert macros, and `TracePrinter`. Used by legacy threaded worker queues.

## Risks And Edge Cases
Waiter counters are manually maintained and can become inaccurate if pthread waits are interrupted unexpectedly. `queue_delete` asserts no waiters, so lifecycle must be externally quiesced. Blocking `queue_put` leaks the preallocated entry only if an assertion aborts.

## Test Signals
Needs multithreaded tests for blocking/full/empty behavior, try error codes, delete with queued payloads, and size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/pcqueue.cc -->
