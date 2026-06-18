# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/NoECPolicySetException.java

## Purpose
`NoECPolicySetException` is an HDFS-private/evolving `IOException` thrown when a directory has no explicit erasure coding policy where one was required.

## APIs and Behavior
It only defines a message constructor and inherits all behavior from `IOException`.

## State, Dependencies, and Integration
The class has no additional state. It integrates with EC policy query/unset flows and client/admin error reporting.

## Risks and Test Signals
Tests should verify that the right exception is thrown for directories inheriting replication or lacking explicit EC policy, and that RPC conversion preserves the message and exception type where clients rely on it.
