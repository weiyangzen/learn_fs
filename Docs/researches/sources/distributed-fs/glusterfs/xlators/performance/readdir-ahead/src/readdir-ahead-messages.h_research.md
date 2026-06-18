# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/readdir-ahead-messages.h

## Purpose
Declares stable log message IDs for the readdir-ahead translator.

## Important APIs, Types, And Functions
`GLFS_MSGID(READDIR_AHEAD, ...)` defines IDs for child and volume misconfiguration, allocation failure, directory release with a pending stub, out-of-sequence prefetch, and dictionary operation failure.

## Control Flow
The implementation logs these IDs during init, prefetch callback validation, release, and memory/dict error paths.

## State And Persistence
No runtime state. IDs must remain append-only to preserve log compatibility.

## Dependencies And Integration Points
Includes `glusterfs/glfs-message-id.h` and relies on the `READDIR_AHEAD` component.

## Risks
Changing message order or deleting IDs breaks stable diagnostics. Missing IDs can force generic logs for important corruption paths such as out-of-sequence directory preload.

## Test Signals
Misconfiguration, OOM injection, and forced out-of-sequence prefetch tests should emit these IDs.
