# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/InputBuffer.java

Purpose: `InputBuffer` is a reusable `FilterInputStream` over caller-supplied byte arrays. It avoids allocating a new `ByteArrayInputStream` for repeated in-memory reads.

Important APIs and types: the private `Buffer` subclass extends `ByteArrayInputStream` and exposes `reset(byte[] input, int start, int length)`, `getPosition()`, and `getLength()`. Public `InputBuffer.reset(byte[], int)` and `reset(byte[], int, int)` retarget the stream to new data, while `getPosition()` and `getLength()` expose the underlying `pos` and `count`.

Control flow: construction creates an empty `Buffer` and passes it to `FilterInputStream`. Each reset swaps the `ByteArrayInputStream` backing `buf`, sets `count` to `start + length`, and resets `mark` and `pos` to `start`, so subsequent inherited `read`, `skip`, `available`, and mark/reset behavior operates on the new byte range.

State and persistence: state is in-memory only: the current backing array reference, start/mark, position, and limit. It does not copy input bytes, so later mutation of the caller's byte array affects reads. There is no persistence or close-owned resource beyond the filter stream wrapper.

Dependencies and integration points: depends only on Java IO plus Hadoop audience/stability annotations. It is paired with `DataInputBuffer` and `OutputBuffer` and is suitable for HDFS/MapReduce internal serialization paths that repeatedly decode transient byte arrays.

Risks and test signals: risks include exposing mutable input without copying, accepting invalid `start + length` combinations until inherited read paths encounter array bounds behavior, and confusing `getLength()` because it returns the absolute limit (`count`), not remaining bytes. Tests should cover resets with nonzero starts, position movement after reads/skips, reuse across multiple arrays, and caller mutation visibility.
