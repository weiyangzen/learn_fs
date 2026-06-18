# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultINodeAttributesProvider.java

## Purpose
`DefaultINodeAttributesProvider` is the identity implementation of `INodeAttributeProvider`, used when no custom provider is configured.

## Important APIs and Types
It exposes a static `DEFAULT_PROVIDER` instance. `start` and `stop` are no-ops. `getAttributes` returns the supplied `INodeAttributes` unchanged.

## Control Flow
There is no conditional behavior; all paths pass through existing inode attributes directly.

## State and Persistence
The class has no mutable state beyond the static instance and persists nothing.

## Dependencies and Integration
It is used by `FSDirectory`/NameNode attribute lookup paths as the baseline provider and can be replaced by custom implementations.

## Risks and Test Signals
The static field is mutable rather than final, so accidental replacement can affect global behavior. Tests should verify default provider identity behavior and lifecycle no-ops, and integration tests should ensure custom provider fallback returns to this behavior when disabled.
