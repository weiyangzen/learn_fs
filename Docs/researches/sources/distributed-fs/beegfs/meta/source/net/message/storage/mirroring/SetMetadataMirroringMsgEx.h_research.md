<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.h

## Purpose
Declares the set-metadata-mirroring request handler and static root-mirroring helpers.

## Important APIs, Types, and Functions
`SetMetadataMirroringMsgEx` inherits `SetMetadataMirroringMsg`, overrides `processIncoming()`, exposes static `setMirroring()`, and declares private static `moveRootInode()` and `moveRootDirectory()`.

## Control Flow, State, and Persistence
The header makes `setMirroring()` callable outside the network request path, which is used by raw inode resync. Persistent mutation details are in the implementation.

## Dependencies and Integration Points
Includes common storage errors and the set-mirroring request message. It is a control-plane integration point for root metadata mirroring.

## Risks and Test Signals
The exposed static API should be tested both through the message and direct resync bootstrap path to ensure identical state transitions and locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.h -->
