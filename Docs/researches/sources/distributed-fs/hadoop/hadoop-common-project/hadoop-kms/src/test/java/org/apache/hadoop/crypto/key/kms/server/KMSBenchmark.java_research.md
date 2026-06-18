# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/KMSBenchmark.java

## Purpose
`KMSBenchmark.java` is a command-line benchmark tool for measuring KMS encrypted-key generation and decryption throughput/latency through `KeyProviderCryptoExtension`.

## Important APIs, Types, and Functions
The class implements `Tool`. `OperationStatsBase` owns common benchmark parameters, thread scheduling, timing, and result printing. `StatsDaemon` executes operations in subject-inheriting threads. `EncryptKeyStats` benchmarks `generateEncryptedKey`; `DecryptKeyStats` benchmarks `decryptEncryptedKey`. Static helpers include `createKeyProviderCryptoExtension`, `runBenchmark`, `printUsage`, and `main`.

## Control Flow
Construction creates a key provider extension from `hadoop.security.key.provider.path`, attempts to pre-generate an EEK for key `systest`, and parses selected setup flags. `run` parses `-op encrypt`, `-op decrypt`, or `-op all`, constructs operation stats, runs each benchmark, then prints stats. `benchmark` divides requested operations across threads, starts daemons, waits for completion, aggregates local counts and cumulative times, and reports elapsed wall time and average call time.

## State and Persistence
State includes shared provider, one shared `eek` field, selected key name, setup flags, and benchmark counters. Optional key creation would persist through the configured key provider, but `createEncryptionKey` is never set to true in the observed parser despite parsing `-createkey` into `encryptionKeyName`.

## Dependencies and Integration Points
It uses Hadoop `ToolRunner`, `GenericOptionsParser`, `KMSUtil.createKeyProvider`, `SubjectInheritingThread`, `Time`, and `KeyProviderCryptoExtension`. It is test/benchmark code rather than server runtime.

## Risks
The `-createkey` flag appears to set only the key name, not `createEncryptionKey`, so requested key creation may not happen. Decrypt benchmark shares a mutable `eek` across threads; encrypt benchmark updates that same field concurrently. Exceptions during operations are logged but do not fail the benchmark, so results can include failed attempts as executed operations. `isInProgress` busy-waits with sleep and relies on local counters.

## Test Signals
Tests should verify CLI parsing, operation division across threads, provider-path requirement, `-op all`, warmup behavior, failure handling semantics, and the apparent `-createkey` flag bug.
