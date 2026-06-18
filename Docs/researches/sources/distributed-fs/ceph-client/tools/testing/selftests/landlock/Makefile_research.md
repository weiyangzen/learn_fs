# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/Makefile

## Purpose
This Makefile builds the Landlock selftest binaries and helper executables. It collects all `*_test.c` files as generated test programs, adds the `fs_bench` benchmark, and defines statically linked extended helper programs used by tests that exec or coordinate subprocesses.

## Important APIs, Types, And Functions
Key make variables are `CFLAGS`, `KHDR_INCLUDES`, `LOCAL_HDRS`, `src_test`, `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `LDLIBS`, and `LDFLAGS`. The file includes the shared kselftest `../lib.mk`, which supplies standard build and install targets.

## Control Flow
The file adds warning, optimization, and kernel-header include flags, records local headers, expands `*_test.c` into test binaries, appends `fs_bench`, and declares `true`, `sandbox-and-launch`, `wait-pipe`, and `wait-pipe-sandbox` as extended generated programs. It assigns `-lcap -lpthread` to test binaries and static linking to helper binaries both before and after including `lib.mk` so the rules work for plain target names and `$(OUTPUT)/`-prefixed targets.

## State, Persistence, And Dependencies
Build artifacts are generated in the kselftest output directory or local tree depending on the harness. The tests depend on installed kernel UAPI headers, libcap, pthreads, and a static-link-capable toolchain for helpers. The comment reminds developers to run `make -C ../../../.. headers_install` first.

## Integration Points
The Makefile is consumed by the Linux kselftest build system. `audit_test.c` and other Landlock tests depend on the extended helpers named in `common.h`, especially `wait-pipe-sandbox`.

## Risks
Missing libcap, static libc support, or stale UAPI headers can cause build failures unrelated to Landlock behavior. The wildcard-based `src_test` means new `*_test.c` files automatically become test binaries, which is useful but can expose incomplete work. Duplicated linker assignments are intentional for target-prefix coverage but easy to simplify incorrectly.

## Test Signals
Useful signals are successful `make -C tools/testing/selftests/landlock`, all `*_test` programs linking with `-lcap -lpthread`, and helper binaries building statically. Runtime signals come from kselftest execution of the produced binaries and optional `fs_bench` manual runs.
