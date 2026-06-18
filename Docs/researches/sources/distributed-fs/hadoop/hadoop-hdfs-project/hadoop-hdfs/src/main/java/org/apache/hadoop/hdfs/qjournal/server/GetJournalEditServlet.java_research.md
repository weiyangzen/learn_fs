<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/GetJournalEditServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/GetJournalEditServlet.java

Purpose: HTTP servlet that serves local edit-log segment files to NameNodes and peer JournalNodes for streaming reads and recovery synchronization.

Important APIs/types/functions: `doGet`, `isValidRequestor`, `checkRequestorOrSendError`, `checkStorageInfoOrSendError`, and static `buildPath`. Query parameters are `jid`, `segmentTxId`, `storageInfo`, and `inProgressOk`.

Control flow: `doGet` reads configuration and query parameters, validates journal id, resolves the `Journal` from servlet context, checks security and namespace/cluster match, finds the requested edit file under synchronized `FileJournalManager`, sets transfer headers, opens the file, and streams it through `TransferFsImage` with optional throttling.

State and persistence behavior: It does not mutate journal state. It exposes finalized or in-progress edit-log files from `JNStorage` and protects against races with finalization by synchronizing on `FileJournalManager` while locating and opening the file.

Dependencies/integration: Registered by `JournalNodeHttpServer` at `/getJournal`; URLs are built by `IPCLoggerChannel`/`QuorumJournalManager`. Security integrates NameNode principals, SecondaryNameNode principal, and same-short-name JournalNode peer access.

Risks: Any thrown `Throwable` becomes an HTTP 500 and IOException; security fallback for peer JournalNodes uses short username matching because peer principals are not enumerated. Storage info is optional, so callers omitting it bypass namespace/cluster comparison.

Test signals: Servlet tests should cover allowed/rejected principals, namespace mismatch 403, missing segment 404, in-progress flag behavior, path URL encoding, transfer headers, throttling, and race behavior around finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/GetJournalEditServlet.java -->
