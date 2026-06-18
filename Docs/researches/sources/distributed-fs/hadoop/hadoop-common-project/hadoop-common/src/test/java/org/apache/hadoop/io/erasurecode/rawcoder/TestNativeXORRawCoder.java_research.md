
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeXORRawCoder.java

Purpose: Concrete test class for native XOR raw erasure coder behavior.

Important APIs and types: Extends `TestXORRawCoderBase`, selects `NativeXORRawErasureCoderFactory`, checks `ErasureCodeNative.isNativeCodeLoaded()`, and adds `testAfterRelease63()`.

Control flow: Setup skips the class when native code is absent and enables verbose dumps. It inherits XOR raw-coder tests for data erasure, parity erasure, too-many-erasure failure, and bad input/output cases. The release test prepares a 6x3 configuration and verifies encode/decode after `release()` fail.

State and persistence: Native coder resources are created and released; test data is in-memory chunks.

Dependencies and integration points: Exercises the native XOR factory and native-code load path.

Risks: Native availability controls whether meaningful tests run. The release test uses a 6x3 layout even though inherited normal XOR tests use 10x1, so it stresses configuration acceptance differently.

Test signals: Covers native XOR compatibility with the shared XOR matrix and resource lifecycle.
