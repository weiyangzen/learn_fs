# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAuthorityLocalFileSystem.java

Purpose: concrete `ViewFileSystemBaseTest` subclass that uses `viewfs://default/` so the URI authority selects the mount table. It verifies the same local-FS-backed behavior as the base class while overriding URI qualification expectations.

Important APIs and types: `ViewFileSystemBaseTest`, `FsConstants.VIEWFS_SCHEME`, `FileSystem.get(URI, conf)`, `Path.makeQualified`, `TRASH_PREFIX`, and `UserGroupInformation`.

Control flow: setup initializes local `fsTarget`, invokes base setup to create mount links and a default `fsView`, then replaces `fsView` with one opened against `viewfs://default/`. `testBasicPaths` asserts URI, working directory, home directory, and path qualification use the authority-bearing scheme. Teardown removes the local test root.

State and persistence: inherits local filesystem mutations from base tests and overrides fallback trash-root calculation for local FS.

Dependencies and integration: covers authority-based mount-table resolution for `ViewFileSystem`, distinct from authorityless `viewfs:///`.

Risks and test signals: regressions surface as wrong URI authority, mount-table lookup using the default table instead of authority, incorrect home/working directory qualification, or trash root differences.
