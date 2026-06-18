# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeTcpNoDelay.java

## Purpose

`TestDataNodeTcpNoDelay` verifies HDFS client/DataNode sockets apply TCP_NODELAY according to default and explicit configuration across normal data writes and DataNode block-transfer replication.

## Important APIs, Types, and Functions

The suite uses `HADOOP_RPC_SOCKET_FACTORY_CLASS_DEFAULT_KEY` to install `SocketFactoryWrapper`, `NetUtils.getDefaultSocketFactory`, MiniDFSCluster, `DFSTestUtil`, and configuration keys for client/server data transfer and IPC TCP_NODELAY. `SocketFactoryWrapper` extends `StandardSocketFactory` and wraps all created sockets in `SocketWrapper`. `SocketWrapper` delegates socket operations and records the last value passed to `setTcpNoDelay`.

## Control Flow

`testTcpNoDelayEnabled` leaves defaults in place, installs the wrapper socket factory, starts a three-DataNode cluster, creates replicated data, forces a block transfer by increasing replication from one to two, and asserts all tracked sockets had TCP_NODELAY enabled. `testTcpNoDelayDisabled` sets data-transfer client, data-transfer server, IPC client, and IPC server TCP_NODELAY keys to false, performs the same data creation and transfer, and asserts the tracked sockets were not all TCP_NODELAY enabled.

## State and Persistence Behavior

State is kept in the static `SocketFactoryWrapper.sockets` list and per-wrapper `tcpNoDelay` booleans. HDFS files are created only to drive socket creation and block transfer. The wrapper is reset and the cluster is shut down in each `finally` block.

## Dependencies and Integration Points

The file integrates Hadoop socket factory configuration, RPC and data-transfer TCP_NODELAY keys, DFS client writes, replication-driven DataNode `transferBlocks`, and Java socket delegation. It checks both client-facing and inter-DataNode transfer paths.

## Risks and Edge Cases

The wrapper records whether `setTcpNoDelay` was ever called with true or false, not whether the first send happened before configuration. The disabled test only asserts not all sockets were true because parts of the client write path always enable TCP_NODELAY. Static socket tracking must be reset between tests. Coverage depends on all relevant sockets being created through the configured default socket factory.

## Test Signals

Signals are `SocketFactoryWrapper.wasTcpNoDelayActive()` returning true under defaults and false when all known TCP_NODELAY settings are disabled after exercising both file creation and block transfer.
