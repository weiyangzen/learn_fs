# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/SpyQJournalUtil.java

Purpose: Utility for creating a spy-backed `QuorumJournalManager` and stubbing `getJournaledEdits` behavior on its `AsyncLogger` instances.

Important APIs/types/functions: `createSpyingQJM(...)`, `mockJNWithEmptyOrSlowResponse(...)`, `spyGetJournaledEdits(...)`, `AsyncLogger.Factory`, `IPCLoggerChannel`, `DirectExecutorService`, Mockito spies, `Semaphore`, and `GetJournaledEditsResponseProto`.

Control flow: `createSpyingQJM` creates `IPCLoggerChannel` loggers whose executor is a `DirectExecutorService`, then wraps each logger in a Mockito spy. `mockJNWithEmptyOrSlowResponse` makes JN0 return an empty response, JN1 call through normally, and JN2 block behind a semaphore. `spyGetJournaledEdits` wraps the real method with a caller-provided pre-hook.

State and persistence behavior: No durable state. Semaphore state coordinates mocked asynchronous responses inside a test.

Dependencies and integration points: Used by QJM client tests needing real IPC behavior plus observable RPC calls. It depends on `getLoggerSetForTests()` and `QJM_RPC_MAX_TXNS_DEFAULT`.

Risks: Stubs are exact on txid and max-txn arguments, so selection changes can bypass mocks. Slow-response tests can deadlock if expected calls do not occur.

Test signals: Enables tests proving QJM can select edits despite empty, slow, or abnormal JournalNode responses.
