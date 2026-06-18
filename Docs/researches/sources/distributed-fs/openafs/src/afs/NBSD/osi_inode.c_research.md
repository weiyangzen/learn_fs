## sources/distributed-fs/openafs/src/afs/NBSD/osi_inode.c

Purpose: this inspected file contains only the standard OpenAFS license/comment block and no executable code.

Important APIs/types/functions: none are defined in this file.

Control flow: none.

Dependencies and integration: likely retained for source-list symmetry with platforms that implement inode-level cache helpers. NetBSD inode definitions are not provided here; platform header installation uses `osi_inode.h`, which is also effectively a placeholder in this subset.

State and persistence: none.

Risks: no direct runtime risk. The risk is build-system or common-code drift assuming NetBSD has inode helper symbols here when it does not.

Test signals: NetBSD build/link coverage, cache backends that might include `osi_inode.c`, and comparison against other OS ports to confirm missing inode helpers are intentional.
