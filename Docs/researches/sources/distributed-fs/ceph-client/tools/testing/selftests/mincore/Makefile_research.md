# sources/distributed-fs/ceph-client/tools/testing/selftests/mincore/Makefile

Purpose: builds the mincore kselftest.

Important APIs/types/functions: sets `CFLAGS += -Wall`, declares `TEST_GEN_PROGS := mincore_selftest`, and includes `../lib.mk`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration points: libc/kernel support for `mincore`, `mmap`, and kselftest harness.

Risks: minimal Makefile assumes default lib.mk rules suffice.

Test signals: generated `mincore_selftest` binary.
