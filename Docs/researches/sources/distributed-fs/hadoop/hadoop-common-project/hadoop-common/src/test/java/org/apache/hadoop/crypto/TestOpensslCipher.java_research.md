# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestOpensslCipher.java

## Purpose
`TestOpensslCipher` validates native OpenSSL cipher construction, input/output buffer preconditions, finalization preconditions, and suite support metadata.

## Important APIs, Types, and Functions
It exercises `OpensslCipher.getLoadingFailureReason()`, `OpensslCipher.getInstance(String)`, `init(int, byte[], byte[])`, `update(ByteBuffer, ByteBuffer)`, `doFinal(ByteBuffer)`, and `OpensslCipher.isSupported(CipherSuite)`. Static AES key and IV fixtures drive initialization.

## Control Flow
Each test assumes OpenSSL loaded successfully. `testGetInstance()` checks valid `AES/CTR/NoPadding`, invalid algorithm (`AES2`), and invalid padding. `testUpdateArguments()` initializes encryption, verifies heap buffers are rejected, then verifies insufficient direct output capacity throws `ShortBufferException`. `testDoFinalArguments()` verifies a heap output buffer is rejected. `testIsSupportedSuite()` checks `UNKNOWN` is false and AES CTR is supported.

## State and Persistence
The tests allocate local heap and direct `ByteBuffer` instances and native cipher state. They do not persist data outside the process.

## Dependencies and Integration Points
Dependencies include OpenSSL native bindings, Java `ByteBuffer`, JCE exception types, `CipherSuite`, `GenericTestUtils.assertExceptionContains`, and JUnit assumptions/assertions.

## Risks and Edge Cases
Native loading makes the suite environment-sensitive. The key edge cases are direct-buffer requirements and output capacity checks, both critical because the native layer cannot safely operate on arbitrary Java buffers.

## Test Signals
Passing tests signal correct error classification for unsupported cipher strings, strict direct-buffer validation, short-buffer handling, and advertised suite support for AES CTR.
