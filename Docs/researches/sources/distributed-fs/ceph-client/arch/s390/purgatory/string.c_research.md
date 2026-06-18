<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/string.c -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/string.c

Purpose: This file supplies minimal string/memory routines to the s390 purgatory by reusing the architecture string implementation in a freestanding build context.

Important APIs/types/functions: It defines `__HAVE_ARCH_MEMCMP` and includes `../lib/string.c`, allowing purgatory code to use `memcmp` for digest comparison without linking normal kernel libraries.

Control flow: There is no local control flow beyond inclusion. The included implementation provides the actual routines.

State and persistence: No local persistent state exists. The compiled routines become part of the purgatory binary.

Dependencies and integration points: It depends on the s390 architecture string implementation and the purgatory Makefile flags. It is used by `purgatory.c`.

Risks and test signals: Included code must remain freestanding-compatible and avoid kernel runtime dependencies. Tests include purgatory link checks and digest verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/string.c -->
