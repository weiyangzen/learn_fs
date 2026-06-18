# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/thread.c

## Purpose
This file implements the `libhdfs` thread abstraction on Windows using `CreateThread` and wait handles.

## Important APIs, Control Flow, and State
`runThread` adapts the generic `threadProcedure` to the `DWORD WINAPI` signature, calls `t->start(t->arg)`, and returns 0. `threadCreate` calls `CreateThread`, stores the resulting `HANDLE` in `t->id`, and reports `GetLastError` on failure. `threadJoin` waits indefinitely with `WaitForSingleObject`, treating `WAIT_OBJECT_0` as success and logging `WAIT_FAILED` or unexpected waits.

## Dependencies and Integration Points
It depends on `os/thread.h` and Windows APIs. Higher-level code sees the same `threadCreate`/`threadJoin` contract as POSIX.

## Risks and Test Signals
The handle is never closed after join, so repeated use can leak handles unless managed elsewhere. Lifetime of the `thread` struct still matters. Tests should cover successful create/join, failure paths, handle cleanup expectations, and builds under both 32-bit and 64-bit Windows.
