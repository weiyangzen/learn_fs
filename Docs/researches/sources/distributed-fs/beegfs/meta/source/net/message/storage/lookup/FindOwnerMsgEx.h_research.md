<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.h

## Purpose
Declares the metadata-owner path lookup extension.

## Important APIs, Types, and Functions
`FindOwnerMsgEx` inherits `FindOwnerMsg`, overrides `processIncoming()`, and uses private `findOwner(EntryInfoWithDepth*)` for normal non-root lookup.

## Control Flow, State, and Persistence
No persistent state is declared. The header documents a simple read-only message without mirrored replay or explicit locks.

## Dependencies and Integration Points
Includes storage definitions/errors, metadata toolkit/common types, and `MetaStore`. It is part of metadata routing and lookup dispatch.

## Risks and Test Signals
The important contract is the `EntryInfoWithDepth` result. Tests should assert that response depth and owner flags match traversal state across local and remote ownership boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.h -->
