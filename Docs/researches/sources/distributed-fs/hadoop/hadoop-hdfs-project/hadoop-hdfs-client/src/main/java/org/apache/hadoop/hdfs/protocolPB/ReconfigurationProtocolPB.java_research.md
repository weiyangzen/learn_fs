# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocolPB/ReconfigurationProtocolPB.java

## Purpose

`ReconfigurationProtocolPB.java` is the protobuf RPC interface marker for live reconfiguration calls to NameNode/DataNode services. It extends the generated `ReconfigurationProtocolService.BlockingInterface` and adds Hadoop RPC/security annotations.

## Important APIs, Types, and Functions

The interface has no methods of its own; it inherits generated blocking RPC methods such as start reconfiguration, list reconfigurable properties, and get reconfiguration status. Annotations define Kerberos principal lookup via `CommonConfigurationKeys.HADOOP_SECURITY_SERVICE_USER_NAME_KEY`, protocol name `org.apache.hadoop.hdfs.protocol.ReconfigurationProtocol`, and protocol version `1`. Audience is public and stability is evolving.

## Control Flow

There is no executable control flow. Hadoop RPC uses the annotations and inherited generated service methods to bind clients and servers to the protobuf implementation.

## State and Persistence Behavior

The interface owns no state. It participates in RPC registration and security metadata only.

## Dependencies and Integration Points

Dependencies are Hadoop classification annotations, RPC `ProtocolInfo`, `KerberosInfo`, `CommonConfigurationKeys`, and generated `ReconfigurationProtocolService`. It is consumed by `ReconfigurationProtocolTranslatorPB` and corresponding server-side PB implementations.

## Risks and Edge Cases

Changing protocol name/version or security annotations would break RPC compatibility or authentication. Because it extends generated protobuf code, proto service signature changes must be coordinated with translators and servers.

## Test Signals

Compile and RPC binding tests are the main signal, along with secure-cluster tests that verify the Kerberos server principal is discovered correctly.
