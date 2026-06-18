# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/TestEpochsAreUnique.java

Purpose: Validates that QJM writer epochs are unique and strictly increasing with and without intermittent JournalNode RPC failures.

Important APIs/types/functions: `QuorumJournalManager.createNewUniqueEpoch()`, `AsyncLogger.getJournalState()`, `AsyncLogger.newEpoch(long)`, `FaultyLoggerFactory`, `SometimesFaulty<T>`, `MiniJournalCluster`, and `NamespaceInfo`.

Control flow: The test formats a MiniJournalCluster, then creates five sequential QJMs and asserts epochs 1 through 5. It then repeatedly creates QJMs with random failures injected into `getJournalState` and `newEpoch`; failures are expected until a quorum succeeds. Every successful epoch must be greater than the previous successful epoch, even if values skip.

State and persistence behavior: Epoch promises are persisted by JournalNodes and observed by later QJMs. Random fault state is in-memory test behavior.

Dependencies and integration points: Exercises epoch election against real JournalNodes using `IPCLoggerChannel` spies and quorum semantics.

Risks: Random injection can make failures expected and triage harder. The correctness risk is epoch reuse after partial promise acceptance.

Test signals: Passing proves QJM never reuses old epochs and can safely skip ahead after faulted attempts.
