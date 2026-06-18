# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestLimitInputStream.java

Purpose: tests `LimitInputStream`, an `InputStream` wrapper that stops reads after a configured byte limit.

Important APIs and types: `LimitInputStream`, `InputStream.read()`, `read(byte[],int,int)`, `reset`, and a deterministic `RandomInputStream`.

Control flow: `testRead` verifies a zero limit returns EOF immediately and a positive limit delegates the first byte to the wrapped stream. `testResetWithoutMark` confirms reset without a mark raises `IOException`. `testReadBytes` reads four bytes and compares them to bytes generated from the same seeded random stream.

State and persistence: state is the remaining-byte counter and any mark/reset state inside the wrapper. No persistence is used.

Dependencies and integration points: extends `HadoopTestBase` for assertions and uses Java stream semantics.

Risks: off-by-one limit handling can allow extra bytes or premature EOF; byte-array reads can ignore limits; reset can incorrectly restore state without mark support. Test signals are EOF, exception, and deterministic byte equality checks.
