# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestPath.java

Purpose: comprehensive unit tests for Hadoop `Path` parsing, normalization, URI conversion, glob escaping, Windows handling, serialization, Avro reflection, qualification, and path merging.

Important APIs/types/functions: `Path` constructors, `toString`, `toUri`, `isAbsolute`, `getParent`, `getName`, `makeQualified`, `mergePaths`, `suffix`, `isWindowsAbsolutePath`, `FileSystem.globStatus`, `listStatus`, Java serialization, and `AvroTestUtil.testReflect`.

Control flow/state/persistence: most tests are pure string/URI assertions. Filesystem-backed glob tests create local directories including a literal `*` name, compare `listStatus` and escaped/unescaped `globStatus`, and clean through temp-root usage. Platform-specific tests use Windows/non-Windows assumptions. Serialization uses byte-array streams; Avro sets trusted package system property.

Dependencies/integration points: integrates with Java `URI`, local filesystem globbing, Hadoop config constants, shell platform flags, and Avro reflection.

Risks/test signals: high signal for path compatibility. It catches normalization drift, colon/drive-letter ambiguity, dot-segment resolution bugs, fragment/query encoding mistakes, reserved character handling, escaped glob misbehavior, Windows absolute detection, merge semantics across schemes/authorities, and serialization contract breakage.
