# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/switch_endian/common.h

Purpose: shared assembly include for endian-switch tests, providing syscall number fallback and common powerpc asm includes.

Important APIs/types/functions: includes `<ppc-asm.h>` and `<asm/unistd.h>`, and defines `__NR_switch_endian` as 363 if missing.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: included by `check.S` and `switch_endian_test.S`.

Risks and test signals: fallback syscall number is architecture-specific; stale numbers would make the test fail on old or divergent headers.
