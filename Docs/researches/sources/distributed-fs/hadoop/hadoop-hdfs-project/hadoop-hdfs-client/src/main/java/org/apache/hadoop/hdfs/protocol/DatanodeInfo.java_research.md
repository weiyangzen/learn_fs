# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/DatanodeInfo.java

## Purpose
`DatanodeInfo` extends `DatanodeID` with runtime DataNode state returned to clients and admin tools: capacity, DFS/non-DFS/block-pool/cache usage, heartbeat and block-report timestamps, xceiver count, rack, upgrade domain, dependent hosts, software version, block count, and administrative state.

## APIs and Control Flow
The `AdminStates` enum covers normal, decommissioning, decommissioned, entering maintenance, and in maintenance. Methods compute usage percentages through `DFSUtilClient`, format detailed and compact reports, mutate admin state through decommission/maintenance methods, test stale heartbeat state with `Time.monotonicNow()`, and implement `Node` topology methods (`parent`, `level`, `networkLocation`). The nested `DatanodeInfoBuilder` creates complete instances from raw values or an existing node.

## State, Dependencies, and Integration
Most fields are mutable snapshots from NameNode heartbeat/block-report tracking. Rack location is normalized with `NodeBase.normalize`; report formatting uses `NetUtils`, `StringUtils`, and `Date`. Equality delegates to `DatanodeID`, so runtime metrics do not affect identity. `DatanodeInfoWithStorage`, reports from `ClientProtocol`, block locations, and admin commands all depend on this shape.

## Risks and Test Signals
The builder’s `setFrom()` comment says `numBlocks` must be set explicitly, but the method copies `lastBlockReport` fields and omits dependent hosts; copying semantics should be tested. `adminState == null` means normal, which is compact but can surprise serializers. Tests should cover percent calculations with zero capacity, stale detection using monotonic time, state transitions for maintenance/decommission, report text, topology parent/level behavior, and equality ignoring mutable metrics.
