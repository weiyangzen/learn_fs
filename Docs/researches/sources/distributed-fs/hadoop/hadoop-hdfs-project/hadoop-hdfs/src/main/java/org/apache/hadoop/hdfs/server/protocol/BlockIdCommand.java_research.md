<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockIdCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockIdCommand.java

## Purpose

`BlockIdCommand` is a compact DataNode command carrying only block ids for an action tied to a block pool.

## Important APIs and types

- Extends `DatanodeCommand`.
- Constructor accepts action, block pool id, and `long[] blockIds`.
- Getters expose block pool id and block id array.

## Control flow

The NameNode constructs the command with the relevant action code; DataNode-side protocol handling interprets the ids according to that action.

## State and persistence behavior

It is an in-memory/RPC DTO. The `blockIds` array is not copied. No persistence occurs in the command object.

## Dependencies and integration points

Depends on `DatanodeCommand` and protocol action constants. It is used where block ids are sufficient and full `Block` metadata would be unnecessary overhead.

## Risks and edge cases

Array mutation after construction can change command contents. Callers must ensure ids belong to the stated block pool and that the receiving action accepts id-only payloads.

## Test signals

Protocol conversion and DataNode command-processing tests should verify block pool/id preservation and action-specific behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockIdCommand.java -->
