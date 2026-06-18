# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointOutputStream.java

## Purpose
`CheckpointOutputStream` writes the checkpoint type header for a new checkpoint stream.

## Important APIs, Types, And Functions
The constructor extends `DataOutputStream` and writes `type.getId()` as the first long.

## Control Flow, State, Dependencies, Risks, And Tests
After construction, callers write format-specific payload bytes. Persistent state is the leading type id in every checkpoint. Dependencies are `CheckpointType` and Java data streams. Risks include callers wrapping streams in the wrong order, not flushing the header, or writing a payload that does not match the declared type. Tests should verify header round trips with `CheckpointInputStream`, all checkpoint types, and behavior on underlying IO failure.
