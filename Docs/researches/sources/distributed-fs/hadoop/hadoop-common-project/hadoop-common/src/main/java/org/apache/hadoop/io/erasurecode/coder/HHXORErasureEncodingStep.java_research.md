# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureEncodingStep.java

Purpose: implements HH-XOR parity generation by RS-encoding sub-packets and adding piggybacks to selected second-sub-packet parity outputs.

Important APIs and control flow: constructor stores RS/XOR raw encoders and computes piggyback partition indexes. `performCoding()` converts chunks to buffers, validates flat input/output lengths as `dataUnits * 2` and `parityUnits * 2`, reshapes to sub-packet matrices, and calls `doEncode()`. `doEncode()` computes piggybacks from the first sub-packet with `HHUtil.getPiggyBacksFromInput()`, RS-encodes each sub-packet, then XORs piggybacks into second-sub-packet parity indexes 1..N.

State and persistence: stores piggyback index and raw encoders. Mutates output buffer content without changing the intended logical positions. No persistence.

Dependencies and integration: depends on `HHUtil`, `ECChunk`, `RawErasureEncoder`, and direct/heap `ByteBuffer` operations. Created by `HHXORErasureEncoder`.

Risks and test signals: test direct vs heap paths, parity count edge cases, invalid input/output lengths, and parity byte-for-byte compatibility with HH-XOR decode. Piggyback indexing assumes `numParityUnits > 1`.
