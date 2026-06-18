# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/Makefile

## Purpose

The clone3 `Makefile` builds clone3 kselftest programs and links libcap for capability-specific tests. The complete 8-line file was read.

## Important APIs, Types, and Functions

It appends `-g -std=gnu99 $(KHDR_INCLUDES)` to `CFLAGS`, appends `-lcap` to `LDLIBS`, defines `TEST_GEN_PROGS := clone3 clone3_clear_sighand clone3_set_tid clone3_cap_checkpoint_restore`, and includes `../lib.mk`.

## Control Flow

Kselftest make infrastructure uses `TEST_GEN_PROGS` to compile and install the four generated binaries with the given flags and libraries.

## State and Persistence Behavior

It creates build outputs for clone3 selftests and does not affect runtime state.

## Dependencies and Integration Points

It depends on kernel header include paths from `KHDR_INCLUDES`, GNU99 C support, libcap, and selftests `lib.mk`.

## Risks and Edge Cases

Missing libcap headers/library breaks the whole directory build even though only one test needs libcap. Header/API drift in local kernel headers can affect clone3 struct and flag availability.

## Test Signals

Successful build of all four `TEST_GEN_PROGS` validates this file.
