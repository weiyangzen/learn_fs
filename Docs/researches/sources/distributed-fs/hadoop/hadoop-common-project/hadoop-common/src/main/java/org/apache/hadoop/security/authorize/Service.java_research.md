# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/Service.java

## Purpose

`Service` is the small data holder that binds a service-level authorization configuration key to a Hadoop RPC protocol class.

## Important APIs, Types, and Functions

It has a constructor `Service(String key, Class<?> protocol)` and getters `getServiceKey()` and `getProtocol()`.

## Control Flow

There is no internal branching. `PolicyProvider` returns arrays of `Service`, and `ServiceAuthorizationManager` iterates them to build ACL and host maps.

## State and Persistence Behavior

The object holds only the key and protocol reference in memory. Policy persistence is external in configuration resources.

## Dependencies and Integration Points

It is used by policy provider implementations for HDFS, MapReduce, and other Hadoop daemons.

## Risks and Edge Cases

The class does not validate null keys or protocols. Incorrect service keys can make services inherit defaults rather than explicit policy.

## Test Signals

Tests should verify provider arrays contain correct key/protocol pairs and that manager refresh maps them to the expected ACLs.
