# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestVLong.java

## Purpose
`TestVLong` verifies TFile variable-length long encoding and decoding through `Utils.writeVLong()` and `Utils.readVLong()`. It checks exact encoded sizes for edge ranges and performs a large randomized round trip.

## Important APIs, Types, and Functions
The test uses Hadoop `FileSystem`, `Path`, `FSDataOutputStream`, and `FSDataInputStream` over a `GenericTestUtils` test directory. `writeAndVerify(int shift)` serializes every `short` value shifted by a byte-aligned amount and then reads the sequence back. `verifySixOrMoreBytes(int bytes)` covers larger encodings. Test methods cover byte, short, 3- through 8-byte encodings, and random long masks.

## Control Flow
`setUp()` creates a local test path and removes any stale output; `tearDown()` removes it again. Each deterministic test writes a contiguous range, closes the stream, reopens it, validates all decoded values in order, and asserts the final file length against a formula for the expected encoding width. `testVLongRandom()` creates one million random masked longs, writes them sequentially, and validates the full stream round trip.

## State and Persistence
Persistent state is limited to a temporary file named `TestVLong` under the test directory. There is no shared static mutable state beyond `ROOT`; every test deletes the file to avoid cross-test contamination.

## Dependencies and Integration Points
The file integrates with Hadoop local filesystem streams and the TFile `Utils` encoding implementation. The encoded-size assertions are a compatibility signal for TFile binary format behavior.

## Risks and Edge Cases
The tests assume exact byte-length formulas for signed values around byte and short boundaries. Random generation uses an unseeded `Random`, so failures may be less reproducible. `1L << 64` in the random mask path effectively wraps Java shift distance, which makes the full-64-bit case behave as a one-bit mask rather than all bits.

## Test Signals
Strong signals are exact encoded file lengths for each width, no read/write mismatch across negative and positive ranges, and successful randomized round trips over one million values.
