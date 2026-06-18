# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.1.xml lines 31470-37821

## Scope

This chunk is a JDiff/API XML slice for Hadoop 0.20.1. It starts at the tail of `org.apache.hadoop.util.ToolRunner`, covers utility helpers, the complete public Bloom filter and hash API packages in this range, then enters the old `org.apache.hadoop.mapred` API. The `mapred` portion covers cluster status, counters, file input/output contracts, job submission/client configuration, and most of the job history logging model. The chunk ends inside the opening `JobID` constructor documentation, so adjacent chunks are needed for the rest of `JobID` and any following MapReduce identifiers.

The source is generated API metadata, not Java implementation. The research target is therefore the compatibility contract: packages, public/protected classes and interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, static/final/synchronized/abstract flags, deprecation markers, and embedded Javadocs.

## Purpose

The `org.apache.hadoop.util` tail documents generic command-line support and small runtime helpers. `ToolRunner.printGenericCommandUsage(PrintStream)` publishes the generic Hadoop CLI options understood by `GenericOptionsParser`, `UTF8ByteArrayUtils` provides byte-level searching over UTF-8 encoded byte arrays, `VersionInfo` exposes build/version metadata, and `XMLUtils.transform` wraps XSLT transformation for Hadoop utility code.

The `org.apache.hadoop.util.bloom` package defines Hadoop's serializable probabilistic set-membership filters. It includes the abstract `Filter` contract, concrete `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, and `RetouchedBloomFilter` variants, plus `Key`, `HashFunction`, and `RemoveScheme`. These APIs are designed for compact network/storage summaries and all filter/key state is exposed through Hadoop `Writable` read/write methods.

The `org.apache.hadoop.util.hash` package documents non-cryptographic hashing support used by Bloom filters and other hash-table style components. `Hash` selects Jenkins or Murmur implementations by configuration or symbolic constant, while `JenkinsHash` and `MurmurHash` expose concrete seeded 32-bit hash functions.

The `org.apache.hadoop.mapred` portion is the old MapReduce API surface. It covers job and cluster introspection (`ClusterStatus`, `JobClient`), counter accounting (`Counters`, `Counter`, `Group`), file-based input and output (`FileInputFormat`, `FileOutputFormat`, `FileOutputCommitter`, `FileSplit`, `InputFormat`, `InputSplit`), job configuration (`JobConf`, `JobConfigurable`, `JobContext`), asynchronous job notifications, and append-only job history logging/parsing (`JobHistory` and nested types). Many old `mapred` types in this chunk are deprecated in favor of `org.apache.hadoop.mapreduce`, but remain part of the 0.20.1 public compatibility surface.

## Important APIs, Types, and Functions

### Utility and Version Helpers

- `ToolRunner.printGenericCommandUsage(PrintStream)` emits generic Hadoop command-line option help. The enclosing `ToolRunner` docs tie this to running `Tool` implementations through `GenericOptionsParser`.
- `UTF8ByteArrayUtils` has static `findByte(byte[], int, int, byte)`, `findBytes(byte[], int, int, byte[])`, and `findNthByte` overloads. These operate on encoded bytes and return byte offsets or `-1`; they do not decode to Java characters.
- `VersionInfo` exposes static `getVersion`, `getRevision`, `getDate`, `getUser`, `getUrl`, `getBuildVersion`, and `main`. It is the public API for reading Hadoop package/build annotation data.
- `XMLUtils.transform(InputStream styleSheet, InputStream xml, Writer out)` applies a stylesheet to XML and declares `TransformerConfigurationException` and `TransformerException`.

### Bloom Filter Package

- `Filter` is the abstract base and implements `Writable`. It owns protected mutable state `vectorSize`, `HashFunction hash`, `nbHash`, and `hashType`. Subclasses must implement single-key `add`, `membershipTest`, logical `and`, `or`, `xor`, and `not`; the base supplies bulk `add` overloads for `List`, `Collection`, and `Key[]`, plus base `write`/`readFields`.
- `BloomFilter` extends `Filter` with default and `(vectorSize, nbHash, hashType)` constructors, single-key add, membership test, logical operations, string rendering, `getVectorSize`, and Writable serialization.
- `CountingBloomFilter` is final and extends `Filter`. It supports `add`, `delete`, `membershipTest`, `approximateCount`, logical operations, string rendering, and serialization. Its docs warn that bucket size limits repeated insert counts; adding the same key more than 15 times can overflow associated counters and raise error rates.
- `DynamicBloomFilter` extends `Filter` and adds the `(vectorSize, nbHash, hashType, nr)` constructor. Its docs describe row growth: when the active row reaches its configured threshold, a new Bloom filter row is created.
- `RetouchedBloomFilter` is final, extends `BloomFilter`, and implements `RemoveScheme`. It tracks false positives through `addFalsePositive` overloads and can call `selectiveClearing(Key, short)` using a removal scheme.
- `RemoveScheme` defines public short constants `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`, selecting strategies for clearing bits in a retouched Bloom filter.
- `HashFunction` is final and maps one `Key` to `nbHash` positions in a range. It is configured by maximum value, number of hashes, and hash type; `clear` is documented as a no-op.
- `Key` implements `WritableComparable`. It wraps a byte-array value plus double weight, supports constructors with default or explicit weight, `set`, byte/weight getters, weight increment overloads, equality/hash, Writable read/write, and `compareTo(Key)`.

### Hash Package

- `Hash` is the abstract selection and wrapper API. It defines `INVALID_HASH`, `JENKINS_HASH`, and `MURMUR_HASH`; static `parseHashType(String)` for names such as `jenkins` and `murmur`; `getHashType(Configuration)`; `getInstance(int)` and `getInstance(Configuration)` singleton lookup; convenience `hash(byte[])` and `hash(byte[], int initval)`; and abstract `hash(byte[], int length, int initval)`.
- `JenkinsHash` exposes singleton `getInstance`, seeded `hash(byte[] key, int nbytes, int initval)`, and a diagnostic `main(String[])` that computes a file hash. Its docs explicitly identify it as a lookup hash, not a cryptographic hash.
- `MurmurHash` exposes singleton `getInstance` and seeded `hash(byte[] data, int length, int seed)`, documenting a Java port of MurmurHash 2.0.

### MapReduce Status, Counters, and Exceptions

- `ClusterStatus` is a Writable cluster snapshot with task tracker counts, active and blacklisted tracker names, blacklisted tracker count, task tracker expiry interval, running map/reduce task counts, map/reduce capacity, `JobTracker.State`, JobTracker heap-used and max-memory values, plus `write`/`readFields`.
- `Counters` is deprecated in favor of `org.apache.hadoop.mapreduce.Counters` but remains a synchronized Writable/Iterable mapred counter container. It exposes group lookup, enum/string counter lookup, deprecated id-based lookup, individual and bulk increments, static `sum`, size, Writable serialization, logging, text rendering, compact string rendering, escaped compact string round-trip parsing, equality, and hash code.
- `Counters.Counter` extends `org.apache.hadoop.mapreduce.Counter` and preserves old mapred accessors such as `setDisplayName`, `makeEscapedCompactString`, and synchronized `getCounter`.
- `Counters.Group` implements `Writable` and `Iterable`, has raw and display names, display name mutation, escaped compact string output, value lookup, deprecated id/name lookup, name lookup/create, size, read/write, iterator, equality, and hash code. Its docs mention localization through resource bundles.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are typed `IOException` classes for output collisions, unexpected file/directory type, accumulated input validation problems, and invalid job configuration.

### File Input and Output APIs

- `FileInputFormat` is an abstract deprecated base for old file-based `InputFormat`s. It implements `InputFormat`, provides `setMinSplitSize`, default `isSplitable(FileSystem, Path)`, abstract `getRecordReader`, static input path filter setters/getters, protected `listStatus`, concrete `getSplits`, `computeSplitSize`, `getBlockIndex`, static path setters/adders/getters, and protected `getSplitHosts` that ranks hosts/racks by contribution to a split.
- `InputFormat` defines the old split and reader contract: `getSplits(JobConf, int)` produces `InputSplit[]`; `getRecordReader(InputSplit, JobConf, Reporter)` creates readers; the docs assign input validation to implementations and define split-to-map task behavior.
- `InputSplit` is a Writable unit of input with `getLength()` and `getLocations()` for scheduler locality.
- `FileSplit` extends the new `mapreduce.InputSplit` while implementing the old split behavior. It exposes constructors using path/start/length plus either `JobConf` or explicit hosts, and methods `getPath`, `getStart`, `getLength`, `toString`, `write`, `readFields`, and `getLocations`.
- `FileOutputCommitter` extends `OutputCommitter` and implements job/task setup, task commit/abort, cleanup, and `needsTaskCommit`; it exposes `TEMP_DIR_NAME` and is documented as committing files under `${mapred.output.dir}`.
- `FileOutputFormat` is the abstract old output base. It provides static output compression configuration, codec selection, abstract `getRecordWriter`, `checkOutputSpecs`, output/work/task output path helpers, unique task filename helpers, and `getPathForCustomFile`.
- `ID` extends `org.apache.hadoop.mapreduce.ID` and supplies the old mapred numeric identifier base, with default and int constructors.

### Job Client and Job Configuration

- `JobClient` extends `Configured` and is the primary old client API for `JobTracker`. It has constructors for default configuration, `JobConf`, or explicit `InetSocketAddress` plus `Configuration`; `init`, `close`, and `getFs`; submit methods for job files and `JobConf`; internal submission validation; job lookup by `JobID` and deprecated string; map/reduce/setup/cleanup task reports; task display filtering; cluster status queries; running/all job lists; static `runJob`; `monitorAndPrintJob`; task output filter getters/setters; `Tool.run`; default map/reduce capacity queries; system directory lookup; queue listing and queue job/status lookup; and `main`.
- `JobClient.TaskStatusFilter` is an enum with `NONE`, `KILLED`, `FAILED`, `SUCCEEDED`, and `ALL`, used to filter task output displayed during monitoring.
- `JobConf` extends `Configuration` and is itself deprecated in favor of `Configuration`, but it remains the core old job description API. Constructors accept no args, an example class, an inherited `Configuration`, `Configuration` plus example class, XML path as string or `Path`, and a `loadDefaults` boolean.
- `JobConf` configures job jar and classpath localization (`getJar`, `setJar`, `setJarByClass`), local dirs and local cleanup, reported user, failed task file retention and regex retention, working directory, task JVM reuse, input/output formats, output committer, output compression, map-output compression, map-output and final key/value classes, sort comparator, key-field comparator and partitioner options, reduce grouping comparator, old/new mapper and reducer mode flags, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution, map/reduce counts, max attempts, job name, session id, per-tracker failure blacklisting, allowed failure percentages, priority, profiling, debug scripts, job-end notification URI, task local scratch dir, map/reduce memory, queue name, memory normalization, and deprecated virtual/physical memory properties.
- `JobConfigurable.configure(JobConf)` is the old hook for classes initialized from a job configuration.
- `JobContext` extends `org.apache.hadoop.mapreduce.JobContext`, is deprecated in favor of the new API, and exposes old `getJobConf()` plus `getProgressible()`.
- `JobEndNotifier` exposes static lifecycle and notification entry points: `startNotifier`, `stopNotifier`, `registerNotification(JobConf, JobStatus)`, and `localRunnerNotification`.

### Job History APIs

- `JobHistory` initializes and parses append-only history files. Public static methods include `init(JobConf, hostname, jobTrackerStartTime)`, `parseHistoryFromFS(path, Listener, FileSystem)`, `isDisableHistory`, `setDisableHistory`, and `getTaskLogsUrl(TaskAttempt)`. Public fields include `LOG` and `JOB_NAME_TRIM_LENGTH`.
- The `JobHistory` docs describe a plain-text line format `[type (key=value)*]`, one master index plus per-job files named by jobtracker id and job id, and a version change from quote-delimited values to escaped values with a `Meta` record.
- `JobHistory.HistoryCleaner` implements `Runnable` and deletes history data older than one month, updates the master index, and removes job tracker references with no recent jobs.
- `JobHistory.JobInfo` extends a `KeyValuePair` type from the surrounding `JobHistory` model. It exposes task map access, local job file path calculation, URL encoding/decoding of history paths/names, user-name extraction, log-location helpers, current history file name recovery, and static log methods for job submitted/inited/started/finished/failed/killed, priority, and arbitrary job info updates.
- `JobHistory.Keys` is an enum of history log field names including jobtracker id, start/finish/submit/launch times, job id/name/user/conf, map/reduce totals and completions/failures, job/task/attempt status, task ids, host/tracker/http-port data, shuffle/sort/reduce timing keys, counters, splits, priority, state string, and version.
- `JobHistory.Listener.handle(RecordTypes, Map)` is the streaming parser callback invoked per history record.
- `JobHistory.MapAttempt` and `JobHistory.ReduceAttempt` extend `TaskAttempt` and provide static log methods for start, finish, failure, and kill. The newer overloads include tracker/http-port/task-type data, finish state strings, and counters; older overloads are deprecated but retained.
- `JobHistory.Task` logs task start, finish, update, and failure events, including an overload that records the failed attempt responsible for a task failure. It also exposes `getTaskAttempts`.
- `JobHistory.TaskAttempt` is the common base for map and reduce attempts.
- `JobHistory.RecordTypes` enumerates line types `Jobtracker`, `Job`, `Task`, `MapAttempt`, `ReduceAttempt`, and `Meta`.
- `JobHistory.Values` enumerates common serialized values such as `SUCCESS`, `FAILED`, `KILLED`, `MAP`, `REDUCE`, `CLEANUP`, `RUNNING`, `PREP`, and `SETUP`.

## Control Flow

For utility command-line execution, a `ToolRunner`-based program accepts generic Hadoop options, lets `GenericOptionsParser` mutate the `Configuration`, then runs application-specific `Tool` logic. The chunk only contains the final generic usage method and docs, but the flow is explicit in the enclosing class documentation.

`UTF8ByteArrayUtils` control flow is index scanning. Callers provide a byte array and bounds; methods search for a single byte, byte sequence, or nth byte occurrence and return offsets without validating or decoding the complete UTF-8 sequence.

Bloom filter flow starts by constructing a filter with vector size, number of hashes, and hash type. `HashFunction.hash(Key)` maps key bytes to multiple vector positions. Concrete filters then set, count, test, clear, or combine those positions according to their specific representation. Bulk `Filter.add` methods repeatedly call single-key `add`. Logical operations mutate `this`, so `and`, `or`, `xor`, and `not` are in-place rather than returning new filter instances.

Counting Bloom filter flow differs because deletion is possible only when the key is believed present. `approximateCount` computes an approximate multiplicity and can overestimate due to false positives or underestimate if earlier deletes caused underflow. Dynamic Bloom filter flow grows by rows when the active row reaches the configured insertion threshold. Retouched Bloom filter flow records known false-positive keys, then `selectiveClearing` clears selected bits according to `RemoveScheme`, trading false-positive removal against newly introduced false negatives.

Hash selection flow starts from a string or configuration value. `Hash.parseHashType` maps supported names to constants, `Hash.getInstance` returns a singleton implementation, and callers pass byte arrays, valid lengths, and seeds into `hash`. These hashes are non-cryptographic and are expected to be deterministic across process and serialization boundaries.

MapReduce input flow begins with `JobConf` carrying configured input paths and optional filters. `FileInputFormat.listStatus` resolves and filters input files; `getSplits` computes split sizes from goal/min/block sizes, consults block locations, ranks split hosts, and returns `FileSplit`s. The framework later asks the concrete `InputFormat` for a `RecordReader` per split. Implementations must preserve record boundaries and validate input either before or during split generation.

MapReduce output flow starts with `JobConf` and `FileOutputFormat` output path/compression settings. `checkOutputSpecs` validates the final destination before submission. Tasks write through a `RecordWriter` under a task/work output path. `FileOutputCommitter` sets up job/task locations, determines whether task output needs committing, promotes successful task output, and aborts failed task attempts.

Job submission flow in `JobClient` is documented as checking input/output specs, computing `InputSplit`s, preparing `DistributedCache` accounting, copying the jar and configuration to the JobTracker system directory on the distributed filesystem, submitting to `JobTracker`, and optionally monitoring progress. `runJob` composes submission with polling until completion; `submitJob` returns a `RunningJob` for external orchestration; job-end notifications provide asynchronous chaining.

`JobConf` control flow is configuration-as-contract. User code sets classes, paths, comparators, compression, reducer counts, failure policies, queues, profiling, scripts, memory, and notification settings. Job submission and task execution then interpret those keys to create input readers, map/reduce runners, partitioners, comparators, committers, task JVMs, and task-local resources.

Counter flow is synchronized at the container level. Callers find or create counters by enum or group/name, increment values, merge another `Counters` object, then serialize them to job/task status and history. Compact string methods provide text round trips for history and diagnostics.

Job history write flow appends event records as plain text. Static log helpers on `JobInfo`, `Task`, `MapAttempt`, and `ReduceAttempt` emit records keyed by `JobHistory.Keys` and classified by `RecordTypes`. Parse flow streams a history file from `FileSystem`, parses each line into a record type and key/value map, and calls `Listener.handle`, allowing callers either to build a full object model or scan without retaining all records.

## State and Persistence Behavior

The XML file persists the Hadoop 0.20.1 public API for JDiff comparison. Runtime state lives in the documented Java classes, but the API signatures here define important persistence contracts.

`Filter`, `BloomFilter`, `CountingBloomFilter`, `DynamicBloomFilter`, `RetouchedBloomFilter`, `Key`, `ClusterStatus`, `Counters`, `Counters.Group`, `FileSplit`, and `InputSplit` expose Hadoop `Writable` binary persistence through `DataOutput` and `DataInput`. Field order, numeric encodings, hash type constants, vector dimensions, and counter names are compatibility-sensitive.

Bloom filter state includes vector size, number of hash functions, selected hash algorithm, and subclass-specific bit/counter/matrix/false-positive data. Serialized filters are only meaningful when readers interpret the same hash constants and vector layout. `Key` stores raw bytes and a double weight; equality, ordering, and serialized form depend on byte content and weight semantics.

`Hash` type constants are persistent identifiers because filter state stores the chosen hash type. Changing constant values or default hash configuration would change filter behavior even if serialized bytes still read successfully.

`ClusterStatus` persists a snapshot of JobTracker-visible cluster state: tracker sets/counts, task counts/capacities, expiry interval, JobTracker state, and memory values. It is not authoritative durable cluster state, but its Writable form is used across client/server boundaries.

`Counters` persist grouped long values, raw names, display names, and localized display behavior. Their documented binary external format starts with a group count and then writes groups and counters with display-name presence flags. Escaped compact strings are another external form used by history logs and diagnostics.

`FileSplit` persists path, byte start, byte length, and host locations. This allows split plans computed on the client/JobTracker side to be shipped to task trackers. Incorrect serialization affects data locality, reader offsets, and task assignment.

`FileInputFormat` and `FileOutputFormat` persist intent through `JobConf` keys: input paths, input filters, min split size, output path, output compression flag, output codec, and task output naming. Actual input/output bytes persist in `FileSystem` paths; the API layer coordinates validation and staging.

`FileOutputCommitter` owns transient and final output directory state, including the public `TEMP_DIR_NAME`. Commit/abort behavior determines whether task attempt files become final output or are cleaned up.

`JobConf` persists job behavior as configuration keys and class names. Jar location, mapper/reducer classes, formats, comparators, partitioner, compression codecs, counts, retries, failure thresholds, queue, notification URI, debug scripts, profiling ranges, memory limits, and output paths all become part of the submitted job. It also bridges local filesystem state through local dirs, local job dir, and failed-task artifact retention.

`JobClient` holds process-local client state such as JobTracker connection, filesystem handle, and task output filter, while its submission path persists job jars/configuration/splits into the JobTracker system directory.

`JobHistory` persists append-only text logs and a master index. Event keys and enum names are durable because history lines store strings. Version 1 escaping and the `Meta` version record are explicitly part of the parse contract. `HistoryCleaner` mutates persistent history directories by deleting old files and updating/removing index entries.

`JobEndNotifier` persists no durable state in this API metadata, but it schedules or executes side effects: invoking configured notification URIs after job completion. The notification URI itself is stored in `JobConf` and may interpolate `$jobId` and `$jobStatus`.

## Dependencies and Integration Points

- Java platform dependencies include `InputStream`, `Writer`, `PrintStream`, `DataInput`, `DataOutput`, `IOException`, `InetSocketAddress`, collections, enums, text parsing, XSLT transformers, and class reflection through configuration.
- Hadoop configuration types (`Configuration`, `JobConf`, `Configured`, `Configuration.IntegerRanges`) drive hash selection, job configuration, class loading, local directories, task memory, queues, notifications, profiling, and mapred/new-API bridging.
- Hadoop serialization dependencies include `Writable`, `WritableComparable`, and `RawComparator`, which underlie Bloom keys, filters, cluster status, counters, splits, and comparator configuration.
- Hadoop filesystem dependencies include `FileSystem`, `Path`, `FileStatus`, `BlockLocation`, and `PathFilter` for input listing, split planning, output validation, job staging, and history parsing.
- Hadoop compression integration appears through `CompressionCodec` class configuration for map outputs and final outputs.
- MapReduce old API dependencies include `Mapper`, `Reducer`, `MapRunner`, `Partitioner`, `InputFormat`, `OutputFormat`, `OutputCommitter`, `RecordReader`, `RecordWriter`, `Reporter`, `OutputCollector`, `RunningJob`, `JobStatus`, `TaskReport`, `TaskID`, `TaskAttemptID`, `JobPriority`, `JobTracker`, `DistributedCache`, and queue info classes.
- New MapReduce API integration appears where old classes extend or refer to `org.apache.hadoop.mapreduce` equivalents, including `Counter`, `InputSplit`, `ID`, and `JobContext`.
- Network topology integration appears in `FileInputFormat.getSplitHosts`, which uses `org.apache.hadoop.net.NetworkTopology` and block/rack locality to pick split hosts.
- Logging integration uses Apache Commons Logging in `FileInputFormat`, `FileOutputCommitter`, `Counters.log`, and `JobHistory.LOG`.
- Job history integration spans filesystem storage, task tracker log URLs, JobTracker identity/start time, task attempt IDs, counters, and parser listeners.

## Risks and Edge Cases

- The chunk begins mid-`ToolRunner` and ends mid-`JobID`; final class-level analysis for those types requires adjacent chunks.
- JDiff metadata omits method bodies. Exact binary layouts, configuration key names, synchronization internals, committer rename/delete logic, split math, and history escaping rules need implementation review.
- `UTF8ByteArrayUtils` searches bytes, not Unicode code points. Multi-byte UTF-8 content is safe for delimiter bytes only when callers understand byte-level semantics.
- Bloom filter logical operations mutate the receiver. Callers expecting persistent immutable filters can corrupt cached filter state.
- Bloom filter operations require compatible vector size, hash count, and hash type across operands. The API does not show whether mismatches are rejected or silently miscomputed.
- `CountingBloomFilter.approximateCount` has explicit overflow and underflow caveats. Counts above 15 for one key can raise false-positive rates, and deletes after underflow can introduce false negatives.
- `RetouchedBloomFilter.selectiveClearing` deliberately introduces false negatives to remove false positives. Consumers relying on standard Bloom "no false negatives" behavior must not treat retouched filters as ordinary Bloom filters.
- `Hash` implementations are non-cryptographic. They must not be used for authentication, tamper resistance, or adversarial collision protection.
- Changing default hash selection or hash constants breaks persisted Bloom filter behavior even if the serialized structure still loads.
- Many `mapred` APIs are deprecated but public. Removing old overloads, changing deprecation-only behavior, or forcing new `mapreduce` classes can break Hadoop 0.20-era applications.
- `Counters` has synchronized methods, but iterators over groups/counters can still expose concurrent mutation hazards depending on implementation. Tests should cover mutation during iteration and serialization.
- Counter display names and escaped compact strings are externally visible in job history and tooling. Escaping regressions break parsers and dashboards.
- `FileInputFormat.listStatus` must handle empty inputs, nonexistent paths, directory/file mismatches, globs, hidden files, custom `PathFilter`s, and permission errors. The API promises `IOException` if zero items.
- `FileInputFormat.getSplitHosts` balances rack and host contribution. Locality bugs may not fail correctness tests but can degrade cluster performance.
- Unsplittable inputs, especially stream-compressed files, rely on `isSplitable` returning false. Incorrect overrides can split non-seekable compressed streams.
- `FileOutputFormat.checkOutputSpecs` can catch existing output paths before submission, but filesystem races can still occur between check and commit.
- `FileOutputCommitter` correctness depends on temporary path isolation per task attempt. Retry/speculation races can corrupt or overwrite output if commit paths collide.
- `JobClient.submitJob` crosses filesystem staging, split computation, distributed cache setup, and JobTracker RPC. Partial failures can leave staged job files or a submitted job without a live client handle.
- Deprecated string-based `JobClient` APIs coexist with `JobID` overloads. Compatibility tests need both, especially parsing and error behavior.
- `JobConf.setNumMapTasks` documentation in this range warns that map counts are usually derived from input size and split size. Treating it as an exact control can lead to surprises.
- Setting zero reducers bypasses shuffle/sort and writes map output directly to the final output path. Applications depending on sort/group semantics must test reducer count changes.
- Speculative execution, failure percentages, max attempts, and per-tracker blacklisting interact. Invalid combinations can cause jobs to fail too early or tolerate too much data loss.
- Debug scripts and job-end notification URIs execute external commands or network callbacks. Configuration injection and access control are deployment concerns outside this API surface.
- Task profiling parameters are passed to child JVMs. Bad strings can prevent task JVM startup or write profile output to unexpected locations.
- Memory APIs include both newer map/reduce memory settings and deprecated virtual/physical memory properties. Unit conversions and disabled sentinel values are compatibility risks.
- `JobHistory` is append-only text with versioned escaping. Broken escaping or enum-name changes can make old logs unparsable.
- `JobHistory.HistoryCleaner` deletes persistent files older than one month and rewrites index state. Clock skew, retention policy changes, or parser failures can remove useful audit data.
- `JobHistory.getTaskLogsUrl` returns null when tracker name, http port, or attempt id is unavailable. UIs and tooling must not assume a URL is always present.
- Several history logging overloads are deprecated but still public. Old task trackers or tools may still emit/read old host-name-only forms.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility checks for all classes, interfaces, constructors, methods, fields, visibility flags, static/final/synchronized/abstract markers, declared exceptions, inheritance, implemented interfaces, and deprecation strings in lines 31470-37821.
- `UTF8ByteArrayUtils` tests for first-byte, byte-sequence, nth-byte, start/end bounds, zero-length ranges, missing delimiters, and multi-byte UTF-8 payloads where the delimiter byte appears only as an actual delimiter.
- `VersionInfo` tests with packaged version annotations/properties and `main` output smoke checks.
- `XMLUtils.transform` tests for successful stylesheet application and transformer configuration/runtime exception propagation.
- Bloom filter round-trip tests for each concrete filter using `write`/`readFields`, including empty filters, multiple keys, compatible/incompatible hash parameters, and logical operations.
- Standard Bloom filter tests proving no false negatives for inserted keys and measuring/allowing false positives for non-inserted keys.
- Counting Bloom tests for add/delete, delete of absent keys, approximate counts, overflow around repeated insertions above 15, and underflow behavior after deletes.
- Dynamic Bloom tests for row creation once insertion thresholds are reached and membership across multiple rows.
- Retouched Bloom tests for all `RemoveScheme` constants, false-positive registration overloads, selective clearing, and expected introduced false negatives.
- `Key` tests for byte/value mutation, weight increment overloads, equality/hash/compare consistency, and Writable serialization of byte arrays plus double weights.
- `Hash` tests for parsing valid/invalid names, configuration selection, singleton lookup, Jenkins/Murmur deterministic vectors, seeded hash behavior, length-limited hashing, and invalid hash returning null.
- `ClusterStatus` Writable round trips for detailed and non-detailed tracker-name modes, blacklisted trackers, capacity/task counts, JobTracker state, expiry interval, and memory values.
- `Counters` tests for enum and string counter lookup, deprecated id lookup, increments, merges, `sum`, group/display name localization, equality/hash, binary serialization, compact string output, escaped compact string round trip, parse errors, and concurrent access where supported.
- `FileInputFormat` tests for input path setters/adders, comma-separated path parsing, path filters, empty inputs, nonexistent inputs, directories/files, split size math, unsplittable files, block-index lookup, and host/rack locality selection.
- `InputFormat`/`InputSplit`/`FileSplit` tests for Writable round trips, path/start/length/location correctness, record reader creation, and deprecated constructor compatibility.
- `FileOutputFormat` tests for output path configuration, existing-output failure, missing-output invalid configuration, compression flag/codec selection, work/task output path calculation, unique name generation, and custom file paths.
- `FileOutputCommitter` tests for setup/commit/abort/idempotency, `needsTaskCommit`, speculative attempts, failed attempts, cleanup, and temp directory layout.
- `JobClient` tests covering constructors, init/close, job submission validation, staging paths, deprecated string job APIs, task report retrieval for map/reduce/setup/cleanup, task display filters, cluster status, queue APIs, `runJob`, and `monitorAndPrintJob` under success and failure.
- `JobConf` tests for all high-impact setters/getters: jar/class discovery, local dirs, user, failed-task file retention, working directory, JVM reuse, input/output classes, committer, compression, key/value classes, comparators, grouping comparator, mapper/reducer mode flags, speculative execution, task counts, attempts, failure percentages, priority, profiling, debug scripts, notification URI substitution, memory settings, queue name, and deprecated memory property migration.
- `JobEndNotifier` tests for start/stop lifecycle, local runner notification, configured URI callbacks, failed callback retry behavior if implemented, and `$jobId`/`$jobStatus` substitution.
- `JobHistory` tests for initialization, disable/enable switch, append log line generation for submitted/inited/started/finished/failed/killed jobs, task and attempt events, counters in history, version/meta records, escaping/unescaping, listener streaming parse, object-model parse via `DefaultJobHistoryParser`, task log URL generation, recovery of history filenames, and cleanup retention boundaries.
