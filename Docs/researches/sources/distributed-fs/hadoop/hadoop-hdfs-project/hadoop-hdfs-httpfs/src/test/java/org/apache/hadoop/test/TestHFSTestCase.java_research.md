# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHFSTestCase.java

Purpose: Self-tests for the HTTPFS test harness: directory, Jetty, HDFS, wait/sleep helpers, and expected-exception annotation behavior.

Important APIs/types/functions: tests for missing annotations, `testDirAnnotation`, `waitFor`, `waitForTimeOutRatio1/2`, `sleepRatio1/2`, `testHadoopFileSystem`, `MyServlet`, `testJetty`, and `testException0/1`.

Control flow: negative tests call helper getters without annotations and expect `IllegalStateException`. Directory/HDFS/Jetty tests use the relevant annotations to prove helpers are available, create/read a file in MiniDFS, and serve a simple servlet through Jetty. Timing tests validate `waitFor` and `sleep` respect wait ratios. Expected-exception tests throw runtime exceptions matching annotation requirements.

State and persistence: uses extension-provided local dirs, Jetty server, and MiniDFS. The servlet writes simple response content; HDFS test creates a file under the HDFS test dir.

Dependencies/integration: `HFSTestCase`, `TestDirHelper`, `TestJettyHelper`, `TestHdfsHelper`, `TestExceptionHelper`, Jetty servlet APIs, Hadoop `FileSystem`, and `Time`.

Risks and test signals: valuable infrastructure regression coverage. Timing assertions use fixed tolerances and may be sensitive on overloaded machines. The `sleepRatio2` test sets ratio to 1 despite its name, so it does not actually validate a ratio of 2.
