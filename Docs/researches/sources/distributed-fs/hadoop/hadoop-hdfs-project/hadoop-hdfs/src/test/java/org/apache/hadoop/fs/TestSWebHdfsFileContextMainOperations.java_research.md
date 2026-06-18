<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSWebHdfsFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSWebHdfsFileContextMainOperations.java

Purpose: Runs the WebHDFS FileContext main-operation suite over HTTPS (`swebhdfs`).
Important APIs/types/functions: `TestSWebHdfsFileContextMainOperations` extends `TestWebHdfsFileContextMainOperations`; overrides class setup, `createFileContextHelper()`, `getWebhdfsUrl()`, and teardown.
Control flow: Setup creates temporary SSL keystores, configures HTTPS-only HDFS endpoints on random localhost ports, starts two Datanodes, builds an `swebhdfs://` URI from the NameNode HTTPS address, and binds FileContext to it.
State and persistence behavior: State includes temporary keystore/config directories, static cluster, static HTTPS URI, and inherited FileContext test namespace. Teardown shuts down the cluster and deletes SSL materials.
Dependencies and integration points: Integrates `KeyStoreTestUtil`, `SSLFactory`, HDFS HTTPS policy, SWebHDFS scheme handling, and inherited FileContext operation tests.
Risks and edge cases: SSL setup failures are wrapped in `RuntimeException`. Hostname verifier and random HTTPS addresses are critical. Cleanup must remove both cluster and keystore artifacts.
Test signals: Signals are inherited WebHDFS/FileContext operation assertions executed over HTTPS plus successful SSL config setup/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSWebHdfsFileContextMainOperations.java -->
