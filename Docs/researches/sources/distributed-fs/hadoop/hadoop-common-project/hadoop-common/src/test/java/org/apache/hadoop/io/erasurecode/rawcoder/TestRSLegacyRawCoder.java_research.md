
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSLegacyRawCoder.java

Purpose: Binds the shared RS raw-coder test matrix to the legacy Java Reed-Solomon implementation.

Important APIs and types: Extends `TestRSRawCoderBase` and selects `RSLegacyRawErasureCoderFactory` for both encoder and decoder factories.

Control flow: `@BeforeEach` sets factories and disables verbose dumps. All actual encode/decode, erasure, buffer, negative, and input-position tests are inherited from `TestRSRawCoderBase` and `TestRawCoderBase`.

State and persistence: No additional state beyond inherited coder and chunk fields. All data is in memory.

Dependencies and integration points: Ensures the older Java RS factory remains compatible with the same public raw-coder contracts as newer Java and native implementations.

Risks: Because this class only configures the base, any inherited test gaps apply here. Legacy-specific edge cases are not isolated.

Test signals: Provides regression signal that legacy RS still handles the standard 6x3 and 10x4 erasure matrix, mixed buffers, too-many erasures, and input position advancement.
