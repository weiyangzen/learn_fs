# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsConfig.java

Purpose: verifies invalid non-nested mount configuration is rejected. It protects the rule that, when nested mount points are disabled, a mount cannot be placed beneath an existing mount path.

Important APIs and types: `ConfigUtil.setIsNestedMountPointSupported`, `ConfigUtil.addLink`, `InodeTree`, `FileAlreadyExistsException`, and anonymous implementations of the `InodeTree` filesystem factory methods.

Control flow: the single test disables nested mount points, adds `/internalDir/linkToDir2` and a child `/internalDir/linkToDir2/linkToDir3`, then constructs an `InodeTree`. The constructor is expected to throw `FileAlreadyExistsException`.

State and persistence: all config is in-memory. The dummy `Foo` type and target factory methods are placeholders because tree construction should fail before real target use.

Dependencies and integration: this is a config-level guard for both `ViewFs` and `ViewFileSystem`, since they rely on `InodeTree` mount-table validation.

Risks and test signals: if this test fails by not throwing, ambiguous nested mount tables may be accepted when compatibility mode says they should not. If it throws a different exception, error classification for callers changes.
