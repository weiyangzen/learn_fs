# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestUTF8ByteArrayUtils.java

Purpose: Unit tests for byte-level search helpers in `UTF8ByteArrayUtils`. Despite the class name, the tests focus on ASCII byte arrays and index/range behavior for single bytes, byte sequences, and nth-byte lookup.

Important APIs/types/functions: Tests call `findByte(byte[], int, int, byte)`, `findBytes(byte[], int, int, byte[])`, `findNthByte(byte[], int, int, byte, int)`, and the overload `findNthByte(byte[], byte, int)`. It extends `HadoopTestBase`, using its assertion conveniences.

Control flow: Each method builds `"Hello, world!"` as bytes and asserts both hit and miss results. Search ranges are varied to ensure `findBytes()` respects the start offset, while nth-byte tests verify second and third matches and return `-1` when the requested occurrence is absent.

State and persistence behavior: Stateless pure-function tests. No mutable global state, filesystem state, or encoding-sensitive persistence is involved beyond `String.getBytes()` using the platform default encoding for ASCII content.

Dependencies and integration points: Depends on Hadoop utility search functions and JUnit. These byte-search helpers are typically used by text parsers that operate on UTF-8 buffers without materializing strings.

Risks: Default charset use is harmless for ASCII literals but would be risky for non-ASCII UTF-8 cases; this test does not cover multibyte code points, empty patterns, negative offsets, or upper-bound edge cases. It also does not verify behavior when pattern length exceeds the search window.

Test signals: Expected hit indexes `4`, `1`, `3`, and `10`, plus `-1` misses, provide simple regression signals for range scanning and occurrence counting.
