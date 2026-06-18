# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedundantEditLogInputStream.java

Purpose: Unit-tests failover behavior in `RedundantEditLogInputStream.nextOp()` when the first edit stream fails during `skipUntil`. It verifies both logging and successful operation retrieval from the next stream.

Important APIs and functions: The test mocks two `EditLogInputStream` instances with Mockito, configures names and txid ranges, makes the first `skipUntil(1)` throw, makes the second skip succeed and `readOp()` return a `MkdirOp`, and captures `RedundantEditLogInputStream.LOG`.

Control flow: A `RedundantEditLogInputStream` is constructed with the mocked stream list and starting txid 1. `nextOp()` attempts the first stream, logs the skip failure and failover, switches to the second stream, reads an operation, and returns it.

State and persistence behavior: No real edit files are persisted. The state under test is the redundant stream's current active stream selection and txid positioning over mocked streams.

Dependencies and integration points: Depends on `FSEditLogOp.MkdirOp`, `EditLogInputStream`, Mockito, and `GenericTestUtils.LogCapturer`. This is a low-level test for NameNode edit-log recovery from multiple storage directories.

Risks: If failover logging changes text, this test may fail despite behavior being correct. Raw `ArrayList` use is unchecked but harmless. It only covers failure during skip, not read failures after partial reads.

Test signals: Passing requires the expected log messages mentioning `FAKE_STREAM0` failover to `FAKE_STREAM1` and identity equality of the returned edit operation.
