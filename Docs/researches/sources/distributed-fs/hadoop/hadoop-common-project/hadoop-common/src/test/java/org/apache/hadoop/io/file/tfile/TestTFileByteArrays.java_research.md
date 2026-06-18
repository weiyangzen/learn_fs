
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileByteArrays.java

Purpose: Base byte-array TFile test suite for sorted files, parameterized by compression and comparator subclasses.

Important APIs and types: Uses `TFile.Writer.append(byte[],...)`, `TFile.Reader`, `Reader.Scanner`, `Scanner.entry()`, `seekTo()`, `lowerBound()`, `createScannerByKey()`, metadata block APIs, and static helpers `writeRecords()`, `readRecords()`, and `composeSortedKey()`.

Control flow: Setup creates a sorted writer with a configured codec and comparator. Tests cover empty files, one/two/multiple block boundaries, locate/seek behavior, reading key/value in different orders, repeated key reads, writer-not-closed failures, duplicate metablocks, missing metablocks, write-after-metablock rejection, single-read value behavior, bad codecs, empty/random file open failures, oversized keys, out-of-order keys, negative offsets/lengths, compression effectiveness, and nonzero output stream position.

State and persistence: Writes temp files named by subclass, tracks expected records per block, and deletes unless `skip` is set.

Dependencies and integration points: Base for gz, none, LZO, and jclass comparator variants; uses `ZlibFactory` to adjust expected block counts.

Risks: Many negative tests catch broad `Exception`, reducing diagnostic precision. Block-count expectations depend on native zlib presence and compression output.

Test signals: High-value regression coverage for TFile byte-array API, scanner behavior, validation, and format errors.
