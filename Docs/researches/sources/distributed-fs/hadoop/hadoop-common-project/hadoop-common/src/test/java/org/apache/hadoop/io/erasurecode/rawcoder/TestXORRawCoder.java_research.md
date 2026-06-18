
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoder.java

Purpose: Binds the shared XOR raw-coder test matrix to the pure Java XOR implementation.

Important APIs and types: Extends `TestXORRawCoderBase` and selects `XORRawErasureCoderFactory` for both encoder and decoder factory fields.

Control flow: Setup assigns factories. Inherited tests cover 10x1 data erasure, parity erasure, data unit 5 erasure, too-many-erasure failure, bad input, and bad output cases across mixed direct and heap buffers.

State and persistence: Uses inherited in-memory chunk and coder state only.

Dependencies and integration points: Validates the Java XOR raw coder factory used by codec registry fallback paths.

Risks: The class has no custom assertions; all behavior is inherited. Factory asymmetry issue in the base does not affect this symmetric class.

Test signals: Standard Java XOR coverage for recoverability, invalid erasures, corruption handling, and buffer compatibility.
