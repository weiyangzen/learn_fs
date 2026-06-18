# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/util/HHUtil.java

Purpose: static utility methods for Hitchhiker-XOR piggyback partitioning, piggyback generation, buffer allocation, and valid-input discovery.

Important APIs and control flow: `initPiggyBackIndexWithoutPBVec()` partitions data units across parity-derived piggyback sets; `initPiggyBackFullIndexVec()` maps each data unit to its piggyback set. `getPiggyBacksFromInput()` repeatedly builds temporary input/output buffers, uses a raw encoder to encode each piggyback group, clones selected parity output, and restores input positions. `getPiggyBackForDecode()` derives the piggyback needed for single-erasure recovery from read parity and decoded parity, using GF addition. `findFirstValidInput()` returns the first non-null input or throws `HadoopIllegalArgumentException`.

State and persistence: stateless utility, but methods allocate temporary heap/direct buffers and mutate positions on temporary and passed buffers carefully.

Dependencies and integration: used by HH-XOR encoding/decoding steps; depends on `RawErasureEncoder`, `RSUtil.GF`, and `ByteBuffer`.

Risks and test signals: test partition indexes for varied data/parity counts, direct/heap clone behavior, input-position restoration, all-null input failures, and piggyback decode math. `numDataUnits / (numParityUnits - 1)` can be dangerous for unsupported parity counts.
