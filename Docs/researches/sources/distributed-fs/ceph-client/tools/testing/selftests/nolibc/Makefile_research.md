# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/Makefile

Purpose: kselftest Makefile for nolibc tests, building both a `nolibc-test` binary without libc and a `libc-test` binary from the same sources for comparison.

Important APIs/variables: defines `TEST_GEN_PROGS := nolibc-test libc-test`, includes `../lib.mk`, compiler helpers, and `Makefile.include`. Defines `cc-option` through `__cc-option`. `nolibc-test` has custom `CFLAGS` with `-nostdlib -nostdinc -static`, nolibc and UAPI include paths, and `CFLAGS_NOLIBC_TEST`; `LDLIBS` uses `-lgcc` when not LLVM. Both targets depend on `NOLIBC_TEST_SOURCES`; nolibc target also orders after `headers`.

Control flow: normal kselftest build uses inherited rules for `TEST_GEN_PROGS`, with explicit flags/LDLIBS for nolibc. `libc-test` has an explicit compile/link recipe using `$(LINK.c)`. `help` delegates to `Makefile.nolibc help`.

State and persistence: writes build outputs under `$(OUTPUT)`. No runtime state.

Dependencies and integration: integrated with kernel selftests build system, nolibc headers under `tools/include/nolibc`, generated kernel headers, and optional architecture/compiler flags from `Makefile.include`.

Risks: static nolibc link is sensitive to compiler/architecture support and `-lgcc` availability outside LLVM. Missing generated headers break the ordered `headers` dependency.

Test signals: successful build of both generated programs; runtime behavior is in the binaries built from `NOLIBC_TEST_SOURCES`.
