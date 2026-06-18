## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBPartHandle.java

Purpose: provides a private, unstable `PartHandle` implementation backed by a byte array for multipart upload part identifiers.

Important APIs and types: static `from(ByteBuffer)` creates a `PartHandle`; `bytes()` returns a new `ByteBuffer` wrapping the stored array; equality compares against any `PartHandle` by `ByteBuffer.equals`; `hashCode()` uses `Arrays.hashCode`.

Control flow: construction stores `byteBuffer.array()` directly. Reads wrap that same byte array for consumers.

State and persistence behavior: state is the byte array representing the serialized part handle. It is serializable through the `PartHandle` contract but has no external persistence logic.

Dependencies and integration points: used by multipart upload code that needs a simple byte-buffer-backed handle representation.

Risks: `ByteBuffer.array()` requires an array-backed buffer and ignores buffer position/limit, so direct, read-only, sliced, or offset buffers can fail or capture extra bytes. The stored array is not defensively copied, so mutations to the original backing array can mutate the handle. `ByteBuffer.equals` is position/limit-sensitive, making equality dependent on returned buffer state.

Test signals: cover array-backed input, direct/read-only rejection, position/limit behavior, equality with another handle, hash stability, and mutation of the original buffer backing array.
