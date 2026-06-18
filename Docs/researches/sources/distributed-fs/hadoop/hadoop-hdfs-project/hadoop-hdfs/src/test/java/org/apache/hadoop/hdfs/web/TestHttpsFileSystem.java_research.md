# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestHttpsFileSystem.java

Purpose: verifies secure WebHDFS (`swebhdfs`) works against an HTTPS-only MiniDFSCluster.

Important APIs/types/functions: `DFS_HTTP_POLICY_KEY`, HTTPS address keys, `KeyStoreTestUtil.setupSSLConfig`, `MiniDFSCluster`, `WebHdfsTestUtil.getWebHdfsFileSystem(conf, "swebhdfs")`.

Control flow: `setUp` configures HTTPS-only NameNode/DataNode endpoints on random ports, creates temporary keystore/SSL config files, starts a one-datanode cluster, writes `/test`, records the actual HTTPS NameNode address, and patches it into configuration. The test obtains an `swebhdfs` filesystem, creates `/testswebhdfs`, writes one byte, verifies existence, opens the file, and reads the expected byte. `tearDown` shuts down the cluster, deletes temp dirs, and cleans SSL config.

State and persistence behavior: temporary keystore directory and SSL config resources under the test temp path; MiniDFSCluster file state. Cleanup is class-level.

Dependencies and integration points: integrates WebHDFS over TLS, Hadoop SSL test utilities, NameNode HTTPS address publication, and filesystem open/create APIs.

Risks: SSL material setup/cleanup and port allocation can be environment-sensitive. The test validates basic create/read rather than certificate failure modes or DN redirect details.

Test signals: successful `swebhdfs` create, exists, open, and byte-level read through HTTPS.
