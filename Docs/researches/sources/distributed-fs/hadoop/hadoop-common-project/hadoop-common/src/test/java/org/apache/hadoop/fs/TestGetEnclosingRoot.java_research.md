## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestGetEnclosingRoot.java

Purpose: tests the default `FileSystem.getEnclosingRoot` behavior for the local/default filesystem. It verifies root equivalence, idempotence, behavior for existing and non-existing child paths, and use through a wrapped UGI context.

Important APIs/types/functions: `FileSystem.get`, `FileSystem.getEnclosingRoot`, `FileSystem.makeQualified`, `UserGroupInformation.doAs`, and `HadoopTestBase` assertions.

Control flow: helper `getFileSystem` obtains a default FS from a new configuration, and helper `path` qualifies path strings. Tests compare root and `/foo/bar` results, create `/foo/bar` for existing-path behavior, check non-existing path behavior, and call the method under a remote user through `doAs`.

State and persistence: may create a `/foo/bar` path on the default filesystem for `testEnclosingRootPathExists`; no explicit teardown is present in this file.

Dependencies/integration points: default filesystem configuration, local filesystem root semantics, path qualification, and UGI-wrapped filesystem access.

Risks and test signals: creating `/foo/bar` can be sensitive if the default FS is not an isolated test filesystem. The expected default contract is simple: all tested paths enclose to the filesystem root and repeated calls are idempotent.
