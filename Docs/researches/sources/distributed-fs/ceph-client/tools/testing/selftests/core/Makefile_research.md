# sources/distributed-fs/ceph-client/tools/testing/selftests/core/Makefile

## Purpose

The core `Makefile` builds generic core selftests for `close_range` and `unshare`. The complete 7-line file was read.

## Important APIs, Types, and Functions

It appends `-g $(KHDR_INCLUDES)` to `CFLAGS`, defines `TEST_GEN_PROGS := close_range_test unshare_test`, and includes `../lib.mk`.

## Control Flow

Kselftest make infrastructure compiles the two listed generated programs using kernel headers.

## State and Persistence Behavior

It only produces build artifacts and has no runtime state.

## Dependencies and Integration Points

It depends on `KHDR_INCLUDES`, the selftests top-level make conventions, and source files `close_range_test.c` and `unshare_test.c` in the same directory.

## Risks and Edge Cases

Header mismatches or missing source files break the directory build. Debug info is always enabled through `-g`.

## Test Signals

Successful build of `close_range_test` and `unshare_test` validates the Makefile.
