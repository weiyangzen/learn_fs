# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractStreamIOStatistics.java

## Purpose
`TestLocalFSContractStreamIOStatistics` validates IOStatistics exposed by local FS input and output streams.

## Important APIs, Types, And Functions
It extends `AbstractContractStreamIOStatisticsTest`, creates `LocalFSContract`, and overrides `inputStreamStatisticKeys()`, `outputStreamStatisticKeys()`, `readBufferSize()`, and `streamWritesInBlocks()`. Expected counters include read bytes, read exceptions, seek operations, skip operations/bytes, write bytes, and write exceptions.

## Control Flow
The inherited suite performs stream reads/writes/seeks/skips and checks that listed counters exist and move in the expected direction. This subclass constrains buffer size to 1024 and says writes occur in blocks.

## State And Persistence
No subclass state. IOStatistics are in stream objects and filesystem statistics while files are local temporary data.

## Dependencies And Integration Points
It depends on `StreamStatisticNames` and local FS stream instrumentation.

## Risks
Exact counter values may vary with buffering, so abstract tests must understand local block writes. Missing keys are instrumentation regressions.

## Test Signals
Signals are presence and monotonic movement of the expected IOStatistics counters.
