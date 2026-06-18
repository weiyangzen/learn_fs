# sources/distributed-fs/lizardfs/src/mount/client/iovec_traits.h

## Purpose
`iovec_traits.h` provides small inline helpers for copying contiguous buffers and other iovec arrays into caller-provided iovec destinations. It also defines a fallback `struct iovec` on Windows-like builds.

## Important APIs, Types, And Functions
- `memcpyIoVec(const iovec*, int, const char*, size_t)` copies a contiguous buffer into an iovec sequence.
- `copyIoVec(const iovec* buf, int bufcnt, const iovec* iov, int iovcnt)` copies from one iovec sequence into another and returns bytes copied.

## Control Flow
Both helpers iterate destination/source segments, copying the minimum available bytes per segment and advancing through zero-length or exhausted entries. Assertions enforce non-null pointers and nonnegative counts.

## State And Persistence
No state or persistence. These are pure memory-copy helpers.

## Dependencies And Integration Points
`lizardfs_c_api.cc` uses `copyIoVec` for `liz_readv`, copying a `ReadCache::Result` converted to iovecs into user buffers. The header uses POSIX `<sys/uio.h>` outside Windows.

## Risks
- `copyIoVec` initializes `iov_base` and `buf_base` from the first entries before checking whether counts are zero; zero counts with invalid pointers can still be problematic despite assertions.
- Parameter names are confusing: `buf` is destination and `iov` is source.
- Assertions disappear in release builds, so invalid pointers/counts become undefined behavior.

## Test Signals
Tests should cover multi-segment copies, zero-length segments, partial destination capacity, zero requested bytes, and source/destination count edge cases.
