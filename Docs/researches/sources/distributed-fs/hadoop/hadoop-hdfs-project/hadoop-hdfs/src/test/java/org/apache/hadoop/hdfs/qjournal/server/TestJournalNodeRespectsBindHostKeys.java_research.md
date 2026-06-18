# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournalNodeRespectsBindHostKeys.java

Purpose: Verifies JournalNode RPC, HTTP, and HTTPS listeners honor explicit bind-host keys.

Important APIs/types/functions: `DFS_JOURNALNODE_RPC_BIND_HOST_KEY`, `DFS_JOURNALNODE_HTTP_BIND_HOST_KEY`, `DFS_JOURNALNODE_HTTPS_BIND_HOST_KEY`, `MiniJournalCluster`, `JournalNodeRpcServer`, `KeyStoreTestUtil`, `HttpConfig.Policy.HTTPS_ONLY`, and `HdfsConfiguration`.

Control flow: Each test first starts a one-node cluster without the bind-host key and asserts it does not bind wildcard `0.0.0.0`. It then sets the relevant bind-host key to wildcard, starts a new cluster, and verifies the listener address. HTTPS setup creates SSL config and sets HTTPS-only policy.

State and persistence behavior: No journal persistence is tested. Temporary SSL keystore/config files support the HTTPS case.

Dependencies and integration points: JournalNode listener setup, MiniJournalCluster builder, SSL test utilities, and HDFS HTTP policy.

Risks: Wrong bind interfaces can expose services or make them unreachable in multi-homed deployments.

Test signals: Passing confirms default non-wildcard behavior and explicit wildcard binding for RPC, HTTP, and HTTPS.
