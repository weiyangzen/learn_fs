# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/UnsupportedActionException.java

## Purpose

`UnsupportedActionException.java` defines a NameNode-private checked exception for unsupported operations. The source was read as a complete 38-line file.

## Important APIs, Types, and Functions

The class extends `IOException`, declares `serialVersionUID`, and provides a single message constructor.

## Control Flow

There is no internal branching. Callers throw it where a requested action is not supported in the current context.

## State and Persistence Behavior

The exception carries only the inherited message and stack trace. It owns no persistent state.

## Dependencies and Integration Points

It integrates with NameNode code paths that already use `IOException` as the RPC/operation failure surface, allowing unsupported action failures to propagate through existing checked-exception handling.

## Risks and Edge Cases

The value is mostly semantic. Catching broad `IOException` can erase the distinction unless callers log or inspect the concrete type.

## Test Signals

Tests should verify the relevant caller surfaces this exception type and message for unsupported operations, and that RPC or CLI layers report it without treating it as an internal crash.
