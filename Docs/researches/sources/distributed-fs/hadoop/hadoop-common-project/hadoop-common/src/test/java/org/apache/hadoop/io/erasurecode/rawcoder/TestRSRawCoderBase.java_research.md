
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderBase.java

Purpose: Shared Reed-Solomon raw-coder matrix covering many erasure patterns and buffer contracts.

Important APIs and types: Extends `TestRawCoderBase` and defines JUnit tests that call `prepare()`, `testCodingDoMixAndTwice()`, `testCodingWithErasingTooMany()`, and `testInputPosition()`.

Control flow: Tests cover 6x3 erasures of all data units, single data units, mixed data/parity units, all parity units, multiple parity units, and 10x4 data/parity erasure. Most run direct then heap buffers twice. A negative case erases more units than parity width and expects failure. Input-position coverage asserts consumed buffers have no remaining bytes after encode/decode.

State and persistence: Relies on inherited mutable erased-index arrays, buffer mode, chunk size, coders, and generated chunks.

Dependencies and integration points: Inherited by legacy Java, new Java, native, and intended interoperability RS test classes.

Risks: Method names prefixed with `testCodingNegative` can still expect success in one case; only the too-many-erasure case is negative. Factory asymmetry may be masked by base decoder creation.

Test signals: Broad RS contract coverage across recovery combinations and ByteBuffer modes.
