<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h

## Purpose
Declares the resync-started notification handler.

## Important APIs, Types, and Functions
`StorageResyncStartedMsgEx` inherits `StorageResyncStartedMsg`, has a default constructor, overrides `processIncoming()`, and uses private `pauseWorkers()`.

## Control Flow, State, and Persistence
The declaration identifies an in-memory synchronization/control message, not a mirrored metadata mutation itself.

## Dependencies and Integration Points
Includes the common resync-started message and is used by resync orchestration before raw metadata transfer.

## Risks and Test Signals
Tests should focus on ensuring `pauseWorkers()` is invoked only for the intended local target and that response behavior is compatible with callers waiting for resync readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->
