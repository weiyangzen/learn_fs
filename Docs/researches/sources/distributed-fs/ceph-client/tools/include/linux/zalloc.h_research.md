# sources/distributed-fs/ceph-client/tools/include/linux/zalloc.h

## Purpose
Declares small allocation helpers for Linux tools code: zeroed allocation and freeing-with-nullification.

## APIs, Types, and Functions
Declares `void *zalloc(size_t size)`, `void __zfree(void **ptr)`, and macro `zfree(ptr)` that casts the address of a typed pointer to `void **` before calling `__zfree()`.

## Control Flow, State, and Persistence
This header contains declarations only. Runtime behavior is supplied by the corresponding tools library implementation: allocate zero-filled memory, free memory, and clear the caller's pointer. Persistent state is limited to heap ownership in callers.

## Dependencies and Integration
Depends on `<stdlib.h>` for `size_t` and normal C allocation semantics. It integrates with tools code that follows kernel-style `kzalloc`/`kfree` patterns while running in userspace.

## Risks and Test Signals
Risks are passing non-pointer lvalues to `zfree`, double-free if aliases still exist, and assuming allocation failure is impossible. Test signals are allocation/failure paths in tool unit tests, pointer-nullification checks, leak detection, and ASan coverage for caller ownership mistakes.
