# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAuthorizationContext.java

## Purpose

`TestAuthorizationContext` verifies the new `INodeAttributeProvider.AuthorizationContext` builder and the compatibility bridge between legacy `AccessControlEnforcer.checkPermission` and `checkPermissionWithContext` in `FSPermissionChecker`.

## Important APIs, Types, and Functions

The test uses `CallerContext`, `UserGroupInformation`, mocked `INodesInPath`, `INodeAttributeProvider`, and `AccessControlEnforcer`. It exercises `AuthorizationContext.Builder` setters for filesystem owner, supergroup, caller UGI, inode attributes, inode array, path components, snapshot ID, path, ancestor index, owner/access flags, operation name, and caller context. It also uses `FSPermissionChecker.setOperationType`.

## Control Flow

`setUp` programs the mocked `INodesInPath` to return empty inode/path state. `testBuilder` populates a builder, builds a context, and asserts getters return the exact configured values. `testLegacyAPI` configures a permission checker with context API disabled, invokes `checkPermission`, and verifies the old `checkPermission` signature is called. `testCheckPermissionWithContextAPI` enables the context API, sets an operation type, invokes `checkPermission`, builds an expected context, and verifies `checkPermissionWithContext` is used.

## State and Persistence Behavior

There is no filesystem persistence. State is mock-returned path metadata plus thread-local `CallerContext` and static operation type state in `FSPermissionChecker`. The tests validate object assembly and dispatch, not on-disk namespace changes.

## Dependencies and Integration Points

The file sits at the integration boundary between `FSPermissionChecker`, `INodeAttributeProvider`, external authorization enforcers, inode path metadata, and caller-context propagation. It ensures newer context-aware authorization hooks can coexist with legacy implementations.

## Risks and Edge Cases

The expected `ancestorIndex` is `inodes.length - 2`, which is `-2` for the empty inode array used here; production callers usually have real paths. The verification relies on `AuthorizationContext.equals` accepting another context object broadly, so it proves API selection more than deep object equality in the Mockito verification. Static operation type and caller context need cleanup discipline in broader suites.

## Test Signals

Signals include getter equality for every builder field, Mockito verification of the legacy `checkPermission` argument list when the context API flag is false, and Mockito verification of `checkPermissionWithContext` when the flag is true and an operation name has been set.
