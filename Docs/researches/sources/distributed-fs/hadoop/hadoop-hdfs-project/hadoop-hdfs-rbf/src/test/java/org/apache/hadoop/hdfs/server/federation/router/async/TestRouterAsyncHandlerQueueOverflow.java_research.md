# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncHandlerQueueOverflow.java

Purpose: validates that a saturated per-namespace async handler queue fails predictably instead of blocking unboundedly.

Important APIs/types/functions: `MiniRouterDFSCluster`, `RouterAsyncRpcClient`, `RouterRpcServer.getAsyncExecutorForNamespace`, `RouterAsyncRpcFairnessPolicyController`, config keys for queue size, handler/responder counts, fairness timeout, max async-call permits, `FSNamesystem`, `NameNodeAdapterMockitoUtil`, `CountDownLatch`, `ThreadPoolExecutor`, `RemoteMethod`, `OpenFilesIterator`, `LambdaTestUtils`, and `syncReturn`.

Control flow: setup starts a two-nameservice HA cluster with active/standby/observer NNs, configures async queue capacity to 2 with single handlers/responders and one async permit, spies an NN `FSNamesystem` method (`getFilesBlockingDecom`) to wait on a latch for `/veryBigOperation`, then creates an async client. The test sends one call downstream, another blocked at permit acquisition, two queued calls, and a fifth call that should be rejected. `syncReturn` is expected to throw `StandbyException` with a busy-namespace message. The latch is released so the test can terminate.

State and persistence behavior: no file state is central; the state is executor queue size, completed-task count, permits, and the latch-blocked NN method. Integration points include router fairness, per-namespace async executors, NN protocol invocation, and rejection-to-exception mapping. Risks are timing sensitivity and a mocked namesystem lock. Test signals are executor queue sizes, completed task counts, timeout-bounded completion, and exact busy exception text.
