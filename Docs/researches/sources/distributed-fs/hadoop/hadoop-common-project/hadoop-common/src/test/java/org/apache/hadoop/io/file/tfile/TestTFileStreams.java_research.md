
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileStreams.java

Purpose: Base streaming API suite for TFile prepared key/value append streams, parameterized by compression subclasses.

Important APIs and types: Uses `TFile.Writer.prepareAppendKey()`, `prepareAppendValue()`, `TFile.Reader.Scanner`, `TestTFileByteArrays.readRecords()`, `WritableUtils`, and stream exceptions such as `EOFException`.

Control flow: Setup creates a writer with configured compression and comparator. Tests write no entries, one/two entries with known, unknown, and mixed key/value lengths, then read through byte-array helpers. Negative tests cover key without value, value without key, length mismatches, key/value too long or short, idempotent close, oversized 64K keys, negative read offsets, and compressed size checks.

State and persistence: Maintains writer/output stream fields and temp file path, closing and deleting in teardown unless skipped by subclasses.

Dependencies and integration points: Base for none and LZO stream variants, and indirectly validates TFile stream-state machine.

Risks: Many negative tests catch broad exceptions. Unknown-length read behavior has a TODO noting inconsistency around `getValueLength()`.

Test signals: High-value coverage of streaming writer state transitions and validation errors.
