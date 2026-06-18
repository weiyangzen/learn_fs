# sources/distributed-fs/ceph-client/tools/testing/selftests/connector/Makefile

## Purpose

The connector `Makefile` builds the process connector filter selftest. The complete 6-line file was read.

## Important APIs, Types, and Functions

It appends `-Wall $(KHDR_INCLUDES)` to `CFLAGS`, defines `TEST_GEN_PROGS = proc_filter`, and includes `../lib.mk`.

## Control Flow

Kselftest make infrastructure compiles `proc_filter.c` into the generated test program.

## State and Persistence Behavior

It only produces build artifacts and has no runtime persistence.

## Dependencies and Integration Points

It depends on kernel headers through `KHDR_INCLUDES` and selftests `lib.mk`.

## Risks and Edge Cases

Warnings are enabled with `-Wall`; header drift in connector/proc connector structs can break the build.

## Test Signals

Successful build of `proc_filter` validates the Makefile.
