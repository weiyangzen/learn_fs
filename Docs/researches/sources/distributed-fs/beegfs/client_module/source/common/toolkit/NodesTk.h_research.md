# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.h

## Purpose
Declares node/topology download helpers and store connection cleanup.

## Important APIs and types
Exports `NodesTk_downloadNodes`, `NodesTk_downloadTargetMappings`, `NodesTk_downloadStatesAndBuddyGroups`, and `NodesTk_dropAllConnsByStore`. It uses `App`, `Node`, `NodeType`, `NodeList`, `NumNodeID`, `NodeStoreEx`, and kernel `list_head` outputs.

## State, dependencies, integration
The header has no state. Its functions integrate management-plane messages into `InternodeSyncer` and other component code that needs a refreshed local topology view.

## Risks and test signals
APIs return `bool` for communication success but do not encode partial parse details. Tests should initialize output lists before calls and verify cleanup rules for both success and failure.
