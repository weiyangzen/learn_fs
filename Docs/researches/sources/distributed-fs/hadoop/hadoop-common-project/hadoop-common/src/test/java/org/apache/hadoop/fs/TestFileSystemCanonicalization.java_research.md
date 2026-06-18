## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemCanonicalization.java

Purpose: validates `FileSystem` URI canonicalization and `checkPath`/`makeQualified` compatibility across short hostnames, FQDNs, IP addresses, default ports, non-default ports, null authority, mismatched schemes, and authority inherited from the default FS.

Important APIs/types/functions: `FileSystem.getCanonicalUri`, `FileSystem.makeQualified`, `FileSystem.checkPath` indirectly, `NetUtils.getCanonicalUri`, `NetUtilsTestResolver.install`, `CommonConfigurationKeys.FS_DEFAULT_NAME_KEY`, and inner `DummyFileSystem`.

Control flow: `@BeforeAll` installs a deterministic resolver. Each test creates a `DummyFileSystem` from an authority and expected canonical URI, then calls `verifyPaths` over host and IP URI variants with/without ports. `verifyCheckPath` expects either successful qualification preserving authority or an `IllegalArgumentException` with `Wrong FS`.

State and persistence: no filesystem data is written. Static resolver state and `DummyFileSystem.defaultPort` define canonicalization behavior.

Dependencies/integration points: protects the name-resolution logic used by `FileSystem` path validation, especially how default port `123` is supplied. It integrates Hadoop net utilities with FS path qualification.

Risks and test signals: DNS/canonical-host behavior is normally unstable, so the test resolver is essential. Failures indicate path validation becoming too permissive or too strict, especially around default ports and default-FS authority fallback.
