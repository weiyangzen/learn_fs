# sources/distributed-fs/glusterfs/xlators/features/quota/src/quota-messages.h

## Purpose
`quota-messages.h` declares stable GlusterFS message IDs for quota and quotad logging. It centralizes symbolic IDs used by `gf_msg()` calls throughout quota enforcement, RPC, ancestry building, xdata serialization, and memory handling.

## Important APIs and Types
- `GLFS_MSGID(QUOTA, ...)` registers quota message symbols including `Q_MSG_ENFORCEMENT_FAILED`, `Q_MSG_ENOMEM`, `Q_MSG_CROSSED_SOFT_LIMIT`, `Q_MSG_QUOTA_ENFORCER_RPC_INIT_FAILED`, `Q_MSG_RPCSVC_INIT_FAILED`, `Q_MSG_ANCESTRY_BUILD_FAILED`, `Q_MSG_SIZE_KEY_MISSING`, and `Q_MSG_INTERNAL_FOP_KEY_MISSING`.

## Control Flow
There is no executable control flow. The header is compiled into code that logs quota errors, warnings, traces, and events with consistent message IDs.

## State and Persistence
The IDs are ABI-like diagnostic constants. Comments explicitly warn that IDs must be appended, not deleted or reused, to preserve log interpretation stability across releases.

## Dependencies and Integration Points
The header depends on `<glusterfs/glfs-message-id.h>` and is included by quota client, server, and helper code. It integrates with GlusterFS logging and event infrastructure; log consumers can key off these IDs.

## Risks
Deleting or reordering IDs can invalidate documentation, monitoring, and support workflows. Sparse or duplicated IDs would reduce diagnostic precision.

## Test Signals
Compile-time use of all symbols catches missing IDs. Logging tests should assert that common failure paths such as xdata decode failure, missing quota size, and RPC initialization failure emit the expected quota component IDs.
