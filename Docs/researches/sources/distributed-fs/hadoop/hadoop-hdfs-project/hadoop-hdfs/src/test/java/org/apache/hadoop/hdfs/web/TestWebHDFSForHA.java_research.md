# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSForHA.java

Purpose: WebHDFS high-availability behavior across logical nameservice failover, delegation tokens, stale standby credentials, open streams, multi-namespace config, and startup retry.

Important APIs/types/functions: `MiniDFSNNTopology`, `DFSTestUtil.newHAConfiguration`, `HATestUtil.setFailoverConfigurations`, `WebHdfsFileSystem`, `DelegationTokenSecretManager`, `ExceptionHandler`, `JsonUtilClient.toRemoteException`, `Whitebox.setInternalState`, `SubjectInheritingThread`.

Control flow: tests build a two-NameNode HA topology under logical URI `webhdfs://minidfs`. `testHA` writes before and after active NN shutdown/failover. `testSecureHAToken` gets a delegation token, fails over, renews/cancels it, and verifies WebHDFS token methods were used. The stale-credentials test forces the old NameNode's secret manager to fail token lookup and verifies the server-side security exception is serialized back as a `StandbyException` client can unwrap. `testFailoverAfterOpen` opens an output stream before failover and writes/closes after. Multi-namespace config checks only the selected nameservice resolves two NN addresses. Startup retry nulls `NameNode.rpcServer`, starts a background mkdir via WebHDFS, restores the server, and waits for success.

State and persistence behavior: temporary HA clusters per test, files/directories under `/test`, token state in NameNode secret managers, and reflective mutation of NameNode internals.

Dependencies and integration points: HA failover proxy configuration, WebHDFS token lifecycle, server exception serialization, client retry, and startup race handling.

Risks: reflective `Whitebox` changes and threaded wait can be timing-sensitive. Token tests rely on secret-manager internals and mocked/spied filesystem registration.

Test signals: successful operation after failover, token renew/cancel routing, stale credential unwrapping, stream survival across failover, address resolution, and retry during startup.
