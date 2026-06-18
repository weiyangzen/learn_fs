<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerProtocols.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerProtocols.java

## Purpose

`BalancerProtocols` is a marker interface representing the full RPC protocol set required by the HDFS balancer: client-facing namespace operations plus NameNode internal block-location/movement operations.

## Important APIs and types

It extends `ClientProtocol` and `NamenodeProtocol`, is annotated private, and carries `@KerberosInfo` with the NameNode Kerberos principal key.

## Control flow

No methods are declared directly. RPC implementations use this combined type so the balancer can authenticate and call both parent interfaces through one proxy.

## State and persistence behavior

No state is defined here.

## Dependencies and integration points

Integrates balancer clients, Hadoop RPC security, `DFSConfigKeys.DFS_NAMENODE_KERBEROS_PRINCIPAL_KEY`, `ClientProtocol`, and `NamenodeProtocol`.

## Risks and edge cases

Any method or security annotation changes in parent protocols affect balancer compatibility. The interface is private, but RPC compatibility still matters across rolling upgrades.

## Test signals

Balancer integration tests and secure-cluster RPC tests cover this type indirectly by creating balancer proxies and running balancing operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerProtocols.java -->
