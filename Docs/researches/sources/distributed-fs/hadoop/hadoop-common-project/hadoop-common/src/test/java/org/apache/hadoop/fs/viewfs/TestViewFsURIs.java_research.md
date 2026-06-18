# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsURIs.java

Purpose: regression test for viewfs initialization when a target URI has an authority but an empty path, such as `file://foo`.

Important APIs and types: `ConfigUtil.addLink`, `FileContext.getFileContext`, `FsConstants.VIEWFS_URI`, `Configuration`, and `URI`.

Control flow: the test adds `/user -> file://foo` to an in-memory config and opens a `FileContext` for `viewfs:///`. The absence of an exception is the assertion.

State and persistence: no filesystem mutation. The test only validates URI parsing and mount-table construction.

Dependencies and integration: protects `ViewFs`/`InodeTree` URI normalization for authority-only targets. That matters for filesystems where authority is meaningful and the root path may be omitted in configuration.

Risks and test signals: if this fails, viewfs may reject legal target URIs or require a slash path where Hadoop callers historically did not. Because the test has no explicit assertions, any thrown exception is the signal.
