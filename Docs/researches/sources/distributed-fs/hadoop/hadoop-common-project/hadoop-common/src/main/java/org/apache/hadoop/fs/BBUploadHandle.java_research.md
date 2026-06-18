## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BBUploadHandle.java

Purpose: private, unstable `UploadHandle` implementation backed by a byte array for multipart upload session identifiers.

Important APIs and types: static `from(ByteBuffer)` creates an `UploadHandle`; `bytes()` returns a wrapped `ByteBuffer`; `equals` accepts any `UploadHandle`; `hashCode` hashes the raw byte array.

Control flow: constructor stores `byteBuffer.array()` directly and later exposes that array through `ByteBuffer.wrap`.

State and persistence behavior: the only state is the backing byte array. The class has no storage or lifecycle behavior beyond the serializable handle contract.

Dependencies and integration points: integrates with Hadoop multipart upload APIs as a simple upload session token representation.

Risks: same buffer hazards as `BBPartHandle`: direct/read-only buffers cannot be converted, position/limit are ignored on input, the backing array is not copied, and equality is tied to `ByteBuffer` remaining-byte semantics.

Test signals: verify construction from ordinary buffers, failure for unsupported buffer kinds, immutability expectations under backing-array mutation, equality against other `UploadHandle` implementations, and hash/equality consistency.
