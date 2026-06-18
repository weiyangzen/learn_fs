# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/RemoteNameNodeInfo.java

## Purpose

`RemoteNameNodeInfo.java` represents another NameNode in the same HA nameservice, including its configuration, NameNode ID, IPC address, and HTTP address. The source was read as a complete 129-line file.

## Important APIs, Types, and Functions

Static factories are `getRemoteNameNodes(Configuration)` and `getRemoteNameNodes(Configuration, String)`. Instance methods expose IPC address, NameNode ID, HTTP address, configuration, mutable IPC setter, `toString`, `equals`, and `hashCode`.

## Control Flow

The factory resolves the nameservice ID, returns an empty list outside HA/federation, obtains configurations for other nodes from `HAUtil`, reads each peer's NameNode ID and service address, derives HTTP/HTTPS info-server URL using the original client's HTTP scheme, and creates `RemoteNameNodeInfo` entries. `equals` compares URL strings instead of `URL.equals` to avoid blocking DNS resolution.

## State and Persistence Behavior

The object is transient configuration state. `setIpcAddress` lets callers override service address resolution, for example to force service RPC address for log rolling.

## Dependencies and Integration Points

It integrates with `DFSUtil`, `HAUtil`, `NameNode.getServiceAddress`, `DFSUtil.getInfoServerWithDefaultHost`, `BootstrapStandby`, `EditLogTailer`, and `StandbyCheckpointer`-adjacent HA code.

## Risks and Edge Cases

Address validation is intentionally left to callers, so invalid port or wildcard addresses can appear until later checks. HTTP scheme is taken from the original configuration, while host defaults come from peer IPC addresses.

## Test Signals

Tests should cover no nameservice behavior, multiple peer discovery, HTTP and HTTPS schemes, NameNode ID extraction, IPC override, equals/hash without DNS blocking, and invalid address handling by callers.
