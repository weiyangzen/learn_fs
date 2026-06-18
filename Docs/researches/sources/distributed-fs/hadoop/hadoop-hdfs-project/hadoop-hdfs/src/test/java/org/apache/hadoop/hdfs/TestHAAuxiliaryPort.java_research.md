# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHAAuxiliaryPort.java

## Purpose
Tests HA NameNode auxiliary RPC ports and verifies the same namespace operations work through main and auxiliary ports before and after failover.

## APIs and Control Flow
The test configures two auxiliary RPC ports globally and per HA NN, defines a two-NameNode topology, builds a zero-DN HA `MiniDFSCluster`, transitions NN0 active, obtains both `NameNodeRpcServer` instances and their auxiliary addresses, creates `/test` via NN0 main RPC URI, verifies existence through NN0 auxiliary ports, shuts down NN0, transitions NN1 active, and verifies existence through NN1 main and auxiliary ports.

## State, Dependencies, Integration
State is HA namespace metadata and per-NameNode RPC listener sets. Dependencies include `MiniDFSNNTopology`, `NameNodeRpcServer`, `DFSClient`, HA config keys, and URI-based client construction. It integrates failover with multi-listener RPC access.

## Risks and Test Signals
Signals are auxiliary address counts and cross-port `exists` checks. Risks include fixed configured auxiliary ports (`9000,9001`) colliding on shared hosts and a minor assertion bug in the NN1 auxiliary loop that calls `client1.exists` instead of `clientTmp.exists`, reducing direct coverage of those auxiliary clients.
