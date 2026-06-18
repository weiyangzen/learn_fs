# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/PathData.java

Purpose: encapsulates a user path string, qualified `Path`, `FileSystem`, `FileStatus`, and existence flag while preserving user-facing path spelling better than `Path.toString()` alone.

Important APIs and types: constructors from `String` and local `URI`, `refreshStatus()`, `suffix()`, `parentExists()`, `representsDirectory()`, `getDirectoryContents()`, `getDirectoryContentsIterator()`, `getPathDataForChild()`, static `expandAsGlob()`, `toFile()`, `openForSequentialIO()`, and `openFile(policy)`.

Control flow: construction parses strings through `stringToUri()`, resolves filesystem, qualifies paths, and optionally looks up status. Glob expansion uses `fs.globStatus()`: null means non-glob missing path and returns one non-existing `PathData`; matches are converted back to schemeful, absolute schemeless, or relative strings based on input form. Directory listing preserves relative child strings, sorts array results, and offers iterator mapping for scalable listings.

State and persistence: `stat` and `exists` are mutable cached status values refreshed by `refreshStatus()`. No filesystem mutation occurs except indirectly through status/list/open calls.

Dependencies and integration: central to nearly every shell command. Uses `FileSystem`, `LocalFileSystem`, `RemoteIterator`, `FutureIO.awaitFuture`, open-file read policy and length options, Hadoop path exceptions, and custom URI parsing for `?`, `#`, Windows drive paths, and relative glob results.

Risks: cached `stat` can become stale unless refreshed. URI parsing intentionally differs from `new URI(String)` and must be regression-tested for Windows, escaped glob chars, schemes without authorities, relative paths, and paths containing URI-reserved characters. `toFile()` is valid only for `LocalFileSystem`. `compareTo()`/`equals()` use qualified `Path`, not preserved user string.

Test signals: cover missing path construction, glob null/empty/multiple behavior, relative and schemeful glob spelling, Windows absolute and backslash paths, directory child string preservation, `representsDirectory()` for slash/dot/dotdot, stale status refresh after delete/create, iterator listing, and open-file options.
