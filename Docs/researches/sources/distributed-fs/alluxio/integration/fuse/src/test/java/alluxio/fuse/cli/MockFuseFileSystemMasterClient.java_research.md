# Research: sources/distributed-fs/alluxio/integration/fuse/src/test/java/alluxio/fuse/cli/MockFuseFileSystemMasterClient.java

Purpose: package-private test double for `FileSystemMasterClient`, used by FUSE shell tests to avoid a real master. It implements the broad master-client interface with inert behavior so individual tests can subclass and override only the method under examination.

Important APIs and control flow: most mutating operations such as `createDirectory`, `completeFile`, `delete`, `rename`, `setAcl`, `setAttribute`, sync, mount, and job APIs are no-ops. Query methods return neutral defaults: `null`, `false`, `0`, `Optional.empty()`, or `Collections.EMPTY_LIST`. Connection lifecycle methods are also no-ops.

State, dependencies, integration, risks, tests: it has no fields and no persistence; all state must live in subclasses, such as `FuseShellTest.GetStatusFileSystemMasterClient`. Dependencies include many Alluxio gRPC option/result types and wire types. Main risk is interface drift: adding methods to `FileSystemMasterClient` requires updates here. It is intentionally unsuitable for tests expecting realistic master side effects.
