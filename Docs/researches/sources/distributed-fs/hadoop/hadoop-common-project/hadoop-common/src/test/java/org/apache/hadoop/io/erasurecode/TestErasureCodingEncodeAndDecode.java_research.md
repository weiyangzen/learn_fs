
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestErasureCodingEncodeAndDecode.java

Purpose: End-to-end smoke test for raw Reed-Solomon encoding and decoding over byte-array inputs for a 6 data, 3 parity layout.

Important APIs and types: Uses `CodecUtil.createRawEncoder()`, `CodecUtil.createRawDecoder()`, `ErasureCoderOptions`, `RawErasureEncoder.encode(byte[][], byte[][])`, and `RawErasureDecoder.decode(byte[][], int[], byte[][])`.

Control flow: The test generates 6 KB of random data, splits it into six 1 KB data blocks, encodes three parity blocks, composes all nine blocks, then iterates all single, double, and triple erasure combinations by nulling selected blocks and asserting decoded bytes equal the backed-up originals.

State and persistence: Mutates the shared `all` block array inside nested loops, restoring erased entries after each decode. No filesystem or durable state is touched.

Dependencies and integration points: Exercises the default RS raw coder selected through `CodecUtil` and `Configuration`, not a specific factory class.

Risks: The misspelled constants are cosmetic. Triple nested loops create broad coverage but can be slow if native or Java coder performance regresses.

Test signals: Strong signal that the configured RS raw coder can recover any erasure set up to parity width.
