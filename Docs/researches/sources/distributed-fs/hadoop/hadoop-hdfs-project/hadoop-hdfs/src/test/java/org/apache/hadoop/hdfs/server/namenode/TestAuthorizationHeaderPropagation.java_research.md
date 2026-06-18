# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationHeaderPropagation.java

## Purpose

`TestAuthorizationHeaderPropagation` verifies that per-RPC authorization-header bytes stored in `AuthorizationContext` are visible to NameNode audit loggers and do not leak across subsequent RPCs after clearing.

## Important APIs, Types, and Functions

The nested `HeaderCapturingAuditLogger` implements `AuditLogger` and reads `AuthorizationContext.getCurrentAuthorizationHeader()` inside `logAuditEvent`, storing a defensive byte-array copy or null. The test configures `DFS_NAMENODE_AUDIT_LOGGERS_KEY`, starts `MiniDFSCluster`, uses `AuthorizationContext.setCurrentAuthorizationHeader`, `AuthorizationContext.clear`, and performs `FileSystem.mkdirs` calls.

## Control Flow

The test clears captured headers, sets `header-one`, makes a mkdir RPC, clears context, sets `header-two`, makes a second mkdir RPC, clears again, then makes a third mkdir with no header. It asserts the first two audit events captured the corresponding byte arrays and the third captured null.

## State and Persistence Behavior

Header state is per-thread/per-RPC context state, copied by the audit logger to avoid later mutation. Namespace state consists only of three created directories. No edit-log recovery or long-lived persistence is validated.

## Dependencies and Integration Points

The file integrates Hadoop security `AuthorizationContext` with `FSNamesystem` audit logger invocation and custom audit logger configuration. It relies on the NameNode audit path executing during each `mkdirs` RPC.

## Risks and Edge Cases

The nested logger uses a static list that must be cleared before assertions. The test assumes one audit event per mkdir and inspects fixed list indexes. It does not test concurrent RPCs or mutation of the caller-provided byte array after setting the context, although the logger itself copies what it observes.

## Test Signals

The decisive signals are `assertArrayEquals(header1, capturedHeaders.get(0))`, `assertArrayEquals(header2, capturedHeaders.get(1))`, and `assertNull(capturedHeaders.get(2))`, proving both propagation and explicit clear behavior.
