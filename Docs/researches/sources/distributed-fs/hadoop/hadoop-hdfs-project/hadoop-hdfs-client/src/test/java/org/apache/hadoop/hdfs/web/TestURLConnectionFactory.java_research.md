## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestURLConnectionFactory.java

Purpose: this test covers `URLConnectionFactory` connection customization, SSL initialization failure logging, and SSLFactory monitor thread cleanup when an `swebhdfs` filesystem is closed.

Important APIs and types: it uses `URLConnectionFactory`, `ConnectionConfigurator`, `SSLFactory`, `KeyStoreTestUtil`, `FileSystem.get()`, `FileUtil`, and the SSL reload thread name constant `SSL_MONITORING_THREAD_NAME`.

Control flow: `testConnConfiguratior()` opens an HTTP connection and verifies the configurator sees the expected URL and stores the connection. `testSSLInitFailure()` configures an invalid hostname verifier and asserts the factory logs SSL configuration failure. `testSSLFactoryCleanup()` sets up test keystores, opens an `swebhdfs://localhost` filesystem, finds the SSL monitor thread in the root thread group, closes the filesystem, and waits for the reloader thread to stop.

State and persistence: temporary keystore/config files are created under a test path and removed before setup. Runtime state includes the connection list, captured logs, filesystem instance, and SSL monitoring thread.

Dependencies and integration points: integrates WebHDFS URL connection factory, Hadoop SSL configuration reload support, filesystem scheme registration for `swebhdfs`, and thread lifecycle cleanup on `FileSystem.close()`.

Risks: thread enumeration can be brittle if multiple SSL monitor threads exist or thread names change. Cleanup waits up to ten seconds and is timing-sensitive.

Test signals: verifies configurators are applied, SSL init failures are logged instead of fatal, and SSL reloader resources do not leak after closing the secure WebHDFS filesystem.
