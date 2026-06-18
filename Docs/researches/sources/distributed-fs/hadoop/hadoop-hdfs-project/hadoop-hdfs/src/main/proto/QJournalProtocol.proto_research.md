# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/QJournalProtocol.proto

## Purpose

`QJournalProtocol.proto` defines the private stable quorum journal protocol used by NameNodes and JournalNodes for high-availability edit-log storage. It covers journal identity, epochs, formatting, upgrade/rollback, writing edits, segment lifecycle, manifest retrieval, tailing journaled edits, and Paxos-style recovery. The source was read as a complete 390-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.qjournal`, Java outer class `QJournalProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Important messages include `JournalIdProto`, `RequestInfoProto`, `SegmentStateProto`, `PersistedRecoveryPaxosData`, journal/heartbeat/start/finalize/purge messages, format and upgrade messages, rollback messages, journal state and epoch messages, edit-log manifest and journaled-edits messages, and `PrepareRecovery`/`AcceptRecovery` messages. `QJournalProtocolService` exposes operations from `isFormatted` through `acceptRecovery`.

## Control Flow

The qjournal lifecycle starts with format or storage inspection, then `newEpoch` establishes a writer epoch. A NameNode sends `journal` requests with request info, first transaction ID, transaction count, serialized records, and segment transaction ID. It starts and finalizes log segments, purges old logs, heartbeats to maintain writer state, queries manifests, tails journaled edits, and uses `prepareRecovery`/`acceptRecovery` to converge on a valid segment after failures. Upgrade, finalize, rollback, and discard RPCs manage JournalNode storage across software/layout changes.

## State and Persistence Behavior

This schema is persistence-critical. `PersistedRecoveryPaxosData` is explicitly the on-disk format for accepted recovery decisions. JournalNodes persist edit-log records, segment state, epochs/promises, storage info, and recovery metadata. `RequestInfoProto` carries epoch and IPC serial number to reject stale or replayed writers, and optionally carries committed transaction ID and nameservice ID.

## Dependencies and Integration Points

It integrates with QuorumJournalManager, JournalNode storage, NameNode edit log writing/tailing, HA failover, edit-log segment recovery, shared `RemoteEditLogManifestProto`, and storage upgrade logic. It is also imported by `InterQJournalProtocol.proto`.

## Risks and Edge Cases

Epoch, IPC serial number, and committed transaction ID semantics are central to split-brain protection. Required fields in recovery and segment messages must remain compatible. Deprecated `httpPort` fields are still required in some responses, so translators must populate them even when `fromURL` is preferred. Nameservice ID spelling differs between `nameServiceId` and `nameserviceId` in one rollback request, which is generated API surface. Recovery acceptance depends on fetching logs from `fromURL` safely.

## Test Signals

Tests should cover epoch fencing, journal writes and segment finalization, manifest and tail retrieval, purge/discard behavior, format/upgrade/rollback/finalize flows, prepare/accept recovery, persisted Paxos data compatibility, deprecated `httpPort`/`fromURL` behavior, and federated nameservice IDs.
