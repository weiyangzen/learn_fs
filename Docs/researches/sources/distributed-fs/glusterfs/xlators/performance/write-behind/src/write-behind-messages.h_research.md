# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/write-behind-messages.h

## Purpose
Declares stable log message IDs for the write-behind translator.

## Important APIs, Types, And Functions
`GLFS_MSGID(WRITE_BEHIND, ...)` defines IDs for size/config errors, init failure, invalid argument, memory failure, missing size, volume misconfiguration, unavailable resources, and pass-through warnings.

## Control Flow
`write-behind.c` emits these IDs during init/reconfigure, request refcount anomalies, iobref failures, and memory accounting failures.

## State And Persistence
No runtime state. IDs are stable operational identifiers and should be append-only.

## Dependencies And Integration Points
Includes `glusterfs/glfs-message-id.h` and uses the `WRITE_BEHIND` component.

## Risks
Changing IDs disrupts log tooling. Missing message IDs for queue corruption or sync errors would make field diagnosis harder.

## Test Signals
Invalid `aggregate-size`/`cache-size`, pass-through reconfigure, OOM injection, and refcount error paths should log under these IDs.
