<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.h

## Purpose
Declares static stat and dynamic-attribute refresh helpers.

## Important APIs, Types, and Functions
`MsgHelperStat::stat()` returns `StatData` and optional parent node/entry IDs. `refreshDynAttribs()` refreshes and optionally persists dynamic attributes. Private `refreshDynAttribsSequential()` and `refreshDynAttribsParallel()` implement target communication strategies.

## Control Flow, State, and Persistence
The header exposes that stat may depend on storage target communication through refresh. `makePersistent` controls whether refreshed attributes are written to disk.

## Dependencies and Integration Points
Includes common types, `MetaStore`, and `MetadataEx`. Used by metadata stat and combined intent operations.

## Risks and Test Signals
Tests should check optional parent output pointer combinations and that refresh helpers are selected based on stripe pattern target count and mirror type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.h -->
