# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancer.java

## Purpose
`TestBalancer` is the main HDFS balancer test harness. It verifies balancer behavior for normal imbalance, uneven distribution, CLI parsing, include/exclude host lists, source/target filtering, rolling upgrade behavior, concurrent balancer leases, erasure-coded striped files, secure keytab execution, RPC throttling, and several exit-status paths.

## Important APIs, Types, and Functions
Important production types include `Balancer`, `Balancer.Cli`, `BalancerParameters`, `BalancingPolicy`, `Dispatcher`, `NameNodeConnector`, `ExitStatus`, `MiniDFSCluster`, `ClientProtocol`, `DatanodeInfo`, `LocatedBlocks`, `FSNamesystem`, and `SimulatedFSDataset`. Core helpers are `initConf`, `initSecureConf`, `createFile`, `generateBlocks`, `distributeBlocks`, `testUnevenDistribution`, `waitForHeartBeat`, overloaded `waitForBalancer`, `doTest`, `runBalancer`, `runBalancerCli`, `testBalancerDefaultConstructor`, `spyFSNamesystem`, and `testBalancerRPCDelay`.

## Control Flow
Most tests configure small simulated-capacity clusters with 100-byte blocks, write data to make original nodes partially full, start empty nodes, run balancer through either API or CLI, and poll NameNode reports until capacity and utilization match expectations. Uneven-distribution tests generate blocks, rebuild without formatting, inject block reports with custom distributions, then rebalance. CLI tests parse invalid parameters and host filters. Rolling-upgrade tests assert default balancer aborts during unfinalized upgrade and succeeds with `runDuringUpgrade`. Striped-file tests enable EC policy, create striped files, rebalance, and verify located striped blocks. Secure keytab tests initialize MiniKdc/SSL, log in with the balancer keytab, and run a functional scenario under `doAs`.

## State and Persistence Behavior
The suite mutates static balancer behavior through `NameNodeConnector.setWrite2IdFile`, creates MiniDFSCluster data, creates/deletes include/exclude host files, creates a `balancer.id` lease file, uses MiniKdc/keytab/SSL artifacts, and spies on `FSNamesystem` to record `getBlocks` timing. Many tests rely on heartbeat, block report, deletion report, and safe-mode state transitions.

## Dependencies and Integration Points
Dependencies cover HDFS cluster simulation, NameNode RPC URI discovery, DataNode storage reports, block placement, erasure coding, Kerberos/SSL, Mockito spies, host topology, and balancer internal dispatchers. The class is reused by encrypted transfer, SASL transfer, RPC delay, HA service, and balancer service mode tests.

## Risks and Test Signals
Risks include heavy timing sensitivity, random block distribution, global static flags, security-global UGI state, cleanup of balancer lease and host files, reflection into dispatcher fields, and several long-running MiniDFSCluster scenarios. Signals include exact exit-code assertions, utilization variance checks, host-filter exclusion counts, parser exception messages, EC block placement verification, RPC throttling metrics, and secure keytab login assertions.
