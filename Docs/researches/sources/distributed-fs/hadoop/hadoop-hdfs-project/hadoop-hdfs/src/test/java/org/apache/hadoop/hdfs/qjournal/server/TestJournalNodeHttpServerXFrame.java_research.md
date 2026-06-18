# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeHttpServerXFrame.java

Purpose: Tests that JournalNode HTTP responses honor the HDFS X-Frame-Options configuration.

Important APIs/types/functions: `MiniJournalCluster`, `JournalNode.getHttpServerURI()`, `DFS_XFRAME_OPTION_ENABLED`, `HttpServer2.XFrameOption.SAMEORIGIN`, and `HttpURLConnection`.

Control flow: Each test starts a one-node MiniJournalCluster with X-Frame enabled or disabled, connects to the JournalNode root URI, and inspects the `X-FRAME-OPTIONS` header. Cleanup shuts down the cluster.

State and persistence behavior: No edit-log persistence is relevant; state is HTTP server configuration at startup.

Dependencies and integration points: JournalNode HTTP server construction and Hadoop HTTP security header config.

Risks: Incorrect headers can weaken clickjacking protections or break deployments expecting disabled behavior.

Test signals: Passing confirms enabled clusters send SAMEORIGIN and disabled clusters omit the header.
