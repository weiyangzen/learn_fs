<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.h

## Purpose
Declares the legacy link-owner lookup message extension.

## Important APIs, Types, and Functions
`FindLinkOwnerMsgEx` inherits `FindLinkOwnerMsg` and overrides only `processIncoming()`.

## Control Flow, State, and Persistence
The declaration identifies a synchronous, non-mirrored read-only response path with no helper state.

## Dependencies and Integration Points
Includes common find-link-owner request and response messages. Dispatch integration is through the standard message extension mechanism.

## Risks and Test Signals
Because the header exposes no locking or mirror awareness, tests should focus on behavior in the implementation and on compatibility with old management-tool requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.h -->
