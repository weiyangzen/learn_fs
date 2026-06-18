## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSBuilder.java

Purpose: `FSBuilder<S, B>` is the public base interface for filesystem and file-context builders. It provides optional and mandatory typed key/value setters plus `build()`, while preserving binary compatibility with older overloaded numeric methods.

Important APIs and types: core abstract methods are `opt(String, String)`, `opt(String, String...)`, `must(String, String)`, `must(String, String...)`, and `build()`. Default overloads convert booleans to strings, ints and longs through `optLong`/`mustLong`, and doubles through `optDouble`/`mustDouble`. Deprecated float/double overloads intentionally cast to long for compatibility with previous linkage behavior.

Control flow, state, and persistence: the interface stores no state. Implementations decide how optional and mandatory options are retained and validated. Mandatory options are expected to make `build()` fail with `IllegalArgumentException` if unsupported or unavailable.

Dependencies and integration: `FSDataOutputStreamBuilder` and open/create builders extend or implement this interface. It integrates typed user-facing builder calls with implementation-specific option parsing in `AbstractFSBuilderImpl` and concrete filesystems.

Risks and test signals: overload resolution and numeric conversion are the main risks. Floating-point values passed to deprecated overloads lose precision by design. Tests should compile-call all overloads, assert resulting option strings in implementations, verify mandatory option rejection, and cover source/binary compatibility scenarios referenced by HADOOP-16202 and HADOOP-18724 comments.
