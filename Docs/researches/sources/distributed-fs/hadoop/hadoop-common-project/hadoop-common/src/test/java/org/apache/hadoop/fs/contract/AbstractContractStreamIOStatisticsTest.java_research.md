# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractStreamIOStatisticsTest.java

Purpose: `AbstractContractStreamIOStatisticsTest` validates `IOStatistics` support on filesystem input and output streams, especially byte counters for reads and writes.

Important APIs and types: it uses `IOStatistics`, `IOStatisticsSnapshot`, `IOStatisticsSource`, `FSDataInputStream`, `FSDataOutputStream`, `STREAM_READ_BYTES`, `STREAM_WRITE_BYTES`, and assertion helpers from `IOStatisticAssertions`. Hooks include `streamWritesInBlocks()`, `readBufferSize()`, `outputStreamStatisticKeys()`, and `inputStreamStatisticKeys()`.

Control flow: `teardown()` aggregates filesystem-level statistics into a static snapshot when the filesystem implements `IOStatisticsSource`; `@AfterAll` logs aggregate stats if non-empty. Output tests verify required statistic keys, single-byte write counters before write, after write, and after close, and byte-array write counters including stringified stats. Input tests verify required keys and read byte counters across single-byte reads, buffer reads, `readFully`, positioned reads, seeks, lazy-seek reads, and EOF-adjacent reads for unbuffered streams.

State and persistence behavior: each test creates and deletes method-path files. Stream statistics must remain queryable after stream close. The static snapshot persists across test methods for final aggregate logging only.

Dependencies and integration points: the file integrates stream statistics extraction, logging support, and concrete stream buffering policy via overridable hooks. It assumes streams expose at least read/write byte counters.

Risks: buffered input streams count bytes at buffer granularity, so `readBufferSize()` must be correctly overridden by concrete tests or expected counters will be wrong. For block-writing streams, in-progress write counters may stay zero until close, controlled by `streamWritesInBlocks()`.

Test signals: pass indicates stream statistics expose required keys, counters start at zero, byte counters advance according to explicit or buffered IO policy, counters remain available after close, seeks do not count as reads, and filesystem aggregate statistics can be harvested.
