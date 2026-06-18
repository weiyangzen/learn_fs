
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsStreams.java

Purpose: Runs the streaming TFile API base suite with LZO compression when supported.

Important APIs and types: Extends `TestTFileStreams`, uses `Compression.Algorithm.LZO.isSupported()`, and configures inherited writer with LZO plus `memcmp`.

Control flow: `setUp()` sets `skip` when LZO is unavailable; otherwise it initializes compression/comparator and calls the base streaming setup. Inherited tests write keys and values through `prepareAppendKey()` and `prepareAppendValue()` with known and unknown lengths, then exercise negative stream-state and size validation cases.

State and persistence: Uses inherited temp file and writer lifecycle. Skipped tests return early via the inherited `skip` flag.

Dependencies and integration points: Covers optional LZO support in TFile's streaming append APIs.

Risks: Manual skip prints output rather than reporting an assumption. Coverage is absent on hosts without LZO.

Test signals: Streaming API regression coverage under LZO compression when the codec is installed.
