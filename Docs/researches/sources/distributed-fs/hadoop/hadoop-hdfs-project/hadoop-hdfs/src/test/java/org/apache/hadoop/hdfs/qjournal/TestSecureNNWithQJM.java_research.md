# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/TestSecureNNWithQJM.java

Purpose: Integration test for running a secure NameNode with Quorum Journal Manager (QJM). It proves Kerberos, SPNEGO, HTTPS-only HTTP policy, block access tokens, data-transfer protection, and JournalNode authentication work while edit logs are persisted through QJM.

Important APIs/types/functions: `MiniKdc`, `MiniJournalCluster`, `MiniDFSCluster`, `HdfsConfiguration`, `KeyStoreTestUtil`, `SecurityUtil`, `UserGroupInformation`, `startCluster()`, `restartNameNode()`, `doNNWithQJMTest()`, `testSecureMode()`, and `testSecondaryNameNodeHttpAddressNotNeeded()`.

Control flow: `init()` creates a test directory, starts a KDC, creates host and HTTP principals, enables Kerberos, configures HTTPS keystores, and sets NameNode/DataNode/JournalNode principals and keytabs. Each test clones the base config, starts JournalNodes, points `dfs.namenode.edits.dir` at the quorum URI, starts a MiniDFSCluster, writes directories, restarts the NameNode twice, and checks the namespace edits survive.

State and persistence behavior: Edit-log durability through JournalNodes is the main persistent signal. Keytabs and SSL files live in the test dir. One test sets the secondary NameNode HTTP address to `null` to show it is irrelevant to this secure QJM path.

Dependencies and integration points: HDFS security config, Hadoop HTTP auth filters, SSL test utilities, MiniKdc, MiniJournalCluster, MiniDFSCluster namespace reload, and hostname-specific principals.

Risks: Environment-sensitive Kerberos/SSL setup can fail because of hostname resolution, ports, or keystore resources. Regressions here can break secure QJM bootstrap even when insecure QJM still passes.

Test signals: Passing tests show authenticated secure mode can write and replay edits through QJM and that no secondary NameNode HTTP address is required.
