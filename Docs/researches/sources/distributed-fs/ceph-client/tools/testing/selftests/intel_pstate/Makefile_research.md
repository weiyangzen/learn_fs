# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/Makefile

Purpose: this kselftest Makefile builds and registers the Intel P-state frequency validation test.

Important APIs and variables: it appends `-Wall` to `CFLAGS` and `-lm` to `LDLIBS`, normalizes `ARCH` through `ARCH_PROCESSED`, and only sets `TEST_GEN_FILES := msr aperf` on x86/i386/x86_64. `TEST_PROGS := run.sh` registers the shell driver. `include ../lib.mk` imports kselftest behavior. `$(TEST_GEN_FILES): $(HEADERS)` declares generated binaries depend on kselftest headers.

Control flow: on x86, make builds `msr` and `aperf`; on other architectures it only exposes `run.sh`, whose own runtime check skips non-x86.

State and persistence: generated files are the `msr` and `aperf` binaries in the build output. No custom clean target is needed beyond kselftest framework defaults.

Dependencies and integration points: integrates with the kselftest build system, math library for `aperf.c`, and runtime `run.sh`.

Risks: architecture detection is string-based; generated binaries are omitted on non-x86, so direct manual invocation of `run.sh` outside kselftest build output can fail if binaries are missing.

Test signals: build success on x86 yields `msr` and `aperf`; runtime pass/fail is governed by `run.sh`.
