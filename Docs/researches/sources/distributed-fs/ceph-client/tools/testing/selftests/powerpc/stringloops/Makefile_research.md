# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/Makefile

Purpose: builds the string primitive tests for powerpc `memcmp` and `strlen`, including 64-bit and optional 32-bit variants.

Important APIs/types/functions: `build_32bit` probes whether `$(CC) $(CFLAGS) -m32` works. `TEST_GEN_PROGS` always includes `memcmp_64` and `strlen`, and conditionally includes `memcmp_32` and `strlen_32`.

Control flow: `memcmp_64` links `memcmp.c` with `../utils.c` and compiles with `-m64 -maltivec`; `strlen` links `strlen.c` and `string.c`; all tests link `../harness.c`. Include path `-I$(CURDIR)` lets local kernel-style asm headers override normal kernel headers.

State and persistence behavior: no runtime state; build products live under `$(OUTPUT)`.

Dependencies and integration points: integrates with kselftest `lib.mk`, powerpc flags, and local `asm/` plus `linux/` compatibility headers.

Risks and test signals: the 32-bit probe is shell-fragile but only gates optional targets. Missing Altivec support or assembler opcode support can fail `memcmp_64` build.
