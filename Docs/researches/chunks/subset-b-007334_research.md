# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 31379-37729

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.20.2. It records API metadata, not Java method bodies: packages, classes, interfaces, inheritance, implemented interfaces, constructors, methods, parameter and exception types, fields, visibility/static/final/synchronized flags, deprecation text, and embedded Javadoc.

The range begins inside `org.apache.hadoop.util.StringUtils.TraditionalBinaryPrefix`, covers utility classes, Bloom filter and hash APIs, and then a large early section of the legacy `org.apache.hadoop.mapred` API through part of `JobHistory.ReduceAttempt`. Runtime behavior below is inferred from signatures and Javadocs. The merge lane should reconcile the partial start and partial end with adjacent chunks.

## Purpose and Major API Surface

The visible tail of `StringUtils.TraditionalBinaryPrefix` exposes binary-size parsing: `valueOf(char)`, `string2long(String)`, enum values `KILO` through `EXA`, and public final fields `value` and `symbol`. Its purpose is converting strings such as `891g` into long byte counts using case-insensitive 1024-based suffixes.

`Tool` and `ToolRunner` define Hadoop's generic command-line execution contract. `Tool` extends `Configurable` and exposes `run(String[])`. `ToolRunner.run(Configuration, Tool, String[])` and `run(Tool, String[])` parse generic Hadoop options through `GenericOptionsParser`, install the processed `Configuration` on the tool, and return the tool exit code. `printGenericCommandUsage(PrintStream)` emits generic option help.

`UTF8ByteArrayUtils` is a byte-scanning helper for UTF-8 encoded byte arrays. It provides `findByte`, `findBytes`, and two `findNthByte` overloads. These are byte-position utilities, so callers get offsets into the original byte array rather than decoded character indexes.

`VersionInfo` exposes build metadata: Hadoop version, source revision, build date, build user, source URL, combined build version, and a `main` method. `XMLUtils.transform(InputStream, InputStream, Writer)` is a small XSLT wrapper that can throw `TransformerConfigurationException` and `TransformerException`.

The `org.apache.hadoop.util.bloom` package defines Hadoop's probabilistic membership filters. `Filter` is the abstract `Writable` base with protected state `vectorSize`, `HashFunction hash`, `nbHash`, and `hashType`; abstract membership/boolean operations `add(Key)`, `membershipTest(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, and `not()`; bulk `add` overloads for `List`, `Collection`, and `Key[]`; plus `write` and `readFields`.

Concrete Bloom types include `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter`. `BloomFilter` is the standard false-positive/no-false-negative bit-vector form and adds set operations, `membershipTest`, `getVectorSize`, `toString`, and `Writable` serialization. `CountingBloomFilter` is final and adds `delete(Key)` and `approximateCount(Key)`, with the documented 4-bit bucket limit where inserting the same key more than 15 times overflows and increases error. `DynamicBloomFilter` adds the `nr` threshold constructor parameter and grows by adding filter rows when active rows are saturated. `RetouchedBloomFilter` is final, implements `RemoveScheme`, records false-positive keys through `addFalsePositive` overloads, and performs `selectiveClearing(Key, short)` to trade selected false positives for possible false negatives.

`Key` is a `WritableComparable` wrapper around a byte-array value and a double weight. It supports default/readFields construction, explicit value and value-plus-weight construction, `set`, byte and weight accessors, weight increments, equality/hash code, serialization, and `compareTo(Key)`. `HashFunction` maps a `Key` to multiple vector positions. `RemoveScheme` defines public short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` for retouched Bloom clearing strategies.

The `org.apache.hadoop.util.hash` package provides non-cryptographic hashes. `Hash` is the abstract common API with constants `INVALID_HASH`, `JENKINS_HASH`, and `MURMUR_HASH`; parsing from names or `Configuration`; singleton lookup by type or configuration; convenience `hash(byte[])` and `hash(byte[], int)` overloads; and abstract `hash(byte[], int, int)`. `JenkinsHash` and `MurmurHash` implement the concrete algorithms and singleton accessors; `JenkinsHash.main(String[])` computes a file hash for diagnostics.

The `org.apache.hadoop.mapred` package section starts with cluster and counter data. `ClusterStatus` is `Writable` status for task tracker counts/names, blacklist counts, tasktracker expiry interval, running and maximum map/reduce slots, `JobTracker.State`, and JobTracker heap memory usage. `Counters` is the deprecated old-API counter container implementing `Writable` and `Iterable`; it manages groups and counters by enum or string names, increments individual or all counters, computes `sum`, serializes binary counter groups, logs counters, renders compact and escaped compact strings, parses escaped compact strings, and implements synchronized equality/hash code. Nested `Counters.Counter` extends `org.apache.hadoop.mapreduce.Counter`; nested `Counters.Group` is a `Writable`/`Iterable` group with raw and display names, counter lookup/creation, compact stringification, serialization, and synchronized iteration.

The file input/output API surface includes `DefaultJobHistoryParser`, file-related `IOException` subclasses, `FileInputFormat`, `FileOutputCommitter`, `FileOutputFormat`, `FileSplit`, `InputFormat`, and `InputSplit`. `FileInputFormat` is the old-API base for file-backed input formats, with input-path/filter configuration, `listStatus`, split planning, split sizing, block index lookup, host locality calculation, and abstract `getRecordReader`. `FileOutputCommitter` implements job/task setup, task commit/abort, job cleanup, and `needsTaskCommit` for files under `mapred.output.dir`. `FileOutputFormat` configures output compression/codecs, validates output specs, stores output paths, computes task work paths, and generates task-specific names. `FileSplit` bridges old and new input split APIs and serializes a path/start/length/host-location tuple. `InputFormat` and `InputSplit` define the old MapReduce split planning and record-reader contracts.

`InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` signal validation failures. `InvalidInputException` is notable because it wraps an uncopied list of problems, exposes it through `getProblems`, and concatenates problem messages in `getMessage`. `IsolationRunner.main` runs a single task from a task directory for debugging or isolation.

`JobClient` is the old-API client facade for connecting to JobTracker, staging and submitting jobs, retrieving `RunningJob` handles, task reports, cluster status, all or incomplete jobs, queues, and system directories, then monitoring or running jobs. It implements `MRConstants` and `Tool`, has constructors for default and explicit tracker connections, synchronized `close` and `getFs`, submission overloads for a job file and `JobConf`, `submitJobInternal`, `isJobDirValid`, task display filtering, `runJob`, `monitorAndPrintJob`, `run(String[])`, and `main`. Nested `TaskStatusFilter` enum values are `NONE`, `KILLED`, `FAILED`, `SUCCEEDED`, and `ALL`.

`JobConf` is the central old-API job configuration type, extending `Configuration` but deprecated in favor of `Configuration`. It exposes constructors from classes, existing configurations, XML files, paths, and default-resource loading flags. The chunk covers setters/getters for jar selection, local dirs and cleanup, user, failed-task file retention, working directory, task JVM reuse, input/output format classes, output committer, output and map-output compression, map and final key/value classes, comparators and grouping comparator, old/new mapper/reducer toggles, mapper/map runner/partitioner/reducer/combiner classes, speculative execution, map/reduce task counts, max attempts, job name, session id, per-tracker failure thresholds, allowed task failure percentages, priority, profiling, debug scripts, job-end notification URI, job local dir, memory limits, queue name, and memory-related public constants.

`JobConfigurable` supplies `configure(JobConf)`. `JobContext` bridges to `org.apache.hadoop.mapreduce.JobContext` while exposing old `JobConf` and a `Progressable`. `JobEndNotifier` manages async or local job-completion notifications through `startNotifier`, `stopNotifier`, `registerNotification`, and `localRunnerNotification`.

`JobHistory` and nested types define append-mode job history logging and parsing. `JobHistory.init` initializes history with JobTracker host/start time, `parseHistoryFromFS` streams records to a `Listener`, `isDisableHistory` and `setDisableHistory` control logging, and `getTaskLogsUrl` builds task log URLs when tracker, port, and attempt id are available. `HistoryCleaner` deletes old history files and stale master-index entries. `JobInfo` manages task maps, local job-file path lookup, URL encoding/decoding of history file paths/names, user and history path lookup, recovery selection between duplicate recovery files, and static logging of submitted, initialized, started, finished, failed, killed, priority, and submit/launch info records. `Keys` enumerates the history key namespace, `Listener.handle(RecordTypes, Map)` is the parse callback, `MapAttempt` logs map attempt start/finish/failure/kill events, `RecordTypes` enumerates line record tags, and the chunk ends inside `ReduceAttempt` logging methods.

## Control Flow and Behavioral Contracts

Generic command-line control flow is `ToolRunner` first parsing Hadoop generic options into a `Configuration`, then installing that configuration into the target `Tool`, then invoking `Tool.run`. Application-specific arguments are passed along after generic parsing.

Bloom filter control flow is hash-driven: a `Key` is converted by `HashFunction` into `nbHash` vector positions bounded by `vectorSize`; `add` mutates the filter state at those positions; `membershipTest` checks those positions; boolean operations mutate the receiver in place. Counting filters add count increments/decrements and approximate count queries. Dynamic filters insert into an active row until its threshold is reached, then create a new row. Retouched filters record known false positives and selectively clear bits based on a `RemoveScheme`.

Hash selection flows through configuration or symbolic constants. Callers parse `"jenkins"` or `"murmur"` to a type, get a singleton `Hash`, and then hash byte prefixes with a seed. The Javadocs explicitly position Jenkins and Murmur as non-cryptographic lookup hashes.

File input flow is old MapReduce's standard path: set input paths and optional `PathFilter` on `JobConf`; `FileInputFormat.listStatus` validates and expands inputs; `getSplits` uses desired split count, minimum split size, block size, file splittability, and block locations; `getSplitHosts` ranks hosts/racks by byte contribution; the framework assigns each `InputSplit` to a mapper and creates a `RecordReader` for records. `InputFormat` documents logical splits, not physical file splitting, so `RecordReader` implementations must respect record boundaries.

File output flow starts by setting output path and compression in `JobConf`; `FileOutputFormat.checkOutputSpecs` validates output before submission; tasks write to task-specific work output paths; `FileOutputCommitter` promotes successful attempt output and aborts failed attempt output. `TEMP_DIR_NAME` and task unique names are part of the compatibility surface for speculative execution and cleanup behavior.

Job submission control flow in `JobClient` is: connect to the configured JobTracker, get a filesystem handle, validate input/output specs, compute input splits, account for `DistributedCache`, copy the job jar and XML config to the distributed system directory, submit to JobTracker, and optionally monitor. `runJob` blocks until completion; `submitJob` returns a `RunningJob` for polling; job-end notification URI offers callback-style completion.

`JobConf` is the dataflow source for most runtime choices. Its class-valued settings drive reflection for input/output formats, mappers, reducers, combiners, partitioners, comparators, compression codecs, and committers. Its scalar settings drive task counts, speculative execution, retries, failure tolerances, profiling, debug scripts, memory limits, queue placement, and notification behavior.

Job history control flow is append-and-parse. Runtime code logs job, task, map-attempt, and reduce-attempt events as line records of a typed tag plus key/value pairs. Finished, failed, and killed job events close the per-job history log. Later parsers either populate a `JobInfo` object model or stream parsed records into `Listener.handle`.

## State, Persistence, and Side Effects

This XML snapshot itself is persistent compatibility data used by JDiff; it has no runtime state. The APIs it describes are stateful and persistence-sensitive.

`Filter`, `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, `RetouchedBloomFilter`, and `Key` implement `Writable` serialization. Their persisted fields include vector size, hash configuration, vector/count matrix contents, false-positive metadata, key bytes, and key weight. Changing serialization order or hash behavior would invalidate filters written by Hadoop 0.20.2 code.

`Counters`, `Counters.Group`, `ClusterStatus`, and `FileSplit` also expose `Writable` contracts. `Counters` has both binary and textual escaped compact encodings used by MapReduce status, logs, and history. Several counter methods are synchronized, so the old implementation promised some thread-safety for mutation, iteration, and serialization.

`JobConf` persists job state as configuration keys and resources. Local-dir cleanup and `getLocalPath` have filesystem side effects. Debug scripts rely on `DistributedCache` localization and task log files. Memory limit constants and queue names affect scheduler and task-tracker behavior outside this class.

`FileInputFormat` and `FileOutputFormat` store paths, filters, compression flags/codecs, and output/work paths in `JobConf`. `FileOutputCommitter` mutates output directories, temporary directories, and task attempt output. Incorrect promotion or cleanup can corrupt distributed output.

`JobClient` owns a cluster connection and filesystem handle, stages job artifacts, submits jobs over RPC, and prints or monitors status. `ClusterStatus` mirrors distributed cluster state, including task tracker membership and blacklist state.

`JobHistory` persists append-only plain-text history files and a master index. `HistoryCleaner` deletes old history files and index entries. `JobInfo.recoverJobHistoryFile` resolves duplicate recovery files by choosing the oldest and ensuring only one remains. `JobEndNotifier` performs external notification side effects.

## Dependencies and Integration Points

The utility portion depends on `Configuration`, `Configurable`, `GenericOptionsParser`, Java streams/writers, XSLT transformer classes, and Hadoop's `Writable`/`WritableComparable`.

Bloom filters integrate with `org.apache.hadoop.util.hash.Hash`, `JenkinsHash`, and `MurmurHash`. They depend on deterministic non-cryptographic hashing for stable vector positions and on `DataInput`/`DataOutput` for persistence.

The old `mapred` APIs bridge heavily to the newer `org.apache.hadoop.mapreduce` package: `Counters.Counter`, `FileSplit`, `ID`, and `JobContext` extend or wrap new API classes while preserving old method signatures. Many types are deprecated but still define Hadoop 0.20.2 compatibility.

Filesystem integration uses `FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `PathFilter`, local files, distributed output directories, and history locations. Split locality integrates with `org.apache.hadoop.net.NetworkTopology`.

Job submission and cluster integration references `JobTracker`, `RunningJob`, `JobStatus`, `TaskReport`, `TaskAttemptID`, `TaskAttemptContext`, `OutputCommitter`, `OutputFormat`, `InputFormat`, `RecordReader`, `Reporter`, `DistributedCache`, `CompressionCodec`, `RawComparator`, `Partitioner`, `Mapper`, and `Reducer`.

History integration depends on `JobID`, `JobPriority`, `Counters`, task attempt ids, tracker names, HTTP ports, task logs, and record schemas represented by `JobHistory.Keys` and `RecordTypes`.

## Risks and Compatibility Notes

The range begins mid-class and ends mid-class. `TraditionalBinaryPrefix` and `JobHistory.ReduceAttempt` are incomplete here, so final per-file research should merge adjacent chunks before drawing complete conclusions about those classes.

Because this is a JDiff XML file, a behavioral change can be as small as a changed attribute: visibility, static/final flags, synchronized flags, exception lists, deprecation strings, enum constants, field names, or parameter types all affect generated API compatibility reports.

Bloom filters are sensitive to deterministic hashing, vector sizing, count overflow, and `Writable` wire format. The counting filter's documented 15-insertion overflow boundary is a correctness risk for callers treating it as an approximate count map. Retouched Bloom filters intentionally introduce false negatives; misuse of `RemoveScheme` can break standard Bloom assumptions.

Hash APIs are non-cryptographic by design. Using Jenkins or Murmur for security-sensitive identity, signatures, or adversarial collision defense would be wrong. Changing singleton behavior or configured hash names would alter Bloom filter compatibility.

File splitting risks include hidden or filtered inputs, zero-input validation, compressed non-splittable files, off-by-one block boundaries, min split size, block size, rack/host locality ranking, and record-reader responsibility for record boundaries.

Output commit risks are high around speculative execution, task attempt naming, temporary directory cleanup, and side-effect files. Any change to `FileOutputCommitter` or `FileOutputFormat` path conventions can cause duplicate output, lost output, or failed recovery.

`JobConf` has broad cross-component coupling. Changing a getter/setter's configuration key, default value, class-loading behavior, or deprecation-preserved old/new API toggle can affect job submission, task launch, scheduling, retries, debug scripts, profiling, memory enforcement, and queue routing.

`JobClient` and history APIs are distributed-system surfaces. Failures can come from filesystem staging, invalid configuration, JobTracker readiness, RPC/IO errors, queue lookup, incomplete recovery, malformed history records, or listener exceptions. History schema keys and record type names are especially compatibility-sensitive because external tools parse them.

## Test Signals

JDiff validation should confirm the full XML remains well formed and this range preserves all class/interface names, inheritance, implemented interfaces, method overloads, parameters, checked exceptions, fields, enum constants, deprecation text, and flags.

Utility tests should cover binary-prefix parsing including case-insensitive suffixes, negatives, trim behavior, overflow/invalid suffix handling, UTF-8 byte search offsets, nth-byte misses, `ToolRunner` generic-option parsing/config injection, `VersionInfo` getters, and `XMLUtils.transform` success and transformer failures.

Bloom/hash tests should cover `Writable` round trips for every filter and `Key`, bulk adds, membership positives and expected false-positive behavior, boolean operations mutating the receiver, counting add/delete/underflow/overflow and `approximateCount`, dynamic row growth at the `nr` threshold, retouched false-positive registration and every `RemoveScheme`, hash type parsing from names/configuration, singleton lookup, and deterministic Jenkins/Murmur hash outputs.

MapReduce serialization tests should cover `ClusterStatus`, `Counters`, `Counters.Group`, `Counters.Counter`, and `FileSplit` read/write compatibility, counter escaped compact round trips, malformed compact string parse errors, synchronized counter mutation, group display names, missing counters returning zero, and equality/hash code.

File input tests should cover path setters/adders/getters, comma-separated parsing, input filters, empty inputs, invalid file types, splitability overrides, compressed inputs, split sizing, block index selection, host/rack locality ranking, `InputSplit.getLength/getLocations`, and `RecordReader` boundary responsibilities.

File output tests should cover compression flags and codec classes, existing-output rejection, invalid output specs, task work path calculation, unique name generation, custom task output paths, `FileOutputCommitter` setup/commit/abort/cleanup, failed attempt cleanup, and speculative attempt collision cases.

JobClient and JobConf tests should verify default and explicit JobTracker connections, filesystem handle lifecycle, job directory validation, submit from file and `JobConf`, `submitJobInternal` exception paths, `RunningJob` lookup by `JobID` and deprecated string id, task report queries, task display filters, cluster status detail flags, queue queries, `runJob`, `monitorAndPrintJob`, CLI exit codes, and every major `JobConf` getter/setter pair.

Job history tests should write and parse representative submitted, initialized, running, finished, failed, killed, priority, map-attempt, and reduce-attempt records; validate `Keys` and `RecordTypes`; exercise listener streaming without retaining the full model; test task log URL construction with missing fields; encode/decode history filenames; recover duplicate history files; disable/enable history; and run cleaner behavior against old and current history entries.
