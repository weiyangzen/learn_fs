# sources/distributed-fs/ceph-client/tools/testing/selftests/tdx/Makefile

## Purpose
Builds the TDX guest kselftest program.

## Important APIs, Types, and Functions
Sets `CFLAGS += -O3 -Wl,-no-as-needed -Wall $(KHDR_INCLUDES) -static`, defines `TEST_GEN_PROGS := tdx_guest_test`, and includes `../lib.mk`.

## Control Flow
Kselftest make infrastructure reads `TEST_GEN_PROGS`, compiles `tdx_guest_test.c` with kernel header includes, and emits the generated test binary.

## State and Persistence Behavior
Build output is the `tdx_guest_test` executable and normal kselftest build artifacts. The Makefile itself owns no runtime state.

## Dependencies and Integration Points
Depends on kernel UAPI headers, static linking support, and kselftest `lib.mk`. Integrates with `make -C tools/testing/selftests/tdx`.

## Risks and Edge Cases
Static linking can fail on environments without static libc. The test requires TDX guest driver support at runtime, so build success alone is not a functional signal.

## Test Signals
Signals are successful compilation with warnings enabled and generation of the `tdx_guest_test` binary.
