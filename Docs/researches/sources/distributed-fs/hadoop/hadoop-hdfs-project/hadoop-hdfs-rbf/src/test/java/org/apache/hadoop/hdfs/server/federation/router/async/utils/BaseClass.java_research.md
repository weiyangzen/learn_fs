# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/BaseClass.java

Purpose: common interface for the synchronous and asynchronous utility classes used to test `AsyncUtil` conversion patterns.

Important APIs/types/functions: declares `applyMethod(int)`, `applyMethod(int, boolean)`, `exceptionMethod(int)`, `forEachMethod(List<Integer>)`, `forEachBreakMethod(List<Integer>)`, `forEachBreakByExceptionMethod(List<Integer>)`, `applyThenApplyMethod(int)`, `applyCatchThenApplyMethod(int)`, `applyCatchFinallyMethod(int, List<String>)`, and `currentMethod(List<Integer>)`. Exception signatures allow IO failures in methods that model checked-exception paths.

Control flow: the interface itself has no implementation; its role is to let `TestAsyncUtil` run the same semantic checks against `SyncClass` and `AsyncClass` depending on execution mode.

State and persistence behavior: no state or persistence. Dependencies are only Java `IOException` and `List`. Integration points are local test utility classes rather than production router code. Risks are contract drift: if `SyncClass` and `AsyncClass` diverge while still satisfying the interface, tests must catch behavioral differences. Test signals are indirect through parameterized `TestAsyncUtil` coverage over both implementations.
