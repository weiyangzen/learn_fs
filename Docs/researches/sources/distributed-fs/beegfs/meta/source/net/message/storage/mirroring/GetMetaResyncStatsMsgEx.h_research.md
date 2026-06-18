<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.h

## Purpose
Declares the metadata resync statistics request handler.

## Important APIs, Types, and Functions
`GetMetaResyncStatsMsgEx` inherits `GetMetaResyncStatsMsg` and overrides `processIncoming()`.

## Control Flow, State, and Persistence
The declaration represents a non-mutating query message with no local state.

## Dependencies and Integration Points
Includes the common stats request message and is wired into metadata mirroring message dispatch.

## Risks and Test Signals
Header-level risk is low; tests should focus on implementation behavior and wire response compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.h -->
