## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFSMainOperationsLocalFileSystem.java

Purpose: binds the shared `FSMainOperationsBaseTest` contract to Hadoop's `LocalFileSystem`, providing broad inherited coverage for main `FileSystem` operations on the local implementation.

Important APIs/types/functions: `FSMainOperationsBaseTest`, `FileSystem.getLocal`, `Configuration`, `Path`, `createFileSystem`, and `getDefaultWorkingDirectory`.

Control flow: the subclass overrides only two hooks. `createFileSystem` returns a fresh local filesystem from a new configuration. `getDefaultWorkingDirectory` lazily caches the local filesystem working directory in a static `Path wd`.

State and persistence: inherited tests create and delete local filesystem data according to the base class. This subclass adds static caching of the working directory, which can persist across test methods in the same JVM.

Dependencies/integration points: integration point is the test framework's abstract filesystem contract. It ensures local FS behavior stays aligned with common operations expected from all Hadoop `FileSystem` implementations.

Risks and test signals: most behavior and risk live in the base class. The subclass risk is stale static working-directory state if the process working directory or local FS configuration changes during a test run.
