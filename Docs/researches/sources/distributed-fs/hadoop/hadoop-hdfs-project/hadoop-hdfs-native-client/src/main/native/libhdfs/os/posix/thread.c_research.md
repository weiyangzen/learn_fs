# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/posix/thread.c

## Purpose
This file implements the `libhdfs` cross-platform thread abstraction on POSIX using pthreads.

## Important APIs, Control Flow, and State
`runThread` adapts a `threadProcedure(void*)` to the `pthread_create` signature by calling `t->start(t->arg)` and returning `NULL`. `threadCreate` starts the thread and stores the pthread ID in `t->id`; `threadJoin` blocks on `pthread_join`. Both print platform error codes to stderr and return the pthread error code.

## Dependencies and Integration Points
It depends on `os/thread.h`, pthreads, and stdio. Callers must keep the `thread` struct valid until the new thread reads its start function and argument.

## Risks and Test Signals
Lifetime of the `thread` struct passed to `pthread_create` is the main risk. The API does not support detached threads, return values, cancellation, or custom attributes. Tests should cover creation, join, failure propagation, and use under libhdfs async or helper code that depends on this abstraction.
