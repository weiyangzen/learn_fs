# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterQJournalProtocol.proto

## Purpose

`InterQJournalProtocol.proto` defines JournalNode-to-JournalNode or internal qjournal RPCs used to fetch edit-log manifests and storage information. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.qjournal`, Java outer class `InterQJournalProtocolProtos`, generic services, and imports `HdfsServer.proto` and `QJournalProtocol.proto`. It defines `GetStorageInfoRequestProto` with `JournalIdProto jid` and optional `nameServiceId`. The service `InterQJournalProtocolService` exposes `getEditLogManifestFromJournal(GetEditLogManifestRequestProto)` and `getStorageInfo(GetStorageInfoRequestProto)`.

## Control Flow

The service reuses the qjournal manifest request/response schema for manifest retrieval and adds a storage-info lookup. Callers identify a journal and optionally a nameservice, then receive either the manifest of edit-log segments or `StorageInfoProto`.

## State and Persistence Behavior

The proto describes access to JournalNode storage state and edit-log segment metadata. Implementations read local journal storage, but this schema does not itself persist data.

## Dependencies and Integration Points

It depends on qjournal request types and shared HDFS server storage information. It integrates with JournalNode synchronization, recovery, bootstrap, and remote manifest inspection.

## Risks and Edge Cases

Because it imports and reuses `QJournalProtocol.proto` types, compatibility changes in qjournal manifest messages affect this internal protocol too. Optional nameservice IDs must be handled correctly for federated or multi-nameservice journal directories.

## Test Signals

Tests should cover manifest retrieval from a journal, storage info retrieval, absent nameservice IDs, federated journal IDs, and compatibility when optional qjournal fields are absent.
