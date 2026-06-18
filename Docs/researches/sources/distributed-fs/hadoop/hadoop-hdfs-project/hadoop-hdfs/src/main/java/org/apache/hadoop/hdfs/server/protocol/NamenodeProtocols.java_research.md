<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocols.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocols.java

## Purpose

`NamenodeProtocols` is a marker interface composing the full set of RPC protocols implemented by a NameNode.

## Important APIs and types

It extends `ClientProtocol`, `DatanodeProtocol`, `DatanodeLifelineProtocol`, `NamenodeProtocol`, authorization and user-mapping refresh protocols, reconfiguration, call-queue refresh, generic refresh, user mapping lookup, and `HAServiceProtocol`.

## Control flow

There are no methods declared locally. The NameNode RPC server advertises/implements this aggregate so server-side code can expose all protocol facets through one implementation type.

## State and persistence behavior

The interface has no state. Implementing classes coordinate client namespace operations, DataNode block reports, admin refreshes, HA transitions, and NameNode protocol operations.

## Dependencies and integration points

This is an integration hub for HDFS client, DataNode, HA, reconfiguration, security refresh, and admin RPCs. Any addition/removal changes the NameNode's advertised surface.

## Risks and test signals

Risks include accidentally omitting a protocol from the aggregate or exposing a protocol on an unintended RPC server. Tests should cover NameNode RPC startup, protocol proxy creation, ACL enforcement per protocol, and HA/admin command routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/NamenodeProtocols.java -->
