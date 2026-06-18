# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/MockResolver.java

## Purpose
`MockResolver` is an in-memory implementation of both `ActiveNamenodeResolver` and `FileSubclusterResolver`. It gives router tests a controllable substitute for state-store-backed membership and mount-table resolution.

## Important APIs, Types, and Functions
The class exposes `addLocation()`, `removeLocation()`, `cleanRegistrations()`, `setDisableRegistration()`, namespace disable helpers, `registerNamenode()`, `getNamespaces()`, `getDestinationForPath()`, `getMountPoints()`, and `getDefaultNamespace()`. `MockNamenodeContext` implements `FederationNamenodeContext` with RPC, service, lifeline, web, nameservice, namenode, state, and modification timestamp fields.

## Control Flow
Mounts are stored by source path. Destination lookup sorts mount keys in reverse order and uses the first prefix match, appending unmatched path suffixes to each `RemoteLocation`. Namenode registration converts a `NamenodeStatusReport` into `MockNamenodeContext`, inserts or replaces by `getNamenodeKey()`, aliases the same list under both nameservice and block-pool ids, and sorts by `NamenodePriorityComparator`. State update methods find a matching RPC address and resort the nameservice list. Observer reads split observer and non-observer memberships, shuffle observers, sort non-observers, and return an immutable list.

## State and Persistence
All state is process-local: `resolver` maps nameservice/block-pool ids to membership lists, `locations` maps mount paths to remote destinations, `namespaces` holds `FederationNamespaceInfo`, and disabled/default namespace flags simulate availability. There is no persistence and no state-store synchronization.

## Dependencies and Integration Points
It integrates with router tests through the same resolver interfaces as production resolvers. Constructors accept `Configuration`, `StateStoreService`, or `Router` for dependency-injection compatibility but ignore them. It depends on `RemoteLocation`, `PathLocation`, `NamenodeStatusReport`, namespace info records, and Hadoop `Time`.

## Risks and Test Signals
`removeLocation()` removes the entire mount key before removing the target from the old list, which is intentionally simple but can surprise tests with multi-destination mounts. `getNamenodesForBlockPoolId()` assumes a non-null list. The path matching is prefix-based, so tests relying on exact path component boundaries should use the production resolver. Test signals are deterministic registration ordering, disabled namespace filtering, default namespace empty-string behavior, and path-to-remote suffix translation.
