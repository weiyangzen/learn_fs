# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/Makefile

Purpose: builds the main powerpc transactional-memory selftest suite.

Important APIs/types/functions: groups signal-context checks in `SIGNAL_CONTEXT_CHK_TESTS` and adds many `TEST_GEN_PROGS`, including syscall, signal, SPR, TAR, trap, unavailable, poison, and VMX copy tests.

Control flow: all binaries link `../harness.c` and `../utils.c`, with global `CFLAGS += -mhtm`. Selected targets add `-pthread`, `-m64`, `-mvsx`, `-O0`, kernel header includes, or PMU support; signal-context checks depend on `tm-signal.S`.

State and persistence behavior: build-only file; output binaries and `settings` test file are the generated state.

Dependencies and integration points: integrates with kselftest `lib.mk`, powerpc flags, HTM-capable compiler, and architecture-specific assembly helpers.

Risks and test signals: unsupported compiler flags or missing HTM instruction support fail at build time. Many runtime tests skip on systems without real HTM.
