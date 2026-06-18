<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReconstructor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReconstructor.java

## Purpose

`StripedReconstructor` is the abstract base for DataNode EC reconstruction tasks. It owns common configuration, block-group geometry, source reader, decoder, optional validation, buffer pool, position tracking, live/excluded bitsets, and reconstruction metrics.

## Important APIs, Types, And Functions

- Constructor builds live and exclusion bitsets, stores block group/policy, creates `StripedReader`, configures caching, and determines validation enablement.
- `initDecoderIfNecessary` creates the raw erasure decoder; `initDecodingValidatorIfNecessary` wraps it with `DecodingValidator` when enabled.
- `getBlock(int)` and `getBlockLen(int)` map EC internal indices to `ExtendedBlock`s and lengths.
- Buffer APIs allocate/free from a static `ElasticByteBufferPool` and use decoder direct-buffer preference.
- Metric APIs increment/read total bytes read, remote bytes read, and bytes written.

## Control Flow

Subclasses call decoder and reader initialization, then repeatedly read, decode, checksum or write, update position, and clear buffers. The base exposes common helpers for network addresses, checksum, read service, xmits, validation, and buffer mark/reset around validation.

## State And Persistence

State includes DataNode/config/policy/block group, coder options, decoder/validator, reader, caching strategy, position, max target length, live/exclude bitsets, and byte counters. It does not persist blocks directly; subclasses perform writes or checksum output.

## Dependencies And Integration Points

It integrates `ErasureCodingWorker`, `StripedReader`, Hadoop raw erasure coding, `StripedBlockUtil`, `ByteBufferPool`, DataNode networking, checksum, and EC reconstruction metrics.

## Risks And Edge Cases

Validation is disabled when coder options allow input mutation. The decoder must be released in cleanup. Shared static buffer pool means buffer leaks affect other tasks. Live/exclude bitsets are derived from byte arrays and depend on valid internal block indices.

## Test Signals

Tests should cover block/length mapping, direct versus heap allocation, decoder lifecycle, validation enablement, metric increments, bitset construction, position/max-target updates, and buffer mark/reset helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReconstructor.java -->
