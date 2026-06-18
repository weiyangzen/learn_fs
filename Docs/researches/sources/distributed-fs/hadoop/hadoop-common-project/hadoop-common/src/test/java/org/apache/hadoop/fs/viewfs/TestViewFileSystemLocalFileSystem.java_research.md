# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemLocalFileSystem.java

Purpose: concrete `ViewFileSystemBaseTest` subclass that runs the generic `FileSystem` viewfs behavior suite against the local filesystem and adds NFly-specific tests.

Important APIs and types: `ViewFileSystemBaseTest`, `FileSystem.getLocal`, `ConfigUtil.addLinkNfly`, `FileSystem.get(URI.create("viewfs:///"), conf)`, `FSDataOutputStream`, `FSDataInputStream`, `FileStatus`, and `TRASH_PREFIX`.

Control flow: setup assigns `fsTarget` to local FS before the base class creates mount points and `fsView`. Teardown deletes the local test root. `testNflyWriteSimple` mounts `/nflyroot` to two local target URIs, writes one file through viewfs, lists the NFly root, and verifies both replicas contain the same UTF string. `testNflyInvalidMinReplication` configures a min replication higher than target count and expects an `IOException` mentioning minimum replication.

State and persistence: creates and deletes local test directories/files. Trash root behavior is overridden for local fallback semantics.

Dependencies and integration: covers the full base `ViewFileSystem` suite plus NFly link creation and validation.

Risks and test signals: likely regressions include local cleanup leaks, NFly replication misconfiguration not rejected, write fanout failure, or local fallback trash root mismatches.
