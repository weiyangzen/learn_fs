# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalAppender.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalAppender.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalAppender.java

### Purpose
`RaftJournalAppender` submits serialized journal messages to the embedded Ratis log, either directly through the local `RaftServer` or through a remote `RaftClient` depending on configuration.

### Important APIs, Types, And Functions
`sendAsync(Message)` chooses local or remote submission. `sendLocalRequest()` builds a write `RaftClientRequest` with the Alluxio Raft group and `RaftJournalSystem.nextCallId()`. `sendRemoteRequest()`, `ensureClient()`, and `handleRemoteException()` manage a lazily created remote client and recycle it after `AlreadyClosedException`. `close()` closes the remote client.

### Control Flow
Local submission bypasses a Ratis client and calls `mServer.submitClientRequestAsync()`. Remote submission calls `mClient.async().send()` and converts connection-closed failures into client reset before rethrowing through `CompletionException`.

### State, Persistence, And Dependencies
The appender owns the optional remote `RaftClient`; persistent storage is Ratis' log. Dependencies include `RaftServer`, `RaftClient`, Ratis protocol IDs, Alluxio configuration `MASTER_EMBEDDED_JOURNAL_WRITE_REMOTE_ENABLED`, and logging helpers.

### Integration Points
`RaftJournalWriter` uses this for normal journal flushes, and `RaftJournalSystem` uses it for catch-up primary-start marker writes and manual checkpoint catch-up.

### Risks
Remote client creation is lazy but not synchronized beyond volatile assignment, so concurrent use could create extra clients if external callers are added. Local request fields must stay aligned with the fixed `RAFT_GROUP_ID`. Remote exception handling assumes `AlreadyClosedException` is the recoverable client-staleness signal.

### Test Signals
Cover local request construction, remote send success, remote `AlreadyClosedException` client reset, close idempotence with and without remote client, and propagation of async failures to `RaftJournalWriter.flush()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/raft/RaftJournalAppender.java -->
