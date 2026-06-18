# sources/distributed-fs/openafs/src/afs/AIX/osi_prototypes.h

Purpose: AIX OSI prototype header for declarations not already covered elsewhere.

Important APIs and functions: declares `afs_aix_SetupPagRefCount(void)` under the `osi_groups.c` comment.

Control flow: none.

State and persistence: none in this header.

Dependencies and integration: included by AIX-specific OpenAFS files that need the PAG reference-count setup declaration.

Risks and test signals: the referenced function is not present in the listed `osi_groups.c`, so either it is compiled conditionally elsewhere or this header is stale. Build/link coverage is the key signal.
