# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawEncoder.java

Purpose: pure-Java XOR encoder that computes one parity output by XORing all data inputs.

Important APIs/types/functions: constructor; `doEncode(ByteBufferEncodingState)`; `doEncode(ByteArrayEncodingState)`.

Control flow: encoding zeroes outputs, copies the first input into output, then XORs each subsequent input byte over the same output positions. It uses absolute buffer access so caller positions are left for the base class to advance.

State and persistence: stateless.

Dependencies and integration: extends `RawErasureEncoder`, uses `CoderUtil`, and is produced by `XORRawErasureCoderFactory`.

Risks: assumes a single parity output; if configured with multiple parity units, only output 0 is filled while validation would permit the output array length. Tests should assert intended parity-unit constraints at higher layers, direct/heap equality, non-zero output clearing, and odd data lengths.
