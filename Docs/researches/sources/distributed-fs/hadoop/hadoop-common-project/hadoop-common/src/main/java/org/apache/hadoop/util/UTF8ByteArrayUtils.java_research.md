# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/UTF8ByteArrayUtils.java

Purpose: `UTF8ByteArrayUtils` provides byte-level search helpers for UTF-8 encoded byte arrays, primarily for separator scanning without decoding to `String`.

Important APIs/types/functions: `findByte(byte[], int, int, byte)` returns the first matching byte in `[start,end)`. `findBytes(byte[], int, int, byte[])` returns the first occurrence of a byte sequence. `findNthByte(byte[], int, int, byte, int)` finds the nth occurrence within a bounded region. `findNthByte(byte[], byte, int)` scans the whole array.

Control flow: all methods use straightforward nested loops and return `-1` on no match. The nth-byte method repeatedly calls `findByte` starting after the previous match.

State and persistence behavior: stateless and allocation-free except call-stack locals.

Dependencies and integration points: depends only on Hadoop annotations. It is useful in text input parsing where delimiters are ASCII bytes embedded in UTF-8 data.

Risks: no input validation for null arrays, negative offsets, end beyond length, or empty pattern semantics. `findBytes` with an empty pattern returns `start` because the inner loop succeeds immediately. The methods do byte matching only and do not validate UTF-8 boundaries.

Test signals: tests should cover start/end bounds, missing matches, repeated delimiters, nth occurrence, empty pattern behavior, and delimiter bytes inside multibyte UTF-8 sequences if callers care.
