
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/codec/TestHHXORErasureCodec.java

Purpose: Verifies that `HHXORErasureCodec` creates encoder and decoder instances using the schema's data and parity unit counts.

Important APIs and types: Uses `ECSchema("hhxor", 10, 4)`, `ErasureCodecOptions`, `HHXORErasureCodec`, `createEncoder()`, `createDecoder()`, and `ErasureCoder.getNumDataUnits()/getNumParityUnits()`.

Control flow: A single JUnit test constructs the codec with a fresh `Configuration`, creates both coder directions, and asserts each exposes 10 data units and 4 parity units.

State and persistence: The schema and options are instance fields. There is no external state, file IO, or coder execution.

Dependencies and integration points: Connects the codec factory layer to `HHXORErasureEncoder` and `HHXORErasureDecoder` constructors through `HHXORErasureCodec`.

Risks: This is only a construction/configuration test; it does not validate HHXOR math, raw coder selection, buffer handling, or decoding outcomes.

Test signals: Useful smoke coverage for codec wiring and schema propagation.
