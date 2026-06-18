# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/coder/HHXORErasureDecodingStep.java

Purpose: implements HH-XOR chunk recovery logic using RS decoding plus piggyback XOR adjustments.

Important APIs and control flow: constructor computes `pbIndex`, piggyback partition indexes, and stores erased indexes plus raw coders. `performCoding()` converts chunks to buffers and exits early with no erasures. It reshapes flat input/output arrays into `[subPacket][unit]` matrices. Single data erasure uses `doDecodeSingle()`: decode second sub-packet with RS, derive a piggyback from read parity, recover first sub-packet by XORing the piggyback with surviving inputs, and advance input positions. Multiple erasures or parity erasures use `doDecodeMultiAndParity()`: RS-decode first sub-stripe, compute piggybacks, remove piggybacks from available parity, RS-decode second sub-stripe, then reapply/remove piggybacks for recovered parity outputs.

State and persistence: stores piggyback indexes, erased indexes, raw RS decoder, and XOR encoder. It mutates `ByteBuffer` contents and positions during coding; no persistence.

Dependencies and integration: depends on `HHUtil`, `RSUtil.GF`, `RawErasureDecoder`, and `RawErasureEncoder`. Created by `HHXORErasureDecoder`.

Risks and test signals: cover single data erasure, multiple data erasures, parity erasures, direct and heap buffers, buffer positions, and invalid array lengths. The method name typo `fisrtValidInput` is harmless; the substantive risk is position/index arithmetic and piggyback partition assumptions.
