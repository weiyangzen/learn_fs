# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall-messages.h

## Purpose
Defines message IDs for upcall logging.

## Important APIs, Types, and Functions
- `GLFS_MSGID(UPCALL, UPCALL_MSG_NO_MEMORY, UPCALL_MSG_INTERNAL_ERROR, UPCALL_MSG_NOTIFY_FAILED)` registers three message IDs.

## Control Flow
No runtime control flow.

## State and Persistence
Message ordering is persistent logging ABI and must remain stable.

## Dependencies and Integration Points
Depends on `glfs-message-id.h`. Used by `upcall.c`/`upcall-internal.c` in `gf_msg()` calls.

## Risks
Removing or reordering IDs breaks log-id stability.

## Test Signals
Build and log-format tests for upcall error paths.
