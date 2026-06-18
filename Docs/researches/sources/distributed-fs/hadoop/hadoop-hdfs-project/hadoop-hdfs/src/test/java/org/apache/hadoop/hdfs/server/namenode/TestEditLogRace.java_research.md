# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestEditLogRace.java

## Purpose
`TestEditLogRace` exercises race-prone NameNode edit-log operations under concurrent namespace mutation, log rolling, safe mode, saveNamespace, and async edit-log queue pressure. Like other edit-log suites, it is parameterized over synchronous and asynchronous edit logging.

## Important APIs, Types, And Functions
The class uses `MiniDFSCluster`, `NamenodeProtocols`, `FSNamesystem`, `FSImage`, `FSEditLog`, `FSEditLogAsync`, `EditLogFileInputStream`, `FSEditLogLoader`, `JournalSet.JournalAndStream`, `EditLogFileOutputStream`, `SafeModeAction`, `RwLockMode`, and `SubjectInheritingThread`. The internal `Transactions` worker repeatedly creates and deletes directories through both `FileSystem` and direct NameNode RPC. `verifyEditLogs` replays every edit log copy for a segment and asserts all journals contain the same number of readable edits.

## Control Flow
`testEditLogRolling` starts 16 transaction workers and rolls logs 30 times, verifying each finalized segment and the next in-progress segment. `testSaveNamespace` performs repeated safe-mode enters and namespace saves while workers mutate the namespace, checking pre-save in-progress edits and post-save finalized edits. `testSaveImageWhileSyncInProgress` spies on stream flush to block a writer in the unsynchronized `logSync` section, then asserts entering safe mode waits for the flush before saving. `testSaveRightBeforeSync` logs an edit under the write lock but sleeps before `logSync`; entering safe mode should call `logSyncAll` and avoid waiting for the sleeping thread. `testDeadlock` congests the async edit queue with spammers, blocks a specific edit operation, then starts a synchronized edit/logSync path to prove queue-full and monitor-lock interactions do not deadlock.

## State And Persistence Behavior
The tests inspect finalized and in-progress edit segment files in the NameNode storage directory, replay them from expected txids, and compare counts across journal copies. They validate the invariant that saveNamespace finalizes all edits up to the checkpoint txid and creates a new in-progress segment containing only the begin transaction. The deadlock test uses last-written txid stagnation as the signal that the async queue is full before releasing the blocked operation.

## Dependencies And Integration Points
This suite integrates concurrency primitives (`CountDownLatch`, `Semaphore`, `Future`, `AtomicReference`, `AtomicBoolean`), NameNode safe mode, edit-log internals, RPC mutation paths, storage files, and async edit queue behavior. It uses Mockito spies and argument matchers to create deterministic stalls inside normally fast code paths.

## Risks And Test Signals
The highest risks are corruption during log rolls, saveNamespace racing with in-flight sync, incorrectly waiting or not waiting when entering safe mode, and deadlocks between synchronized callers and async queue backpressure. Test signals are successful replay of every segment, expected wait-time comparisons around `BLOCK_TIME`, checkpoint txid alignment with last-written txid, completion of futures under timeout, and absence of worker-captured exceptions.
