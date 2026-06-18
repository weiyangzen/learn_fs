# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystemBasics.java

Purpose: builds minimal local HAR directory structures and tests `HarFileSystem` initialization, metadata caching, read-only semantics, path qualification, list status, version handling, and URI forms.

Important APIs/types/functions: `HarFileSystem`, `FileSystem.getLocal`, `_index`, `_masterindex`, `getHarVersion`, `getUri`, `getHomeDirectory`, `getWorkingDirectory`, `getMetadata`, `listLocatedStatus`, `makeQualified`, `FileContext.getFileContext`, and mutating methods expected to throw.

Control flow/state/persistence: setup creates a temp local root, a `.har` directory, empty index files, and writes the HAR version into `_masterindex`; teardown closes HAR and deletes the tree. Positive tests assert version/URI/home/working directory, metadata reuse for identical underlying FS, LRU eviction after `METADATA_CACHE_ENTRIES_DEFAULT + 1` archives, initialization without an explicit underlying FS, authority preservation, and fixture-based located-status listing from `/test.har`. Negative tests delete `_index`, overwrite `_masterindex` with unsupported version after a timestamp delay, and call mutation methods expecting `IOException`.

Dependencies/integration points: depends on local FS, HAR metadata cache, `Shell.WINDOWS` path adjustment, bundled `/test.har` resource, `FsPermission`, and `FileContext` registration of `har` URIs.

Risks/test signals: cache invalidation by modification time is timing-sensitive; unsupported-version tests rely on a one-second timestamp granularity delay. It signals regressions in HAR read-only guarantees, URI authority handling, metadata cache eviction, and initialization from classpath filesystem resources.
