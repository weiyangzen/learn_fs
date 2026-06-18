# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/Makefile

Purpose: builds the VPHN associativity unpacking selftest.

Important APIs/types/functions: declares `TEST_GEN_PROGS := test-vphn`, includes kselftest make files, and sets `CFLAGS += -m64 -I$(CURDIR) -fno-strict-aliasing`.

Control flow: `test-vphn` links with `../harness.c`; `test-vphn.c` includes `vphn.c` directly for userspace testing.

State and persistence behavior: build-only file, no runtime state.

Dependencies and integration points: depends on local `asm/vphn.h`, powerpc 64-bit compiler support, and kselftest harness.

Risks and test signals: 32-bit builds are not targeted. Strict-aliasing is disabled because the parser views packed register bytes through different integer widths.
