<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.h

## Purpose
Declares the session-store resync message extension.

## Important APIs, Types, and Functions
`ResyncSessionStoreMsgEx` inherits `ResyncSessionStoreMsg` and overrides `processIncoming()`.

## Control Flow, State, and Persistence
The header exposes no lock or mirrored-message wrapper; the implementation controls replacement of the mirrored session store.

## Dependencies and Integration Points
Includes the common resync-session-store message. It is invoked by metadata buddy resync workflows.

## Risks and Test Signals
Behavioral tests should focus on implementation; the declaration’s main compatibility point is the inherited buffer-carrying message contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.h -->
