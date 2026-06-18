# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/strlen_32.S

Purpose: 32-bit powerpc optimized `strlen` implementation imported for selftest builds.

Important APIs/types/functions: exports `test_strlen` through `_GLOBAL(strlen)` and uses classic word-at-a-time zero-byte detection with `lomagic` and `himagic` constants.

Control flow: aligned strings loop over words, using subtract/and masks to detect any zero byte, then isolate the byte position with big-endian-safe logic. Misaligned strings adjust the first loaded word so bytes before the string cannot appear as NUL.

State and persistence behavior: stateless leaf routine.

Dependencies and integration points: built conditionally when 32-bit compiler support exists, using local `asm/cache.h`, `asm/ppc_asm.h`, and `linux/export.h`.

Risks and test signals: correctness depends on endian and misalignment bit manipulation. `strlen.c` compares against libc across offsets, but its mismatch handling is diagnostic-only.
