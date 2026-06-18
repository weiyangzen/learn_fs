# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalNodeSyncer.java

## Purpose
`JournalNodeSyncer` is a background repair daemon for a single JournalNode journal. It periodically contacts peer JournalNodes, compares finalized edit-log manifests, and downloads missing finalized segments into local storage.

## Important APIs and types
Key lifecycle methods are `start(String nsId)`, `stopSync()`, and `isJournalSyncerStarted()`. Important helpers include `getOtherJournalNodeProxies()`, `startSyncJournalsDaemon()`, `formatWithSyncer()`, `syncWithJournalAtIndex()`, `getMissingLogList(...)`, and `downloadMissingLogSegment(...)`. The nested `JournalNodeProxy` wraps an `InterQJournalProtocol` RPC proxy and lazily caches the peer HTTP base URL.

## Control flow
Startup optionally updates the nameservice ID, discovers peer JournalNode addresses from shared-edits configuration, creates inter-Journal RPC proxies, and starts a daemon once. The daemon waits for local formatting; if enabled, it can format from another JournalNode's storage info only after confirming the peer has edit logs, avoiding a race with fresh NameNode formatting. During steady state it creates the `edits.sync` directory, round-robins peers, obtains local and remote manifests, computes missing finalized log segments by comparing start transaction IDs, and downloads each missing segment over HTTP. Downloads go to temporary storage first and are then moved into the current directory with `journal.moveTmpSegmentToCurrent`.

## State and persistence
Runtime state includes `shouldSync`, daemon reference, peer proxies, the current peer index, and whether the daemon started. Persistent effects are local journal formatting and finalized edit-log segment files under `JNStorage`. Temporary files live under the storage sync/current temp paths and are cleaned on shutdown or failed download. Metrics increment via `JournalMetrics.incrNumEditLogsSynced()` after a successful move.

## Dependencies and integration points
The syncer depends on `Journal`, `JournalNode`, `JNStorage`, QJournal inter-node RPC, `GetJournalEditServlet` URL construction, `Util.doGetUrl` transfer logic, secure `doAsLoginUser` execution, optional Kerberos relogin, `DataTransferThrottler`, shared-edits URI parsing, and JournalNode HTTP servers.

## Risks and edge cases
Peer discovery has several configuration fallbacks and can fail if nameservice-specific shared edits URIs disagree. The missing-log comparison assumes sorted manifest lists and compares by start transaction ID, not full segment identity. Formatting from peers is intentionally conservative but still powerful: a wrong peer or nameservice ID could format local storage incorrectly. HTTP host rewriting uses the RPC peer host with the manifest URL scheme/port, which matters behind proxies or unusual bind addresses. Partial downloads must be deleted or later sync attempts may see stale temp files.

## Test signals
Tests should exercise peer address exclusion for the local JournalNode, nameservice-specific config fallback, startup idempotence, formatting disabled/enabled behavior, empty peer manifests, sorted missing-log detection, successful and failed HTTP downloads, temp-file cleanup, throttler configuration, and daemon interruption during shutdown.
