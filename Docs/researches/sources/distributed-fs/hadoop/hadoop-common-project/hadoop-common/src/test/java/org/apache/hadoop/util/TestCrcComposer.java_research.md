<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCrcComposer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCrcComposer.java

## Purpose

`TestCrcComposer.java` validates composing per-chunk CRCs into whole-file or striped cell CRCs.

## Important APIs, Types, and Functions

The suite uses `CrcComposer.newCrcComposer`, `newStripedCrcComposer`, `update` overloads for byte arrays, `DataInputStream`, and single CRC ints, `digest`, `CrcUtil.readInt/writeInt`, and `DataChecksum.Type.CRC32C`.

## Control Flow

Setup generates deterministic random data, computes full CRC, chunk CRCs, and cell CRCs. Tests feed CRCs by different update APIs, handle final partial chunks with smaller byte counts, and compare the digest against full or cell-level expected values. Negative tests intercept unaligned byte-array lengths and stripe-boundary mismatches.

## State and Persistence Behavior

State is per-test random data arrays, computed CRC arrays, and composer internal accumulated CRC/cell state. No persistence exists.

## Dependencies and Integration Points

It integrates with `DataChecksum`, `CrcComposer`, `CrcUtil`, `LambdaTestUtils`, Java streams, and JUnit timeouts.

## Risks and Edge Cases

The highest risks are partial final chunks, wrong chunk-size metadata, crossing stripe boundaries without a matching CRC, and byte-array lengths not divisible by CRC size.

## Test Signals

Signals include digest equality to full CRC, striped digest equality to expected cell CRC bytes, multi-stage composition, and expected exceptions for invalid update shapes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestCrcComposer.java -->
