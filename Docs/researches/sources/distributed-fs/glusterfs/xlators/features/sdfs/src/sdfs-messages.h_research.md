# sources/distributed-fs/glusterfs/xlators/features/sdfs/src/sdfs-messages.h

## Purpose
`sdfs-messages.h` defines SDFS log message ID constants for the SDFS translator. It follows older explicit macro style rather than the `GLFS_MSGID()` macro used by quota.

## Important APIs and Types
- `GLFS_SDFS_BASE` is defined as `GLFS_MSGID_COMP_SDFS`.
- `GLFS_SDFS_NUM_MESSAGES` is `2`.
- `GLFS_MSGID_END` marks the end of the SDFS component range.
- `SDFS_MSG_ENTRYLK_ERROR` and `SDFS_MSG_MKDIR_ERROR` are the two message IDs.
- `glfs_msg_start_x` and `glfs_msg_end_x` define sentinel message tuples.

## Control Flow
No executable control flow. The constants are used by SDFS logging sites to tag errors.

## State and Persistence
Message IDs are stable diagnostic constants and should be treated as persistent log ABI. Comments describe rules for appending, modifying, and deleting messages.

## Dependencies and Integration Points
Depends on `<glusterfs/glfs-message-id.h>`. It is referenced by the SDFS build and presumably by `sdfs.c` logging. The header guard macro starts as `_DFS_MESSAGES_H_` and ends with a comment naming `_SDFS_MESSAGES_H_`.

## Risks
- `glfs_msg_start_x` uses `GLFS_DFS_BASE`, which appears inconsistent with `GLFS_SDFS_BASE` and may be a typo unless defined elsewhere.
- The header guard/comment naming mismatch is harmless to compilation but increases maintenance confusion.
- `GLFS_SDFS_NUM_MESSAGES` must be incremented when adding IDs.
- Documentation comments for each message are empty, limiting operational guidance.

## Test Signals
Build SDFS with server support to catch undefined `GLFS_DFS_BASE` or header guard issues. Logging tests should ensure `SDFS_MSG_ENTRYLK_ERROR` and `SDFS_MSG_MKDIR_ERROR` map into the SDFS component range and that new message additions update the count.
