# sources/distributed-fs/openafs/src/afs/sysctl.h

Purpose: assigns numeric sysctl namespace IDs for platform-independent and platform-specific OpenAFS cache-manager controls.

Important APIs/types: top-level IDs include `AFS_SC_ALL`, `AFS_SC_DARWIN`, `AFS_SC_AIX`, `AFS_SC_DFBSD`, `AFS_SC_FBSD`, `AFS_SC_LINUX`, `AFS_SC_HPUX`, `AFS_SC_IRIX`, `AFS_SC_NBSD`, `AFS_SC_OBSD`, `AFS_SC_SOLARIS`, and `AFS_SC_UKERNEL`. Subspaces define Darwin releases and feature controls, AIX releases, FreeBSD releases, and Linux kernel generations.

Control flow: compile-time constants only.

State and persistence: none in this header; external sysctl registration code interprets these IDs.

Dependencies and integration points: used by OS-specific sysctl handlers and user/admin tooling that expects stable numeric IDs.

Risks: renumbering breaks compatibility. Adding new platform controls must avoid collisions and preserve existing values.

Test signals: compile sysctl consumers, verify registered OIDs match expected numeric paths, and test platform feature toggles such as Darwin real modes, fsevents, and bulkstat where implemented.
