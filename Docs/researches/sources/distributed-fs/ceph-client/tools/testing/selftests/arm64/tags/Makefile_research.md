# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/Makefile

## Purpose

This Makefile builds the arm64 tagged-address syscall smoke test `tags_test`.

## Important APIs, Types, and Functions

It appends `$(KHDR_INCLUDES)` to `CFLAGS`, declares `TEST_GEN_PROGS := tags_test`, and includes `../../lib.mk`.

## Control Flow and Data Flow

Kselftest make infrastructure compiles `tags_test.c` into the generated program list and handles install/clean behavior.

## State and Persistence Behavior

Only build outputs in `$(OUTPUT)` are produced.

## Dependencies and Integration Points

It depends on kernel UAPI headers for `PR_SET_TAGGED_ADDR_CTRL` and kselftest `lib.mk`.

## Risks and Edge Cases

The file is intentionally minimal; missing kernel headers or unsupported target architecture will surface at compile time.

## Test Signals

A successful build creates the `tags_test` kselftest binary.
