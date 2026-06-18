## sources/distributed-fs/openafs/src/afs/NBSD/osi_vfs.h

Purpose: small NetBSD VFS compatibility header for mode-bit aliases.

Important APIs/macros: defines include guard `_OSI_VFS_H` and maps `VSUID` to `S_ISUID` and `VSGID` to `S_ISGID`.

Control flow: none.

Dependencies and integration: included by platform/common code needing portable vnode mode-bit names. The actual richer NetBSD vnode/VFS mappings are in `osi_machdep.h`.

State and persistence: none.

Risks: minimal. The header assumes `S_ISUID` and `S_ISGID` are in scope before use. Future mode aliases should be coordinated with `osi_machdep.h` to avoid split definitions.

Test signals: compile coverage for NetBSD code paths using `VSUID`/`VSGID`, and include-order checks ensuring mode constants are defined.
