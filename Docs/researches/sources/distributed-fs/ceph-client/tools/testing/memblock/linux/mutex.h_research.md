<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mutex.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mutex.h

## Purpose

`linux/mutex.h` is a simulator mutex shim. It provides enough syntax for kernel code that declares mutexes or uses guard-style mutex helpers, without implementing locking.

## Important APIs, Types, and Functions

It defines `DEFINE_MUTEX(name)` as an `int`, provides `dummy_mutex_guard(int *name)`, and maps `guard(mutex)` to the dummy guard symbol.

## Control Flow

There is no locking behavior. Guard expressions compile to dummy functions, so critical sections are not serialized.

## State and Persistence Behavior

Mutexes become integer variables with no lock state. The simulator is single-process and does not persist synchronization state.

## Dependencies and Integration Points

It integrates with kernel code included in the memblock simulator that expects mutex macros. The tests themselves run single-threaded, so real locking is unnecessary for current coverage.

## Risks and Edge Cases

Concurrency behavior is not tested. If future simulator code becomes multi-threaded or depends on lock ordering, this shim will be insufficient.

## Test Signals

Compilation is the key signal. Any runtime race tests or lockdep-like expectations would require a real mutex model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mutex.h -->
