
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeRSRawCoder.java

Purpose: Concrete test class for native ISA-L Reed-Solomon raw encoder and decoder behavior.

Important APIs and types: Extends `TestRSRawCoderBase`, selects `NativeRSRawErasureCoderFactory`, gates setup with `ErasureCodeNative.isNativeCodeLoaded()`, and uses inherited RS erasure matrix tests plus an explicit release test.

Control flow: Setup skips when native code is unavailable and enables dumps. It inherits most RS raw-coder cases but redeclares them, preparing 6x3 or 10x4 layouts and running mixed direct/heap buffer tests twice. `testAfterRelease63()` prepares a 6x3 coder, releases encoder and decoder, and expects subsequent calls to fail with closed IOExceptions.

State and persistence: Native coder instances may allocate native resources and are released by tests. Chunk data remains in memory.

Dependencies and integration points: Covers Hadoop native erasure-code loading and native RS raw factory integration.

Risks: Test coverage depends on native library availability. Duplicate inherited test definitions increase maintenance cost.

Test signals: Strong native RS recoverability, buffer compatibility, too-many-erasure failure, and release semantics.
