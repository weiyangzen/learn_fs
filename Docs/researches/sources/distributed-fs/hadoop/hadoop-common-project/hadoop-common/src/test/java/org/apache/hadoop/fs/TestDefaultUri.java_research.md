## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDefaultUri.java

Purpose: tests `FileSystem` default URI parsing and the compatibility rule that a bare host without a scheme is treated as HDFS, while malformed bare-host paths with a trailing slash fail.

Important APIs/types/functions: `FileSystem.FS_DEFAULT_NAME_KEY`, `FileSystem.getDefaultUri`, `FileSystem.get`, `FileSystem.setDefaultUri` indirectly via config, `LocalFileSystem`, `UnsupportedFileSystemException`, and `LambdaTestUtils.intercept`.

Control flow: each test sets `fs.defaultFS` to a different string and then validates parsed URI scheme/authority or expected failure. Cases include `hdfs://nn_host`, a port, a trailing slash, bare `nn_host`, invalid `nn_host/`, `file:///`, and `FileSystem.get` on scheme-less values.

State and persistence: only mutates an instance `Configuration`; no filesystem state is written. The class-level configuration is reused across tests, so each test overwrites the relevant key before assertions.

Dependencies/integration points: documents the public configuration contract consumed by Hadoop clients, shell commands, and filesystem factory resolution. `file:///` integration confirms local filesystem lookup still works through `FileSystem.get`.

Risks and test signals: the bare-host-to-HDFS compatibility behavior is subtle and easy to break while tightening URI validation. The test method names contain `tet` typos but are still discovered through `@Test`. Expected exception messages are part of the behavioral contract.
