# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/HDFSPolicyProvider.java

Purpose: Registers HDFS IPC protocol interfaces with Hadoop service authorization by mapping each protocol class to the ACL configuration key that controls access to it.

Important APIs and types: `HDFSPolicyProvider` extends `PolicyProvider`. The static `hdfsServices` array maps ACL keys to `ClientProtocol`, `ClientDatanodeProtocol`, `DatanodeProtocol`, `InterDatanodeProtocol`, `NamenodeProtocol`, `QJournalProtocol`, `InterQJournalProtocol`, `HAServiceProtocol`, `ZKFCProtocol`, refresh/get-user-mapping protocols, `GenericRefreshProtocol`, `DatanodeLifelineProtocol`, and `ReconfigurationProtocol`. `getServices()` returns that array.

Control flow: There is no dynamic control flow beyond returning the prebuilt array to the service authorization framework.

State and persistence behavior: The service map is static in-memory metadata. Effective authorization state comes from `CommonConfigurationKeys` ACL values loaded by Hadoop RPC/service authorization.

Dependencies and integration points: Integrates with Hadoop `PolicyProvider`, `Service`, common security ACL keys, HDFS client/server/qjournal protocols, HA protocols, and admin refresh protocols. It is consumed during RPC server authorization setup.

Risks: Missing a protocol leaves it without the intended service ACL mapping; mapping a protocol to the wrong key can over- or under-authorize RPC access. The returned array is not defensively copied, so accidental mutation by a caller would affect later consumers.

Test signals: Service authorization tests should verify every HDFS RPC protocol is present with the expected ACL key, secure RPC startup loads this provider, and admin refresh/reconfiguration/lifeline protocols enforce their configured ACLs.
