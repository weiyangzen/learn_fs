# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerException.java

## Purpose

`DiskBalancerException` is the typed IOException used by disk balancer RPC and command code. It carries a structured `Result` enum in addition to the normal exception message/cause.

## Important APIs, Control Flow, and State

`Result` enumerates disk-balancer failure categories such as not enabled, invalid plan/version/hash, old plan, DataNode mismatch, malformed plan, plan already in progress, invalid volume/move/node, internal error, no such plan, unknown key, non-regular DataNode status, and invalid host file path. Constructors support message+result, message+cause+result, and cause+result. `getResult` exposes the enum.

State is immutable per exception: the inherited IOException state plus final `result`. There is no persistence, but result names can cross RPC boundaries and appear in CLI/log output.

## Dependencies, Integration, Risks, and Tests

Dependencies are JDK `IOException`. The exception integrates with `ClientDatanodeProtocol`, DataNode disk balancer service, and CLI commands such as cancel/query/execute.

Risks include adding/removing enum values without updating clients, logs, or protobuf/RPC mapping, and commands relying on result text. Tests should verify constructors preserve message/cause/result and that command/RPC paths propagate meaningful result codes.
