# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeRpcServer.java

## Purpose
`JournalNodeRpcServer` is the protobuf RPC front door for a JournalNode. It implements both `QJournalProtocol` for NameNode-to-JournalNode quorum journal operations and `InterQJournalProtocol` for JournalNode-to-JournalNode sync/recovery reads.

## Important APIs and types
The constructor builds an `RPC.Server` using `QJournalProtocolPB`, `QJournalProtocolServerSideTranslatorPB`, `InterQJournalProtocolPB`, and `InterQJournalProtocolServerSideTranslatorPB`. Lifecycle methods are `start()`, `join()`, `stop()`, and `getAddress()`. Protocol methods include journal formatting, epoch negotiation, journaling, log segment start/finalize/purge, recovery prepare/accept, manifest retrieval, storage info retrieval, edit cache reads, upgrade/rollback/finalize helpers, and inter-JournalNode manifest retrieval.

## Control flow
Construction copies the configuration, forces TCP_NODELAY for low-latency IPC, resolves the configured RPC bind address, validates the handler count, creates the main QJournal protobuf service, and adds the inter-Journal protocol to the same server. Most protocol methods are thin dispatchers: they resolve the target journal via `jn.getOrCreateJournal(journalId, nameServiceId)` and delegate to `Journal` or `JournalNode` methods. Manifest responses are wrapped with converted protobuf manifests plus HTTP port/URL so clients can download edit logs over HTTP.

## State and persistence
The server owns the RPC listener and configured handler count. Persistent journal state is owned by `Journal`, `JNStorage`, and `JournalNode`; this class only routes operations that mutate that state. It marks `NewerTxnIdException` and `JournaledEditsCache.CacheMissException` as terse exceptions to keep expected read-miss paths from producing noisy RPC logs.

## Dependencies and integration points
It integrates with Hadoop IPC, protobuf RPC engine 2, `HDFSPolicyProvider` for service ACLs, JournalNode HTTP serving, QJM protobuf translators, and storage protocol types such as `NamespaceInfo`, `StorageInfo`, `RemoteEditLogManifest`, and `SegmentStateProto`. It also attaches the JournalNode tracer to the RPC server.

## Risks and edge cases
Misconfigured or nonpositive handler counts are corrected to the default, but an incorrect bind host or address can still prevent service startup. Since most methods create journals on demand, malformed IDs can create unexpected local journal directories. The server exposes powerful upgrade and rollback operations, so service authorization must be enabled correctly in secure deployments.

## Test signals
Tests should cover handler count validation, bind address resolution, service ACL refresh under authorization, terse exception registration, protocol delegation for each Journal operation, manifest response URL/port fields, and inter-JournalNode service availability on the same RPC server.
