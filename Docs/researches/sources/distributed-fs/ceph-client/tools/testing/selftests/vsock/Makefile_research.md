# sources/distributed-fs/ceph-client/tools/testing/selftests/vsock/Makefile

## Purpose

This Makefile wires the vsock VM selftest wrapper into kselftest. It builds the shared `tools/testing/vsock/vsock_test` binary and installs it into the selftest output directory, while registering `vmtest.sh` as the test program.

## Important APIs, Types, and Functions

Key variables are `TOOLSDIR`, `VSOCK_TEST_DIR`, `VSOCK_TEST_SRCS`, `TEST_PROGS`, and `TEST_GEN_FILES`. The Makefile delegates `$(MAKE) -C $(VSOCK_TEST_DIR) vsock_test` and uses `install -m 755` to copy the generated binary to `$(OUTPUT)/vsock_test`. It includes `../lib.mk` for the kselftest build contract.

## Control Flow

`make` sees `TEST_PROGS += vmtest.sh` and `TEST_GEN_FILES := vsock_test`. The output binary target depends on the upstream vsock test binary, which in turn depends on all C and header files under `tools/testing/vsock`. Building this selftest therefore rebuilds the generic vsock test before the VM harness runs.

## State and Persistence Behavior

The file writes only build artifacts under `$(OUTPUT)` and the delegated vsock build directory. It has no runtime persistence.

## Dependencies and Integration Points

It integrates a selftests subdirectory with the generic vsock test suite and kselftest's `lib.mk`. The runtime script expects `vsock_test` to appear next to it.

## Risks and Edge Cases

The source dependency uses `wildcard` over C and header files, but changes in delegated Makefile logic or generated dependencies may not be visible here. Build failures in `tools/testing/vsock` surface as failures of this wrapper target.

## Test Signals

The main signal is that `$(OUTPUT)/vsock_test` exists and is executable, and kselftest enumerates `vmtest.sh` as the test program.
