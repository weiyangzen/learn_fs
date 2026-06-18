# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/EncodingState.java

Purpose: base package-private state for encode operations, storing the encoder and logical `encodeLength`, with shared input/output count validation.

Important APIs/types/functions: fields `encoder`, `encodeLength`; generic `checkParameters(T[] inputs, T[] outputs)`.

Control flow: validation requires input count to equal `encoder.getNumDataUnits()` and output count to equal `encoder.getNumParityUnits()`. Buffer-specific subclasses handle null, length, directness, and offset details.

State and persistence: per-call in-memory only.

Dependencies and integration: superclass of `ByteBufferEncodingState` and `ByteArrayEncodingState`; used before all Java/native/dummy encoder dispatch.

Risks: limited to count checks; tests must include subclass validation to catch invalid buffers. Exception text is generic, so higher-level tests should rely on behavior rather than overly strict messages unless needed for compatibility.
