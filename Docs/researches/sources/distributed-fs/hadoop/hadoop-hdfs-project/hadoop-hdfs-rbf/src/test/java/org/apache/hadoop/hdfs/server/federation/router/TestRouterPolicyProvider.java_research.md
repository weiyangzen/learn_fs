# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterPolicyProvider.java

## Purpose

`TestRouterPolicyProvider.java` verifies that `RouterPolicyProvider` declares security policy entries for every RPC protocol interface implemented by key HDFS RPC server classes. The source was read as a complete 99-line parameterized JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `RouterPolicyProvider`, Hadoop `Service`, Apache Commons `ClassUtils.getAllInterfaces`, `Sets.difference`, `RouterRpcServer`, `NameNodeRpcServer`, `DataNode`, `RouterAdminServer`, and JUnit parameterization. Key methods are `initialize`, `data`, `initTestRouterPolicyProvider`, and `testPolicyProviderForServer`.

## Control Flow

`initialize` reads all services from `RouterPolicyProvider` and stores their protocol classes in a static set. The parameterized test runs for each server class, finds all implemented interfaces whose simple names end in `Protocol`, logs both protocol sets, asserts the server exposes at least one protocol, computes the difference between server protocols and provider protocols, and fails if any server protocol lacks a policy entry.

## State and Persistence Behavior

State is limited to the static `policyProviderProtocols` set and the current parameter's `rpcServerClass`. No external state is modified.

## Dependencies and Integration Points

This test protects the security authorization boundary between HDFS RPC server protocol interfaces and router policy provider service declarations. It also indirectly tracks protocol interface changes on namenode, datanode, router RPC, and router admin servers.

## Risks and Edge Cases

The heuristic only considers interfaces whose simple names end with `Protocol`; protocols with different naming would be ignored. It checks presence but not ACL key correctness or service principal configuration. Interface inheritance changes can add protocols and require provider updates.

## Test Signals

Signals are a non-empty protocol set for every scanned server class and an empty difference between implemented protocol interfaces and `RouterPolicyProvider` service protocols.
