# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestNfs3HttpServer.java

## Purpose
`TestNfs3HttpServer` verifies that the NFS gateway HTTP/HTTPS info server starts and exposes default servlet endpoints.

## Important APIs, Types, And Functions
Setup uses `NfsConfiguration`, `HttpConfig.Policy.HTTP_AND_HTTPS`, `KeyStoreTestUtil`, `MiniDFSCluster`, and ephemeral NFS/http/https addresses. `testHttpServer` starts `Nfs3`, obtains `Nfs3HttpServer`, fetches `/jmx`, and checks the secure port.

## Control Flow
Before all tests, SSL config and keystores are generated under a temp directory, then MiniDFSCluster starts. The test starts NFS, reads the info server URI, downloads `/jmx`, asserts JMX content includes a Java MBean prefix, and asserts HTTPS port is positive. Teardown deletes temp files, shuts down the cluster, and cleans SSL config.

## State And Persistence
It writes temporary keystore and SSL config files under the test temp path and creates an in-process MiniDFSCluster. No durable repository files are modified.

## Dependencies And Integration Points
It covers `RpcProgramNfs3.startDaemons`, `Nfs3HttpServer`, Hadoop HTTP server defaults, HTTPS configuration, and metrics/JMX exposure.

## Risks
The NFS service is not explicitly stopped in the test method. Network-bound tests can be sensitive to local port allocation and HTTP policy configuration.

## Test Signals
Passing confirms the NFS info server can start with HTTP and HTTPS enabled and serve the standard `/jmx` endpoint.
