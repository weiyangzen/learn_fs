
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoder.java

Purpose: Binds the shared RS raw-coder test matrix to the newer Java Reed-Solomon implementation.

Important APIs and types: Extends `TestRSRawCoderBase` and selects `RSRawErasureCoderFactory` for both encoder and decoder factories.

Control flow: Setup assigns factories and disables dumps. The inherited matrix generates chunks, encodes parity, erases data/parity combinations, decodes with least required inputs, checks unchanged inputs when required, validates recovered bytes, and tests input positions.

State and persistence: Uses inherited in-memory chunk state and newly created raw coders per test flow.

Dependencies and integration points: Verifies the default Java RS raw coder used by registry and configuration paths.

Risks: The class contains no Java-RS-specific assertions beyond the inherited contract. If factory fields diverge, note that `TestRawCoderBase.createDecoder()` currently instantiates `encoderFactoryClass`, so asymmetric tests may not behave as named.

Test signals: Standard RS recoverability and buffer-contract coverage for the Java implementation.
