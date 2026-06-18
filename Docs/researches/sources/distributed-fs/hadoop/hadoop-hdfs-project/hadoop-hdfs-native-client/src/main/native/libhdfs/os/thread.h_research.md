# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/thread.h

## Purpose
`thread.h` defines the platform-neutral thread abstraction for `libhdfs`.

## Important APIs, Control Flow, and State
It declares `threadProcedure` as `void (*)(void *)` and a `thread` struct containing platform `threadId`, start function, and argument pointer. `threadCreate` immediately starts a new thread based on that struct; `threadJoin` waits for completion.

## Dependencies and Integration Points
The header includes `platform.h` for `threadId`, mapping to `pthread_t` on POSIX and `HANDLE` on Windows. Platform implementations adapt the generic callback to `pthread_create` or `CreateThread`.

## Risks and Test Signals
The API leaves ownership and lifetime of the `thread` struct and `arg` to callers. It also omits return values, thread attributes, detaching, and cancellation. Tests should verify basic create/join on all platforms and ensure callers do not pass stack state that can disappear before the new thread starts.
