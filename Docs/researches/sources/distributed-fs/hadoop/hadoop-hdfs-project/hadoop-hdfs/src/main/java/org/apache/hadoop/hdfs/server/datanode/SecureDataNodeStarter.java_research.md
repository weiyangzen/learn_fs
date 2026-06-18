<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/SecureDataNodeStarter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/SecureDataNodeStarter.java

## Purpose

`SecureDataNodeStarter` is the Apache Commons Daemon entry point used when a DataNode must bind privileged resources before dropping privileges. It acquires streaming and optional HTTP sockets, then starts normal DataNode initialization with those resources.

## Important APIs, Types, And Functions

- Implements `Daemon` with `init`, `start`, `stop`, and `destroy`.
- `SecureResources` carries the streaming `ServerSocket`, optional HTTP `ServerSocketChannel`, SASL status, and flags indicating whether RPC and HTTP ports are privileged.
- `getSecureResources(Configuration)` binds the streaming address and, when HTTP is enabled, the info-server address.
- `appendMessageToBindException` adds the attempted address to bind errors while preserving cause and stack trace.

## Control Flow

`init` creates a fresh `HdfsConfiguration`, stores daemon arguments, and obtains secure resources. `start` calls `DataNode.secureMain(args, resources)`. Resource acquisition reads SASL settings, streaming address, socket timeout, listen backlog, and HTTP policy; it then binds exact configured ports and fails if the OS assigned a different port.

## State And Persistence

The class stores only daemon arguments and bound secure resources. The sockets are live process resources handed to `DataNode`; no filesystem persistence occurs here.

## Dependencies And Integration Points

It integrates Commons Daemon startup, `DataNode`, `DFSUtil` HTTP policy, data-transfer SASL, `SecurityUtil` privileged-port detection, and HDFS configuration keys. It is part of secure-cluster bootstrap rather than normal in-process DataNode logic.

## Risks And Edge Cases

Port binding must happen before privilege drop and must use exact configured ports. HTTP binding is skipped when HTTP is disabled, even if HTTPS is used. Socket resource cleanup on later startup failure is delegated to DataNode lifecycle. Diagnostics go to stderr during early startup.

## Test Signals

Tests should cover SASL-enabled flags, privileged versus nonprivileged ports, HTTP-enabled and disabled policies, bind failures with address-enriched exceptions, wrong local-port detection, and handoff to `DataNode.secureMain`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/SecureDataNodeStarter.java -->
