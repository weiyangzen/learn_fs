# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.c

## Purpose
Provides synchronous helper calls for downloading cluster topology from a management node and for dropping node-store connections.

## Important APIs and control flow
`NodesTk_downloadNodes` sends `GetNodesMsg`, parses `GetNodesRespMsg` into a caller-owned `NodeList`, and optionally returns root owner ID and mirror state. `NodesTk_downloadTargetMappings` sends `GetTargetMappingsMsg` and splices response mappings into a caller list. `NodesTk_downloadStatesAndBuddyGroups` sends `GetStatesAndBuddyGroupsMsg` with local node ID, then splices target states and buddy groups from the response. All request helpers use `RequestResponseArgs_prepare` and silence retry/connection logs in non-debug builds. `NodesTk_dropAllConnsByStore` iterates a `NodeStoreEx` and disconnects available streams from each node pool.

## State, dependencies, integration
The file depends on BeeGFS network messages, `MessagingTk`, `NodeStoreEx`, `NodeConnPool`, and Linux list splicing. `InternodeSyncer` uses these helpers for node sync, mapping sync, and target-state refresh.

## Risks and test signals
Callers own parsed nodes and spliced list elements. Failed communication leaves output lists untouched except for any caller initialization. Test response parsing, log flag behavior, list ownership after `RequestResponseArgs_freeRespBuffers`, and connection drop iteration with node references.
