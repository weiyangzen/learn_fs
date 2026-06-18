# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/Makefile

Purpose: this kselftest makefile builds and registers the CAN raw-filter selftest in the `tools/testing/selftests/net/can` subtree. It declares `test_raw_filter.sh` as the executable test program and `test_raw_filter` as a generated binary.

Important APIs and variables: `top_srcdir = ../../../../..` points include paths at the kernel source root. `CFLAGS` enables warnings, optimization, debug info, the kernel UAPI include directory, and `$(KHDR_INCLUDES)`. `TEST_PROGS` and `TEST_GEN_FILES` are the kselftest/lib.mk contract variables consumed by `../../lib.mk`.

Control flow and integration: including `../../lib.mk` supplies the build/install/run rules. The generated C test depends on the kselftest harness and CAN UAPI headers, while the shell wrapper handles CAN interface setup.

State and dependencies: this file persists no runtime state. Build state is the compiled `test_raw_filter` artifact. It depends on the surrounding kselftest make infrastructure and suitable kernel headers.

Risks and test signals: the main risk is build/environment mismatch, especially missing or stale UAPI CAN headers. A successful signal is that `make` emits the `test_raw_filter` binary and the kselftest runner sees `test_raw_filter.sh` as the runnable program.
