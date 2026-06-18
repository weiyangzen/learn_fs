# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-messages.h

## Purpose
Defines message IDs for utime logging.

## Important APIs, Types, and Functions
- `GLFS_MSGID(UTIME, UTIME_MSG_NO_MEMORY, UTIME_MSG_SET_MDATA_FAILED, UTIME_MSG_DICT_SET_FAILED)`.

## Control Flow
No runtime control flow.

## State and Persistence
Message ordering is persistent logging ABI.

## Dependencies and Integration Points
Included by `utime.c` for `gf_msg()` calls.

## Risks
IDs must be appended, not removed or reordered.

## Test Signals
Build and log-path coverage for no-memory, mdata set, and dict set failures.
