## sources/distributed-fs/openafs/src/afs/NBSD/osi_prototypes.h

Purpose: NetBSD OSI prototypes header placeholder.

Important APIs/types/functions: the file only defines include guards (`_OSI_PROTO_H_`) and contains no prototypes. Its comment says "Exported macos support routines", which appears stale or copied and does not match the NetBSD path.

Control flow: none.

Dependencies and integration: may be included by common/platform code expecting an OSI prototypes header. In this tree it does not expose any NetBSD declarations; declarations instead appear in other headers such as `osi_machdep.h` or source-local prototypes.

State and persistence: none.

Risks: stale comments and empty headers can mislead maintainers. If new NetBSD OSI functions need shared prototypes, adding them here would reduce implicit-declaration or source-local duplication risk.

Test signals: include hygiene, warnings-as-errors builds for missing prototypes, and audit for functions declared only in C files.
