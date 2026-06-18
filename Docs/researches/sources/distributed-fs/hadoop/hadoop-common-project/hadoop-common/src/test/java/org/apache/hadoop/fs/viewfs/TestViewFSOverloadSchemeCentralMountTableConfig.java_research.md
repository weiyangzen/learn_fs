# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFSOverloadSchemeCentralMountTableConfig.java

Purpose: extends overload-scheme local filesystem tests to verify centralized mount-table config files stored under `Constants.CONFIG_VIEWFS_MOUNTTABLE_PATH`. It specifically checks that the newest versioned file is used and an older invalid mount-table XML file is ignored.

Important APIs and types: `TestViewFileSystemOverloadSchemeLocalFileSystem`, `ViewFsTestSetup.addMountLinksToFile`, `Constants.CONFIG_VIEWFS_MOUNTTABLE_PATH`, `Path`, `Configuration`, and Java `FileWriter`.

Control flow: `setUp` calls the parent setup, creates `mount-table.1.xml` and `mount-table.2.xml` in the test root, and points config at that directory. The override of `addMountLinks` writes malformed XML into the old file, then writes real mount links to the latest file using the shared file serializer. Parent tests then exercise create, delete, merge slash, and conflict behavior through the overload scheme.

State and persistence: this test persists temporary mount-table XML files in the local test root and removes them through the parent teardown.

Dependencies and integration: integrates `ViewFileSystemOverloadScheme`, central mount-table discovery, local filesystem access, and helper serialization format.

Risks and test signals: a failure usually means version ordering is wrong, stale/bad files are parsed, central mount-table path handling broke, or file-backed config no longer matches in-memory config semantics.
