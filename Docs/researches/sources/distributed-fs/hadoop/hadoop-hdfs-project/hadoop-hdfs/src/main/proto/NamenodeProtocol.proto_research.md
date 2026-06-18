# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/NamenodeProtocol.proto

## Purpose

`NamenodeProtocol.proto` defines the private stable RPC contract used by subordinate NameNodes, checkpointing nodes, balancers, and related internal clients to communicate with the active/primary NameNode. The source was read as a complete 327-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.namenode`, Java outer class `NamenodeProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Messages cover block selection (`GetBlocksRequestProto`, `GetBlocksResponseProto`), block-token keys, transaction IDs, edit-log rolling, checkpoint transaction IDs, NameNode-file transaction IDs, error reports, subordinate NameNode registration, checkpoint start/end, edit-log manifests, upgrade state, rolling-upgrade state, file path lookup, and Storage Policy Satisfier path retrieval. `NamenodeProtocolService` exposes RPCs for those operations.

## Control Flow

Clients request blocks for balancing or movement, fetch block keys, query the latest edit-log/checkpoint transaction IDs, roll edit logs for checkpointing, get version information, report subordinate errors, register subordinate NameNodes, begin and end checkpoints using checkpoint signatures, fetch edit-log manifests since a transaction ID, query upgrade/rolling-upgrade state, and fetch the next SPS path. Some messages, such as `GetFilePathRequestProto`, are defined without a corresponding service method in this file segment, which may indicate use by translators elsewhere or legacy/dead schema.

## State and Persistence Behavior

The protocol observes and drives NameNode metadata state: block maps, block-token keys, edit-log transaction IDs, checkpoint signatures, upgrade flags, and SPS queues. Checkpoint and edit-log operations affect persistent namespace recovery material through NameNode implementation code.

## Dependencies and Integration Points

It integrates with balancer/block movement, block-token secret management, checkpointing, BackupNode/secondary NameNode workflows, edit-log rolling, storage upgrade/rolling-upgrade logic, and SPS. It imports shared server structures from `HdfsServer.proto`.

## Risks and Edge Cases

Defaults such as `minBlockSize = 10485760` in `GetBlocksRequestProto` are explicitly for rolling upgrades and should not be changed casually. Required checkpoint/edit-log fields must match NameNode persistent state exactly. Missing optional SPS path means no path is available, not necessarily an error. Unused or unmatched messages need caution because generated APIs may still be consumed elsewhere.

## Test Signals

Tests should cover balancer get-block requests with defaults and optional filters, block-key retrieval, transaction/checkpoint ID queries, edit-log rolling, checkpoint start/end signatures, manifest retrieval, upgrade/rolling-upgrade flags, SPS path behavior, and mixed-version request decoding.
