# sources/distributed-fs/openafs/src/afs/HPUX/osi_prototypes.h

## sources/distributed-fs/openafs/src/afs/HPUX/osi_prototypes.h

Purpose: HP-UX OSI prototype placeholder.

Important APIs/types/functions: only include guards are defined; no prototypes are exported locally.

Control flow: none.

State/persistence: none.

Dependencies/integration: included by platform build logic expecting an `osi_prototypes.h` file for each port.

Risks/test signals: risk is absence of prototypes hiding implicit-int or K&R declarations in legacy HP-UX code. Build warnings are the only meaningful signal.
