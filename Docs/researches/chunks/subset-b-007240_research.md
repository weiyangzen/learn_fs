# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml lines 48967-50813

## Scope

This chunk is the tail of the Apache Hadoop Common 3.5.0 JDiff API XML. It begins inside `org.apache.hadoop.util.StringInterner`, continues through the end of `org.apache.hadoop.util`, covers the public Bloom filter API package, a Curator package summary, and the public functional helper APIs under `org.apache.hadoop.util.functional`, then closes with an empty `org.apache.hadoop.util.hash` package and the closing `</api>`.

Because the source is JDiff XML, this document describes the exported API contract rather than full method bodies. Control-flow and state notes are inferred only from signatures, inheritance, serialization methods, and Javadocs present in this chunk.

## Purpose

The chunk documents utility APIs used across Hadoop Common rather than one cohesive runtime subsystem. The covered APIs fall into five groups:

- General Hadoop utilities: string interning, OS resource introspection, command-line `Tool` execution, binary prefix parsing/formatting, checksum type identity, and build/version metadata.
- Probabilistic set-membership utilities: standard, counting, dynamic, and retouched Bloom filters plus the hash adapter and selective-removal scheme constants.
- Curator integration marker package: package-level documentation for ZooKeeper Curator utilities.
- Functional and asynchronous I/O helpers: checked-exception-friendly future handling, option propagation into filesystem builders, closeable task-pool submission, and `RemoteIterator` adapters.
- Package boundary metadata for `org.apache.hadoop.util.hash`, which is present here only as an empty package entry.

These APIs provide reusable infrastructure for Hadoop command-line tools, filesystem/client code, distributed service diagnostics, probabilistic metadata structures, and asynchronous filesystem operations.

## Important APIs, Types, and Functions

`StringInterner` is partially covered. The visible methods are `weakIntern(String)` and `internStringsInArray(String[])`, with the preceding `strongIntern` documentation tail also visible. The API distinguishes strong interning, which retains a strong reference and prevents collection, from weak interning, which uses `String.intern()` without retaining application-level strong references. `internStringsInArray()` mutates the supplied array in place and returns the same array.

`SysInfo` is an abstract public plugin for system resource information. `newInstance()` returns a default OS-specific implementation or throws `UnsupportedOperationException` when the OS cannot be determined. Abstract getters expose total and available virtual/physical memory, logical processor count, physical core count, CPU frequency, cumulative CPU time, CPU usage percentage, used virtual cores, aggregate network bytes read/written, and aggregate storage bytes read/written. CPU percentage and vcore usage may return `-1` when unavailable.

`Tool` is the standard Hadoop command interface. It extends `org.apache.hadoop.conf.Configurable` and defines `run(String[] args)`, returning a process-style exit code and allowing checked exceptions. The Javadoc establishes the integration contract: generic Hadoop options should be delegated to `ToolRunner`, while the implementation handles application-specific arguments.

`ToolRunner` provides static execution and utility methods. `run(Configuration, Tool, String[])` parses generic arguments, updates the tool configuration, and invokes `Tool.run()`. `run(Tool, String[])` delegates using the tool's current configuration. `printGenericCommandUsage(PrintStream)` emits generic option help. `confirmPrompt(String)` reads an interactive response and returns true for case-insensitive `y` or `yes`.

`StringUtils.TraditionalBinaryPrefix` is represented as a public static enum in the XML. It exposes `values()`, name-based `valueOf(String)`, symbol-based `valueOf(char)`, `string2long(String)`, and `long2String(long, String, int)`. Public final fields `value`, `symbol`, `bitShift`, and `bitMask` define each prefix. The documented prefixes are traditional binary units from kilo through exa, with case-insensitive symbols; parsing examples show suffix multiplication by powers of 1024.

`DataChecksum.Type` is represented as a public static enum with `values()`, name-based `valueOf(String)`, id-based `valueOf(int)`, and public final fields `id` and `size`. This is the API-visible identity layer for checksum algorithms and checksum byte sizes.

`VersionInfo` exposes protected instance getters and public static getters for Hadoop build metadata: version, Git revision, branch, compile date, user, repository URL, source checksum, build version, protoc version, and compile platform. `main(String[])` is public and static, indicating a command-line reporting entry point.

`BloomFilter` extends `Filter` and supports default deserialization construction, parameterized construction with vector size, number of hash functions, and hash type, plus `add(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, `membershipTest(Key)`, `toString()`, `getVectorSize()`, `write(DataOutput)`, and `readFields(DataInput)`. The contract is classic Bloom-filter behavior: compact set membership, no false negatives for normal insertion/query use, and possible false positives.

`CountingBloomFilter` is a final `Filter` implementation with the same constructor shape and logical operations as `BloomFilter`, plus `delete(Key)` and `approximateCount(Key)`. The API documents a small counter width: inserting the same key more than 15 times can overflow all associated positions, increasing error rates. Deletion is documented as a no-op when the key is not considered present, but underflow can later reduce approximate counts below the true count with a false-negative probability.

`DynamicBloomFilter` extends `Filter` and adds a parameterized constructor `(vectorSize, nbHash, hashType, nr)`, where `nr` is the maximum number of keys per row. Its contract is a matrix of standard Bloom filters that adds rows as the recorded set grows and no active row can accept more keys.

`HashFunction` is a final helper that maps a `Key` into multiple integer positions. The constructor takes the maximum returned value, number of hash values, and hash algorithm type. `hash(Key)` returns the integer positions. `clear()` is explicitly a no-op.

`RemoveScheme` is a public interface used by retouched Bloom filters. It exports short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`, representing strategies for selecting a bit to clear when removing false positives.

`RetouchedBloomFilter` is a final subclass of `BloomFilter` and implements `RemoveScheme`. It adds false-positive tracking through overloaded `addFalsePositive()` methods for a single `Key`, `Collection<Key>`, `List<Key>`, and `Key[]`. `selectiveClearing(Key, short)` applies a removal scheme to clear bits for a known false positive. It retains writable serialization through `write(DataOutput)` and `readFields(DataInput)`.

`CloseableTaskPoolSubmitter` implements `TaskPool.Submitter` and `Closeable`. It wraps an `ExecutorService`, exposes `getPool()`, submits `Runnable` tasks as `Future<?>`, and shuts the pool down in `close()`. Its purpose is explicit thread-pool lifecycle management.

`FutureIO` is a final utility class for futures and checked exceptions. It includes `awaitFuture(Future<T>)`, timed `awaitFuture(Future<T>, long, TimeUnit)`, untimed and duration-bounded `awaitAllFutures(Collection<Future<T>>...)`, `cancelAllFuturesAndAwaitCompletion(Collection<Future<T>>, boolean, Duration)`, overloads of `raiseInnerCause()` for `ExecutionException` and `CompletionException`, `unwrapInnerException(Throwable)`, `propagateOptions()` overloads for `FSBuilder`, and `eval(CallableRaisingIOE<T>)`. The key contract is that future failures are unwrapped so `IOException`, `RuntimeException`, `Error`, cancellation, timeout, and interruption are surfaced in caller-friendly forms.

`RemoteIterators` is a final utility class for adapting and composing Hadoop `RemoteIterator` instances. It creates iterators from singletons, `Iterator`, `Iterable`, arrays, long ranges, mapping functions, filters, casts, closeable wrappers, and halt predicates. It also converts remote iterators to `List` or array, applies a checked-exception consumer with `foreach()`, and performs cleanup with optional statistics logging and close propagation.

## Control Flow

`ToolRunner` defines the command startup flow expected by Hadoop CLI applications. A caller provides a `Configuration`, a `Tool`, and raw arguments. `ToolRunner` parses generic Hadoop command-line options, mutates or creates the configuration, sets it on the tool, and then delegates the remaining application arguments to `Tool.run()`. The return value is the tool's process-style exit code.

`SysInfo` flow is implementation-selected. Callers ask `SysInfo.newInstance()` for the OS default, then repeatedly call abstract metric getters. The API separates instantaneous or sampled values, such as CPU usage percentage, from cumulative counters, such as cumulative CPU time and aggregate I/O byte counters. Unavailable sampled metrics are represented by sentinel `-1` values rather than exceptions.

`TraditionalBinaryPrefix` parsing first trims input and then interprets an optional binary-prefix suffix. Formatting reverses that by selecting an appropriate binary prefix and applying the requested unit and decimal precision. The enum fields expose the exact multiplier and bit-mask metadata used by the conversion layer.

The Bloom filter family has a common lifecycle: construct an empty filter, add keys through `add(Key)`, query with `membershipTest(Key)`, combine compatible filters with boolean operations, and optionally serialize through `write()`/`readFields()`. Counting filters add deletion and approximate count retrieval; dynamic filters add row-growth when the active row reaches `nr`; retouched filters add a second phase where observed false positives are recorded and selected bits are cleared according to a removal scheme.

`FutureIO.awaitFuture()` and `awaitAllFutures()` block on one or more futures, unwrap `ExecutionException` or `CompletionException`, and rethrow meaningful causes. Interruption while waiting becomes `InterruptedIOException`; future cancellation remains `CancellationException`; timed waiting may raise `TimeoutException`. `cancelAllFuturesAndAwaitCompletion()` first cancels every future with a caller-selected interrupt flag, then waits up to a duration and returns futures that still completed successfully while ignoring thrown exceptions and timeout.

`FutureIO.propagateOptions()` scans a `Configuration` for keys under optional and mandatory prefixes and applies the stripped options to an `FSBuilder`. The documented stripping rules convert keys such as `fs.example.s3a.option` to `s3a.option`, `fs.example.fs.io.policy` to `fs.io.policy`, and `fs.example.something` to `something`. The overload with separate optional and mandatory prefixes applies both modes to the same builder.

`RemoteIterators` composes lazy iteration. Source adapters provide a `RemoteIterator<T>` interface over local objects, Java iterators, arrays, or numeric ranges. Mapping and type-casting wrappers transform each yielded value. Filtering may advance the source in `hasNext()` to find the next accepted value, or perform that work on demand in `next()` if `hasNext()` is skipped. Closing wrappers propagate close to any closeable source iterator and also close an extra supplied resource. Haltable wrappers consult a checked-exception boolean predicate so long-running iteration can stop quickly.

## State and Persistence Behavior

The XML itself is generated API metadata and has no runtime persistence behavior. The APIs it describes expose several stateful runtime contracts.

`StringInterner` state is process-local interning state. Strong interning deliberately retains references and can grow memory retention; weak interning avoids retaining the original object strongly. `internStringsInArray()` mutates caller-owned array state in place.

`SysInfo` has no persistent state in the public contract, but implementations are expected to observe OS state and counters. Some values are static hardware/container properties, while CPU usage and I/O counters depend on sampling and operating-system support.

`VersionInfo` reads build-time metadata embedded in the Hadoop artifact. The protected instance getters indicate an instance-backed metadata source, while the public static getters expose process-wide component build information to callers and command-line tools.

Bloom filters are explicitly stateful and serializable through Hadoop's `DataOutput`/`DataInput` pattern. `BloomFilter` persists the bit vector and filter parameters. `CountingBloomFilter` persists counter state and can be affected by overflow or underflow. `DynamicBloomFilter` persists multiple row filters and insertion thresholds. `RetouchedBloomFilter` persists both the base Bloom filter state and the additional false-positive information used for selective clearing.

`CloseableTaskPoolSubmitter` owns an `ExecutorService` lifecycle. Its durable state is not persisted, but the object controls whether the executor can accept more work and whether threads are shut down through `close()`.

`FutureIO` is stateless, but it controls observable state transitions in futures by waiting, cancelling, or propagating exceptions. It also mutates `FSBuilder` state when propagating configuration options.

`RemoteIterators` wrappers are stateful during traversal. Filtering wrappers may cache the next accepted element between `hasNext()` and `next()`. Range iterators track the current long. Closing wrappers track resources that should be closed after use. Wrappers may preserve and expose underlying `IOStatisticsSource` statistics so statistics survive transformation chains.

## Dependencies and Integration Points

The utility APIs integrate with `org.apache.hadoop.conf.Configuration`, `Configurable`, `GenericOptionsParser`, `FSBuilder`, `RemoteIterator`, `IOStatisticsSource`, and Hadoop's checked-exception functional interfaces such as `CallableRaisingIOE`, `FunctionRaisingIOE`, and `ConsumerRaisingIOE`.

Command-line integration is through `Tool` and `ToolRunner`, which are the bridge between Hadoop generic options and application-specific drivers. The Javadoc example references MapReduce-era classes such as `JobConf`, `JobClient`, and `RunningJob`, showing that the contract is intended for both Common and MapReduce tools.

System and build diagnostics integrate through `SysInfo` and `VersionInfo`. Resource managers, daemons, tests, and command-line diagnostics can depend on the stable public getters for memory, CPU, I/O, and build metadata.

Bloom filters depend on `org.apache.hadoop.util.bloom.Key`, `Filter`, `org.apache.hadoop.util.hash.Hash`, Java collections, and Hadoop writable-style serialization via `DataInput`/`DataOutput`. They are reusable across any subsystem needing approximate membership or compact cache summaries.

`FutureIO` integrates asynchronous Java concurrency (`Future`, `CompletableFuture`, `ExecutionException`, `CompletionException`, `CancellationException`, `TimeoutException`, `Duration`, `TimeUnit`) with Hadoop's `IOException`-oriented filesystem APIs. It also promotes APIs from `org.apache.hadoop.fs.impl.FutureIOSupport` into the public utility namespace for application code.

`RemoteIterators` integrates local Java iteration sources with Hadoop remote listing APIs. The package documentation explicitly notes that Hadoop filesystem APIs raise `IOException`, which is why the functional package provides checked-exception-capable alternatives to `java.util.function`.

The Curator package appears here only with package-level documentation stating that it provides utilities for Curator ZooKeeper interaction. The empty hash package marker indicates that the public API for `org.apache.hadoop.util.hash` is either absent from this chunk or contains no documented public types here.

## Risks and Edge Cases

`StringInterner` strong interning can retain data indefinitely, so it is risky for high-cardinality or untrusted strings. `internStringsInArray()` mutates its argument, which can surprise callers that expect a copy.

`SysInfo` values are platform-dependent. `newInstance()` can fail for unsupported OS detection, and CPU usage or vcore usage may be unavailable. Tests and callers must accept sentinel values and should not assume every metric exists on every platform or container environment.

`ToolRunner.confirmPrompt()` performs interactive I/O and only treats `y` or `yes` as affirmative. Automation using Hadoop tools needs to avoid unexpected prompts or provide input explicitly.

`TraditionalBinaryPrefix.string2long()` can overflow if a large numeric prefix is multiplied by a binary unit. Case-insensitive symbols are convenient but can mask invalid user input if validation is weak around suffix handling.

Checksum type lookup by integer id must remain compatible with serialized data and wire protocols. Unknown ids or size mismatches are compatibility-sensitive because checksum metadata is used in storage and data-transfer paths.

Bloom filters have inherent false-positive risk. Counting Bloom filters add overflow risk after repeated insertion of the same key and possible underflow effects after deletion, including approximate counts lower than the true count. Retouched Bloom filters intentionally trade selected false-positive removal for possible false negatives, so they are not appropriate where classic Bloom-filter "no false negatives" behavior is required after retouching.

Boolean operations on Bloom filters are only meaningful for compatible filters. The API signatures accept `Filter`, so implementations must defend against mismatched vector sizes, hash counts, hash types, or incompatible subclasses.

`FutureIO` can hide subtle concurrency behavior if callers do not distinguish thread interruption, future cancellation, task failure, and timeout. Its documented behavior preserves `CancellationException`, converts waiting interruption to `InterruptedIOException`, and unwraps runtime errors, so callers need tests for each case. `cancelAllFuturesAndAwaitCompletion()` deliberately ignores exceptions and timeout, which is useful for cleanup but risky if used where failures must be reported.

`FutureIO.propagateOptions()` relies on prefix naming and dot-segment stripping. Misconfigured prefixes can silently push wrong optional or mandatory settings into an `FSBuilder`, and mandatory propagation can change builder validation behavior.

`RemoteIterators` are lazy and may own remote resources. `foreach()` explicitly does not close the iterator afterwards, so callers need `cleanupRemoteIterator()` or closeable wrappers when iterators hold file handles, network connections, or listing statistics. Filtering in `hasNext()` can perform remote I/O earlier than callers expect, and skipping `hasNext()` shifts that work into `next()`.

## Test Signals

Useful tests for `StringInterner` should verify strong versus weak/reference-retention expectations where observable, in-place array mutation, null handling if supported by the implementation, and idempotence for equal strings.

`SysInfo` tests should cover OS-specific `newInstance()` selection, unsupported OS handling, non-negative hardware counters, `-1` sentinel behavior for unavailable sampled metrics, and monotonicity for cumulative CPU and I/O counters where the platform supports them.

`Tool` and `ToolRunner` tests should exercise generic option parsing, propagation into the tool's `Configuration`, preservation of application-specific arguments, null configuration handling, returned exit codes, printed generic usage, and prompt parsing for `y`, `yes`, mixed case, and negative responses.

`TraditionalBinaryPrefix` tests should cover suffix parsing for positive and negative values, case-insensitive symbols, no-suffix values, whitespace trimming, formatting precision, unit suffixes, maximum representable prefixes, overflow rejection, and invalid suffix diagnostics.

`DataChecksum.Type` tests should verify stable id lookup, name lookup, checksum size fields, and unknown id behavior.

Bloom filter tests should cover insertion, membership, expected false-positive behavior under controlled parameters, no false negatives for standard filters before retouching, logical `and`/`or`/`xor`/`not`, serialization round trips, vector-size reporting, and rejection or handling of incompatible filter operations.

Counting Bloom filter tests should add and delete keys, verify absent-key deletion is a no-op, assert approximate counts for low values, and explicitly exercise counter overflow beyond 15 repeated inserts and underflow-adjacent deletion cases.

Dynamic Bloom filter tests should insert enough keys to cross the per-row `nr` threshold, verify new rows are added without losing membership for earlier rows, and round-trip the multi-row state through `write()`/`readFields()`.

Retouched Bloom filter tests should record false positives through every overload, apply each `RemoveScheme` constant, verify selected false positives can be removed, and measure or assert the accepted false-negative tradeoff after selective clearing.

`CloseableTaskPoolSubmitter` tests should verify `submit()` delegates to the wrapped executor, `getPool()` returns the original executor, and `close()` shuts it down without requiring callers to touch the executor directly.

`FutureIO` tests should cover successful future results, `IOException` wrapped in `ExecutionException` or `CompletionException`, `UncheckedIOException`, runtime exceptions, errors, cancellation, interruption, timeout, multiple futures, cancellation cleanup, and `eval()` conversion of checked I/O failures into future-compatible failures.

`FutureIO.propagateOptions()` tests should populate `Configuration` keys under optional and mandatory prefixes and assert the exact stripped builder option names, including the documented `s3a.option`, `fs.io.policy`, and `something` cases.

`RemoteIterators` tests should cover every source adapter, mapping, type casting, filtering with and without explicit `hasNext()`, close propagation, halt predicates returning false, range `[start, excludedFinish)` boundaries, `toList()`, `toArray()` with too-small and sufficiently-sized destination arrays, `foreach()` count returns, exception propagation from source and consumer, statistics passthrough, and cleanup of closeable sources.

## Cross-Chunk Notes

The chunk starts after the beginning of `StringInterner`, so the full `strongIntern(String)` method declaration and any earlier `org.apache.hadoop.util` classes are in the preceding chunk. The final per-file reconciliation should merge this with earlier chunks for complete package coverage.

The Bloom API references `Filter`, `Key`, and hash classes whose declarations are outside this chunk. The final report should combine this chunk with the chunks that contain those declarations to describe the complete serialization format and compatibility constraints.

`FutureIO` references `CallableRaisingIOE`, `FunctionRaisingIOE`, `ConsumerRaisingIOE`, `TaskPool`, and `FSBuilder` declarations that are not fully defined here. The reconciliation lane should connect this public helper surface to those functional interfaces and builder implementations.
