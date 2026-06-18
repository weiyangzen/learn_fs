# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestGetUriFromString.java

Purpose: this unit test validates `Util.stringAsURI(String)` for relative paths, absolute Unix paths, absolute Windows paths, and already-formed file URIs.

Important APIs and types: `Util.stringAsURI`, `URI`, JUnit assertions, and SLF4J logging. Constants encode representative path inputs and expected URI scheme/path values.

Control flow: `testRelativePathAsURI` only asserts that a relative string produces a non-null URI. `testAbsolutePathAsURI` feeds Windows and Unix absolute path strings and asserts that both become `file` scheme URIs. `testURI` passes valid Unix and Windows-style `file://` URIs and checks both scheme and decoded path, including `%20` decoding for spaces.

State and persistence: no persistent state exists. The tested utility may consult platform path behavior, but the test expects platform-independent handling for the supplied strings.

Dependencies and integration points: this is a narrow compatibility guard for common HDFS storage/config parsing code that accepts user-provided path or URI strings. It protects callers that pass checkpoint/name/data directory paths in either URI or local-path form.

Risks: the relative-path test does not assert scheme/path details, so regressions in relative-path normalization might slip through. Windows path behavior is tested on any OS using string shape rather than the host filesystem, which is useful but may not catch every Java URI edge case.

Test signals: failures indicate `Util.stringAsURI` no longer preserves file scheme expectations or decodes URI paths as callers expect.
