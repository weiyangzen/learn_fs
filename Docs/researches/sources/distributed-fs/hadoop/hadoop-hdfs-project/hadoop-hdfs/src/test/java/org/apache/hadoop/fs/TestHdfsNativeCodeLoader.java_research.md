<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHdfsNativeCodeLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHdfsNativeCodeLoader.java

Purpose: Checks whether native HDFS code loading is enforced when the test JVM requests it.
Important APIs/types/functions: `requireTestJni()` reads `require.test.libhadoop`; `testNativeCodeLoaded()` checks `NativeCodeLoader.isNativeCodeLoaded()`.
Control flow: If the property is absent or false, the test logs and returns. If required, it fails with `LD_LIBRARY_PATH` context when libhadoop is not loaded.
State and persistence behavior: No filesystem or cluster state; reads system properties and environment variables.
Dependencies and integration points: Integrates JUnit with Hadoop `NativeCodeLoader` and native-library test configuration.
Risks and edge cases: Behavior changes entirely based on a JVM property. Failure diagnostics depend on `LD_LIBRARY_PATH` rather than all native search paths.
Test signals: Signals are either a skip-like return when native code is optional or a hard failure when required native code is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHdfsNativeCodeLoader.java -->
