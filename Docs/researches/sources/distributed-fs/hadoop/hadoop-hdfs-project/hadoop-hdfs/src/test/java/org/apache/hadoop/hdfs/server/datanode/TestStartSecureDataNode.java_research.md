# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStartSecureDataNode.java

Purpose: This security-oriented integration test verifies secure MiniDFSCluster startup with an externally supplied Kerberos KDC and clear failures when secure DataNode streaming or HTTP bind ports are already occupied.

Important APIs/types/functions: `MiniDFSCluster`, secure DataNode/NameNode configuration keys, `SecurityUtilTestHelper.isExternalKdcRunning`, JUnit `assumeTrue`, `SecureDataNodeStarter.getSecureResources`, `DFS_DATANODE_ADDRESS_KEY`, `DFS_DATANODE_HTTP_ADDRESS_KEY`, `NetUtils.getFreeSocketPort`, and `BindException`.

Control flow: The secure-start test first skips unless an external KDC is declared running, reads NameNode/DataNode principals and keytabs from system properties, configures Kerberos authentication and low DataNode ports, starts a one-DataNode MiniDFSCluster with DataNode address checking, and asserts the DataNode is up. The bind tests reserve a server socket on the intended streaming or web address, call `SecureDataNodeStarter.getSecureResources`, and expect `BindException` containing the occupied address.

State and persistence behavior: The class mutates Hadoop security configuration, consumes external principal/keytab system properties, and binds local network ports. It does not focus on HDFS file persistence; state under test is process/socket startup configuration and secure resource acquisition.

Dependencies and integration points: It crosses HDFS secure mode config, external KDC/keytab setup, MiniDFSCluster secure startup, DataNode privileged port/resource setup, HTTP/streaming bind paths, and local socket binding.

Risks and test signals: Signals are successful cluster startup for valid external Kerberos config and `BindException` for occupied ports. Risks include platform/network sensitivity, privileged-port/root assumptions, skipped coverage without external KDC properties, and local service interference.
