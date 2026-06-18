<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/CheckpointCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/CheckpointCommand.java

## Purpose

`CheckpointCommand` is the `NamenodeCommand` returned by `NamenodeProtocol.startCheckpoint` when a subordinate or backup NameNode is allowed to run a checkpoint. It packages the checkpoint identity and whether the produced image must be sent back to the active NameNode.

## Important APIs and types

The class extends `NamenodeCommand` with action `NamenodeProtocol.ACT_CHECKPOINT`. Its payload is a `CheckpointSignature` plus `needToReturnImage`. The public surface is the default constructor for serialization, the main constructor, `getSignature()`, and `needToReturnImage()`.

## Control flow

The constructor calls the superclass with the checkpoint action code and stores the signature/return flag. Consumers inspect the command after the active NameNode admits a checkpoint and use the signature to bind subsequent `endCheckpoint` or image-transfer work to the same checkpoint attempt.

## State and persistence behavior

This is an in-memory RPC value object. It does not persist data itself, but it carries a `CheckpointSignature` that describes persistent namespace/checkpoint state managed by NameNode storage.

## Dependencies and integration points

It integrates `NamenodeProtocol`, `NamenodeCommand`, and `CheckpointSignature`. Wire compatibility depends on the corresponding protobuf RPC translator for Namenode protocol commands.

## Risks and test signals

Risks are mostly protocol drift: missing or mismatched signatures can let a backup node complete the wrong checkpoint, and the return-image flag affects whether the NameNode receives a fresh fsimage. Useful tests cover accepted/rejected checkpoint flows, image-return decisions, null/default serialization, and signature mismatch rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/CheckpointCommand.java -->
