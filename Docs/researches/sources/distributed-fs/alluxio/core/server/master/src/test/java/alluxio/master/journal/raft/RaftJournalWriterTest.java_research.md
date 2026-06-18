# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/journal/raft/RaftJournalWriterTest.java

Purpose: focused unit tests for `RaftJournalWriter` batching and flush behavior over a mocked `RaftJournalAppender`.

Important APIs/types/functions: uses `RaftJournalWriter`, `RaftJournalAppender.sendAsync`, Ratis `RaftClientReply`, `ClientId`, `RaftGroupMemberId`, `RaftGroupId`, and Alluxio journal protobuf entries. The setup returns a custom `CompletableFuture` whose `get` methods immediately return a successful Ratis reply.

Control flow: `writeAndFlush` writes ten mount entries and verifies no async send before explicit `flush`, one send after the first flush, no duplicate send on an empty second flush, then a second send after writing another entry. `writeTriggerFlush` reflectively lowers static `FLUSH_BATCH_SIZE` to 128 bytes, writes mount entries, and verifies automatic sends occur at least proportional to serialized path byte volume.

State and persistence behavior: state is in-memory writer buffer contents and appender invocation count. No real Raft log or durable journal is created.

Dependencies and integration points: integrates with Ratis reply construction enough for `RaftJournalWriter.flush` to see a successful append. Uses reflection to mutate a static final field and Mockito verification for batching behavior.

Risks: reflective mutation of `FLUSH_BATCH_SIZE` is JVM/version-sensitive. The byte estimate does not include full protobuf overhead, so the assertion is deliberately lower-bound. The mocked future reports `isDone=false` despite returning from `get`, which is acceptable for this writer path but not a complete async model.

Test signals: good signal for explicit flush idempotence and automatic batch-size flushing; does not cover append failures, close behavior, or sequence numbering.
