
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsByteArrays.java

Purpose: Runs the byte-array TFile base suite with LZO compression when LZO support is available.

Important APIs and types: Extends `TestTFileByteArrays`, uses `Compression.Algorithm.LZO.isSupported()`, and configures `init(LZO, "memcmp", 2605, 2558)`.

Control flow: `setUp()` sets `skip` if LZO is unsupported and prints `Skipped`; otherwise it initializes LZO compression, memcmp comparator, sampled block record counts, and delegates to base setup. Inherited tests then cover sorted byte-array behavior, negative cases, metadata, seeks, and compression checks.

State and persistence: Uses inherited temp file handling. If skipped, setup avoids writer creation and teardown avoids deletion.

Dependencies and integration points: Guards optional LZO integration in TFile without failing environments lacking the codec.

Risks: Expected records-per-block values are hard-coded and may drift with codec implementation changes. Skip is manual rather than JUnit assumptions.

Test signals: Full byte-array TFile behavior matrix under LZO when supported.
