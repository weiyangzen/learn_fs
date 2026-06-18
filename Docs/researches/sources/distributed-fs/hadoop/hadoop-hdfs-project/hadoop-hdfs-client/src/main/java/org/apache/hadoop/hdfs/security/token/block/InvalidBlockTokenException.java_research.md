# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/security/token/block/InvalidBlockTokenException.java

## Purpose

`InvalidBlockTokenException.java` is the checked exception used when HDFS block access token verification fails.

## Important APIs, Types, and Functions

The class extends `IOException`, declares `serialVersionUID = 168L`, and provides a no-argument constructor plus a message constructor.

## Control Flow

There is no internal flow. DataNode/client security paths throw it to signal token verification failure.

## State and Persistence Behavior

It carries normal exception message/cause state inherited from `IOException`. No custom persistence behavior exists.

## Dependencies and Integration Points

Dependencies are `IOException` and Hadoop audience/stability annotations. It integrates with block token validators and DataTransferProtocol error handling.

## Risks and Edge Cases

The class has no cause-taking public constructor, so callers that need to preserve a lower-level cause must wrap differently or lose direct cause chaining. It is marked evolving, so consumers should not assume more than `IOException` semantics.

## Test Signals

Tests are generally indirect: invalid/expired/wrong-mode block token tests should assert this exception type or its remote translation. Constructor tests can verify message propagation.
