# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.h

## Purpose
Declares upcall private/client/inode/local state and the helper APIs shared between `upcall.c` and `upcall-internal.c`.

## Important APIs, Types, and Functions
- `EXIT_IF_UPCALL_OFF()` branches to a label when cache invalidation is disabled.
- `UPCALL_STACK_UNWIND()` and `UPCALL_STACK_DESTROY()` clean `upcall_local_t` around stack unwind/destroy.
- `upcall_private_t` stores timeout, inode context list/lock, reaper thread, registered xattr dict, fini flag, enable flag, and init flag.
- `upcall_client_t` stores client UID and access/expire timing.
- `upcall_inode_ctx_t` stores inode GFID and client list.
- `upcall_local_t` stores per-fop inode, locs, fd, and xattr copy.
- Function prototypes expose cleanup, reaper, enable checks, invalidation, xattr filtering/comparison, and invalidation-needed checks.

## Control Flow
Macros define common branch and cleanup behavior used by nearly every fop wrapper. The local-wipe pattern ensures refs are dropped after unwind.

## State and Persistence
Defines in-memory state only. The client/inode registries are per-graph runtime cache state.

## Dependencies and Integration Points
Depends on GlusterFS client, upcall utils, compat errno, message/memory headers, stack, loc, dict, and inode types.

## Risks
The `upcall_local` comment notes pointer lifetime uncertainty; all stored pointers must be refcounted or copied. Macros hide cleanup side effects and require consistent frame ownership.

## Test Signals
Compile coverage plus runtime leak/refcount tests around fop callbacks and fini/forget paths.
