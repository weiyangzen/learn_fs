# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestPureJavaCrc32C.java

Purpose: validates initial/reset behavior for Hadoop's `PureJavaCrc32C` and includes a manual benchmark against JDK `CRC32C`.

Important APIs and types: `PureJavaCrc32C`, `CRC32C`, `Checksum`, nested `PerformanceTest`, reflection constructors, and `SubjectInheritingThread`.

Control flow: the active JUnit test creates a checksum, records its initial value, resets it, and verifies the reset value matches initialization. The nested benchmark generates random data up to 32 MiB, warms both implementations, measures multiple chunk sizes and thread counts, and checks the pure-Java checksum value equals the JDK baseline for every run.

State and persistence: no persisted state; benchmark state is local buffers and thread result arrays.

Dependencies and integration points: supports Hadoop's CRC32C fallback path where native CRC is unavailable and lets maintainers compare performance manually.

Risks: this unit file has minimal active correctness coverage beyond reset equivalence; arithmetic correctness is mainly guarded elsewhere. Test signals are the reset assertion and benchmark runtime value checks when manually executed.
