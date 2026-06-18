# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/Statistic.java

## Purpose
`Statistic` is the enum vocabulary for S3A counters, gauges, durations, and quantiles. It drives metric declaration in `S3AInstrumentation` and storage statistics exported by the filesystem.

## Important APIs, Types, and Functions
Each enum value stores a symbol, description, and `StatisticTypeEnum`. Categories cover low-level HTTP/action durations, HTTP responses, filesystem invocations, object IO, stream read/write/prefetch/cache metrics, committer metrics, store retry/throttle/client creation metrics, delegation token metrics, multipart uploader metrics, audit metrics, and client-side encryption gauge. APIs are `getSymbol()`, `fromSymbol()`, `getDescription()`, `getType()`, and `toString()`.

## Control Flow and State
Static initialization builds `SYMBOL_MAP` from all enum values for reverse lookup. `S3AInstrumentation` iterates all values by type to create metrics and IOStatistics declarations.

## State and Persistence Behavior
Enum values and the symbol map are static immutable runtime state. The enum does not store metric values; it names and classifies them.

## Dependencies and Integration Points
Dependencies include `StatisticTypeEnum`, Hadoop `StoreStatisticNames`, `StreamStatisticNames`, `FileSystemStatisticNames`, and `AuditStatisticNames`. It integrates with instrumentation, stream stats, store stats, audit tests, committers, retry/throttle reporting, and external monitoring expecting stable symbols.

## Risks and Test Signals
Risks include symbol collisions silently overwriting `SYMBOL_MAP`, type misclassification causing missing counters/gauges/durations, changing symbols breaking metrics consumers, and new audit values requiring test support updates. Tests should verify unique symbols, reverse lookup, type-driven metric registration, expected metric publication, and compatibility of important symbol names.
