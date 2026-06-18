# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestHDFSPolicyProvider.java

## Purpose
Ensures `HDFSPolicyProvider` declares service ACL policies for every RPC protocol implemented by important HDFS RPC server classes.

## APIs and Control Flow
`initialize` loads all `Service` entries from `HDFSPolicyProvider` into `policyProviderProtocols`. `data` parameterizes the test over `NameNodeRpcServer`, `DataNode`, and `JournalNodeRpcServer`. `testPolicyProviderForServer` uses `ClassUtils.getAllInterfaces`, filters interfaces whose names end with `Protocol`, and checks the set difference from policy-provider protocols is empty.

## State, Dependencies, Integration
State is static reflection-derived sets of protocol classes. Dependencies include `HDFSPolicyProvider`, `Service`, HDFS server classes, `ClassUtils`, JUnit parameterization, and `Sets.difference`. It integrates service authorization configuration with actual RPC surface area.

## Risks and Test Signals
The key signal is a failing diff listing uncovered protocols. Risks are naming-convention dependence (`endsWith("Protocol")`), reflection including inherited interfaces that may not require policy, and missing protocols whose interface names do not follow the convention.
