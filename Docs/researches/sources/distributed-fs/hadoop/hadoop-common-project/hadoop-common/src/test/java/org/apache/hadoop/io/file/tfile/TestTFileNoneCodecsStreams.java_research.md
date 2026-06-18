
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsStreams.java

Purpose: Runs the streaming TFile API base suite without compression.

Important APIs and types: Extends `TestTFileStreams` and configures `Compression.Algorithm.NONE` with `memcmp`.

Control flow: `setUp()` initializes inherited compression and comparator settings, then delegates to stream base setup. Inherited tests write records through prepared key/value streams with known, unknown, and mixed lengths; read them with byte-array helpers; and assert failures for missing values, value-before-key, length mismatches, oversized keys, repeated close, negative offsets, and compression checks.

State and persistence: Uses inherited temp file creation, writer state, and deletion in teardown.

Dependencies and integration points: Provides baseline coverage for TFile stream append semantics without codec buffering effects.

Risks: No custom assertions beyond base suite. Compression-not-working tests skip compressed-size comparison for none codec.

Test signals: Baseline streaming API regression coverage for uncompressed TFiles.
