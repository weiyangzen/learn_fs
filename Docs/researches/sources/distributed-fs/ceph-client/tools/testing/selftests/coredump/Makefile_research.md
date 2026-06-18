# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/Makefile

## Purpose

This Makefile builds and installs the coredump selftest programs and the `stackdump` helper script.

## Important APIs, Types, and Functions

It sets `CFLAGS += -Wall -O0 -g $(KHDR_INCLUDES) $(TOOLS_INCLUDES)`, declares `TEST_GEN_PROGS` as `stackdump_test`, `coredump_socket_test`, and `coredump_socket_protocol_test`, and declares `TEST_FILES := stackdump`.

## Control Flow

The kselftest `../lib.mk` infrastructure handles build and run rules. Additional dependencies link `coredump_test_helpers.c` into each generated C test binary.

## State and Persistence Behavior

The file itself has no runtime state. It persists build metadata and ensures the shared helper source is rebuilt into each executable.

## Dependencies and Integration Points

It integrates with kernel selftest build variables, exported kernel headers, tools headers, and the common kselftest library. The generated tests depend on coredump, pidfd, Unix socket, and fs mount APIs.

## Risks and Edge Cases

If the helper dependency is omitted or stale, individual tests may fail at link time or run against mismatched declarations. `-O0 -g` favors debuggability over optimization.

## Test Signals

Successful `make` should produce all three binaries and copy `stackdump` as a test file. Build failures indicate missing headers, helper compile errors, or lib.mk integration problems.
