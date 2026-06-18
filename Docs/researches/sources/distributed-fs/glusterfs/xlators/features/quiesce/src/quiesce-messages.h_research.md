# sources/distributed-fs/glusterfs/xlators/features/quiesce/src/quiesce-messages.h

## Purpose

`quiesce-messages.h` defines structured log message IDs for the quiesce translator.

## Important APIs, Types, and Functions

It declares the `QUIESCE` GLFS component and two messages: `QUIESCE_MSG_INVAL_HOST` for invalid failover host addresses and `QUIESCE_MSG_FAILOVER_FAILED` for failed failover initiation.

## Control Flow

No direct control flow exists. `quiesce.c` uses these message macros when parsing failover hosts and when failover setxattr submission fails.

## State and Persistence Behavior

No runtime state is stored. Message IDs are part of the logging ABI and should remain stable.

## Dependencies and Integration Points

It includes `glfs-message-id.h` and uses `GLFS_COMPONENT` and `GLFS_NEW` macros.

## Risks and Edge Cases

The comment notes that message IDs should not be removed or reused. The closing guard comment names `__NL_CACHE_MESSAGES_H__`, which is stale but harmless.

## Test Signals

Compile structured logging and verify logs include host and errno fields for invalid failover host and failover submission failure cases.
