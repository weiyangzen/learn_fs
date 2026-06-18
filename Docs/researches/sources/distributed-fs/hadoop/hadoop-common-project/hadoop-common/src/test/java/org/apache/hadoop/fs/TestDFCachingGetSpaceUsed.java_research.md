## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFCachingGetSpaceUsed.java

Purpose: verifies that `CachingGetSpaceUsed.Builder` can instantiate `DFCachingGetSpaceUsed`, initialize it against a real local file, and report a non-trivial used-space value. It is a narrow integration test for the `GetSpaceUsed` builder path that selects a concrete implementation class.

Important APIs/types/functions: `CachingGetSpaceUsed.Builder`, `GetSpaceUsed`, `DFCachingGetSpaceUsed`, `FileUtil.fullyDelete`, `GenericTestUtils.getTestDir`, `RandomAccessFile`, and `RandomStringUtils.randomAlphabetic`. The helper `writeFile` creates and fsyncs a local file of roughly `FILE_SIZE` bytes before the builder is invoked.

Control flow: `setUp` deletes and recreates the test directory, `testCanBuildRun` writes a file, builds the space-used implementation with a long refresh interval, checks the runtime type and usage lower bound, and closes the instance. `tearDown` deletes the directory.

State and persistence: the test creates local files under the Hadoop test directory and explicitly syncs file contents to disk, so the space-used query is not racing only buffered data. The `DFCachingGetSpaceUsed` instance likely starts background/cache state and is explicitly closed.

Dependencies/integration points: depends on local filesystem semantics, disk accounting via `df`, and the Hadoop `FileUtil` cleanup helper. It exercises the builder's reflection/class-selection integration with `DFCachingGetSpaceUsed`.

Risks and test signals: the assertion allows a small slack below `FILE_SIZE`, but still depends on platform disk accounting and test-directory writability. A regression would show as build failure, wrong implementation type, negative/zero reported usage, or leaked background resources if `close` behavior changes.
