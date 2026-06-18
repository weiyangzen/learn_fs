# sources/distributed-fs/ceph-client/tools/testing/selftests/capabilities/Makefile

## Purpose

This Makefile builds Linux capability execve selftests and their validation helper.

## Important APIs, Types, and Functions

It sets `TEST_GEN_FILES := validate_cap`, `TEST_GEN_PROGS := test_execve`, adds `-O2 -g -std=gnu99 -Wall $(KHDR_INCLUDES)` to `CFLAGS`, links `-lcap-ng -lrt -ldl`, and includes `../lib.mk`.

## Control Flow

Kselftest builds the helper as a generated file and `test_execve` as the executable test. The main test copies `validate_cap` at runtime into a private tmpfs for setuid/setgid scenarios.

## State and Persistence Behavior

No runtime state is owned by the Makefile. Build outputs are used by runtime tests.

## Dependencies and Integration Points

It depends on libcap-ng and kernel capability headers. It integrates with the capabilities selftest directory and kselftest build infrastructure.

## Risks and Test Signals

Risks include missing libcap-ng development files or helper not being available beside `test_execve`. Signals are successful build and runtime discovery/copying of `validate_cap`.
