## sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.h

Purpose: placeholder NetBSD inode header. The file contains only an identifying comment in the inspected tree.

Important APIs/types/functions: no macros, types, or prototypes are defined.

Control flow: none.

Dependencies and integration: installed by `src/afs/Makefile.in` as `${MKAFS_OSTYPE}/osi_inode.h` for the selected platform. It satisfies include/install expectations for OpenAFS code that has a platform `osi_inode.h` contract.

State and persistence: none.

Risks: because it is empty, any future common code that expects NetBSD-specific inode definitions must add them here or guard its usage. Empty installed headers can hide missing implementation until a consumer uses a symbol.

Test signals: include-tree install checks, NetBSD client build, and downstream code that includes `<afs/osi_inode.h>`.
