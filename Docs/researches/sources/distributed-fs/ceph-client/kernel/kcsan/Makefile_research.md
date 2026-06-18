# sources/distributed-fs/ceph-client/kernel/kcsan/Makefile

## Purpose
Builds the KCSAN runtime, debugfs interface, reporting code, boot selftest, and optional KUnit suite with the instrumentation exclusions required for sanitizer runtime code.

## Important APIs, Types, and Functions
This is Kbuild metadata rather than C API. It sets `KCSAN_SANITIZE := n`, `KCOV_INSTRUMENT := n`, `UBSAN_SANITIZE := n`, removes ftrace flags from runtime objects, sets special `CFLAGS_core.o`, builds `core.o debugfs.o report.o`, and conditionally builds `selftest.o` and `kcsan_test.o`.

## Control Flow
Kbuild uses the file to prevent recursive sanitizer/ftrace instrumentation of the sanitizer runtime. `KCSAN_INSTRUMENT_BARRIERS_selftest.o := y` forces barrier instrumentation in boot selftests, while `CFLAGS_kcsan_test.o := $(CFLAGS_KCSAN)` intentionally instruments the KUnit tests.

## State and Persistence
No runtime state. Build-time flags determine which objects exist and how they are instrumented.

## Dependencies and Integration Points
Integrates with Kbuild sanitizer variables, ftrace flags, structleak plugin disabling, and `CONFIG_KCSAN_SELFTEST` / `CONFIG_KCSAN_KUNIT_TEST`.

## Risks
Accidentally instrumenting runtime objects can recurse into KCSAN from KCSAN itself. Removing required instrumentation from tests would make selftests meaningless. Architecture-specific atomics require `-mno-outline-atomics` when supported.

## Test Signals
Build output and enabled config options determine whether boot selftests and KUnit tests are available. Recursive instrumentation failures usually appear as early boot crashes or noisy sanitizer recursion.
