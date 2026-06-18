# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/NameNodeHAProxyFactory.java

## Purpose

`NameNodeHAProxyFactory.java` creates non-HA NameNode RPC proxies for use by HA failover proxy providers. The source was read as a complete 52-line file.

## Important APIs, Types, and Functions

The generic class implements `HAProxyFactory<T>`. It provides two `createProxy` overloads and `setAlignmentContext`.

## Control Flow

Both factory methods delegate to `NameNodeProxies.createNonHAProxy` for a concrete NameNode address and return the proxy. The overload with `fallbackToSimpleAuth` passes the optional `AlignmentContext`, enabling coordinated client alignment behavior where supported.

## State and Persistence Behavior

The only state is the optional in-memory `alignmentContext`. No persistent data is written.

## Dependencies and Integration Points

It integrates with HDFS `NameNodeProxies`, Hadoop `Configuration`, `UserGroupInformation`, `AlignmentContext`, and the HA client proxy-provider stack.

## Risks and Edge Cases

The overload without `fallbackToSimpleAuth` does not pass `alignmentContext`; callers needing alignment must use the newer overload. Proxy creation failures propagate as IOExceptions and drive failover provider behavior.

## Test Signals

Tests should verify proxy creation delegates with retries and fallback auth, alignment context is passed in the supported overload, and failures from `NameNodeProxies` propagate.
