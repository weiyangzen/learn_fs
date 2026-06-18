# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-messages.h

## Purpose
Declares stable structured log IDs for the leases translator.

## Important APIs, Types, and Functions
`GLFS_MSGID(LEASES, ...)` declares IDs for allocation failure, recall failure, invalid lease IDs/unlocks/types, invalid inode/fd ctx, disabled translator, missing timer wheel, and cleanup lookup failures.

## Control Flow
No runtime flow; `leases.c` and `leases-internal.c` reference these IDs in `gf_msg()` calls.

## State and Persistence
No runtime state. IDs are intended to be append-only.

## Dependencies and Integration Points
Includes `<glusterfs/glfs-message-id.h>` and integrates with GlusterFS logging.

## Risks and Edge Cases
Removing/reordering IDs can break log consumers. New log sites should append IDs instead of reusing unrelated ones.

## Test Signals
Compile verifies referenced message IDs exist.
