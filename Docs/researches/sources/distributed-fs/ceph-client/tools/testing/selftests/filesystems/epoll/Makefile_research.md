# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/epoll/Makefile

## Purpose
Build metadata for the epoll wakeup filesystem selftest.

## Important APIs, Types, And Functions
Adds `$(KHDR_INCLUDES)` to `CFLAGS`, links pthread with `LDLIBS += -lpthread`, sets `TEST_GEN_PROGS := epoll_wakeup_test`, and includes `../../lib.mk`.

## Control Flow
kselftest builds the threaded epoll wakeup test binary from the directory’s source.

## State And Persistence
Generated binary only.

## Dependencies And Integration Points
Requires pthread and kernel headers. The generated test exercises epoll wakeup semantics but that source file is outside this work item.

## Risks
This Makefile only covers build metadata; behavioral coverage lives in `epoll_wakeup_test.c`. Link failures occur if pthread support is unavailable.

## Test Signals
Successful build produces `epoll_wakeup_test`.
