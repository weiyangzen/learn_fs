# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/linux/export.h

Purpose: minimal userspace stub for Linux `EXPORT_SYMBOL()` used by imported kernel string assembly.

Important APIs/types/functions: defines `EXPORT_SYMBOL(x)` as empty.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: lets `memcmp_32.S`, `memcmp_64.S`, and `strlen_32.S` compile outside the kernel.

Risks and test signals: adequate only for symbol export annotations; any future use of richer export macros would need expansion.
