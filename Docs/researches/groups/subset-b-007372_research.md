# Research: subset-b-007372 Hadoop util source files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Preconditions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Preconditions.java

## Purpose
`Preconditions` is Hadoop's private replacement for the small subset of Guava precondition helpers used in common code. It validates null references, argument predicates, and state predicates while preserving familiar exception types.

## Important APIs, Types, And Functions
The class is final with only static helpers. Key APIs are `checkNotNull(T)`, `checkNotNull(T,Object)`, `checkNotNull(T,String,Object...)`, `checkNotNull(T,Supplier<String>)`, `checkArgument(...)`, and `checkState(...)`. Package-visible getters expose default messages for tests.

## Control Flow
Each method returns immediately on success. On failure it either stringifies an object message, formats a varargs template, or evaluates a supplier. Formatting/supplier failures are caught, logged at debug, and replaced by a default message before throwing `NullPointerException`, `IllegalArgumentException`, or `IllegalStateException`.

## State And Persistence
There is no mutable business state. Static constants hold default messages, and a static SLF4J logger records message-construction failures. Nothing is persisted.

## Dependencies And Integration Points
It depends on `java.util.function.Supplier`, SLF4J, and Hadoop audience/stability annotations. It is integrated anywhere Hadoop wants low-overhead validation without carrying a public Guava dependency.

## Risks
Supplier-based messages are evaluated only on failure, but a null supplier on a failed check becomes a debug log plus default message rather than exposing the supplier bug. Varargs formatting uses `String.format`, so invalid format strings do not propagate. Successful checks do not validate message templates.

## Test Signals
Useful tests verify successful identity return, exception type and message for each overload, fallback behavior when format/supplier evaluation fails, and debug-only logging of message construction errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Preconditions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PrintJarMainClass.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PrintJarMainClass.java

## Purpose
`PrintJarMainClass` is a tiny private command-line utility that prints the `Main-Class` declared in a jar manifest. It is intended for scripts or launch plumbing that need to inspect jars without running them.

## Important APIs, Types, And Functions
The only API is `main(String[] args)`. It opens `args[0]` as a `JarFile`, obtains the manifest, reads the main attributes, and prints the normalized class name.

## Control Flow
The command tries to read the jar in a try-with-resources block. If a manifest and `Main-Class` exist, slashes are replaced with dots, the value is printed, and the method returns normally. Any `Throwable`, missing argument, unreadable jar, missing manifest, or absent attribute falls through to printing `UNKNOWN` and exiting with status `1`.

## State And Persistence
No mutable or persistent state is kept. The process writes one line to stdout and may terminate the JVM with a nonzero code.

## Dependencies And Integration Points
It depends on `java.util.jar.JarFile` and `Manifest`, plus Hadoop annotations. It pairs conceptually with `RunJar`, which uses the same manifest attribute to locate entry points.

## Risks
The broad `catch (Throwable)` hides malformed input details, including programming errors such as missing `args[0]`. Output goes to stdout even on failure, so callers must check exit status if `UNKNOWN` could also be meaningful.

## Test Signals
Tests should cover jars with slash and dotted `Main-Class` values, missing manifests, missing attributes, nonexistent files, empty argument arrays, and process exit code handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PrintJarMainClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PriorityQueue.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PriorityQueue.java

## Purpose
`PriorityQueue<T>` is an old Hadoop/Lucene-style abstract min-heap. Subclasses supply ordering through `lessThan`, and the implementation provides constant-time top lookup plus logarithmic insert and pop.

## Important APIs, Types, And Functions
Subclasses call `initialize(int maxSize)` and implement `lessThan(Object,Object)`. Public operations are `put`, `insert`, `top`, `pop`, `adjustTop`, `size`, and `clear`. Internal heap maintenance lives in `upHeap` and `downHeap`.

## Control Flow
The heap is one-based: `heap[1]` is the least element. `put` appends and bubbles up. `insert` either appends, replaces the current top when full and the new element is not less than the top, or rejects the element. `pop` swaps in the last element, clears the old slot for GC, and bubbles down. `adjustTop` assumes the top object changed and only repairs downward.

## State And Persistence
Mutable state is the backing array, current size, and max size. There is no synchronization and no persistence. `clear` nulls occupied slots.

## Dependencies And Integration Points
It depends only on Hadoop annotations and Java arrays. Integrations must provide a strict, stable ordering via `lessThan`.

## Risks
Calling `put` beyond `maxSize` throws an array bounds exception. `insert` implements a bounded top-N pattern whose replacement semantics are easy to misuse. Non-transitive comparators can corrupt heap ordering, and concurrent access is unsafe.

## Test Signals
Tests should check heap ordering, bounded insertion behavior, `adjustTop` after mutating top priority, clearing GC slots, max-size overflow, duplicate/equal keys, and null behavior if subclasses allow it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PriorityQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProcessUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProcessUtils.java

## Purpose
`ProcessUtils` centralizes a small amount of process-related support: locating the current JVM PID and launching a command asynchronously with inherited IO.

## Important APIs, Types, And Functions
The class exposes `getPid()` and `runCmdAsync(List<String>)`. It is final with a private constructor and a static logger.

## Control Flow
`getPid` first reads `JVM_PID` from the environment. If absent or blank, it falls back to the runtime MXBean name and parses the substring before `@`. Invalid or missing values return null. `runCmdAsync` logs the command, builds a `ProcessBuilder`, inherits the current process IO streams, starts it, and wraps `IOException` in `IllegalStateException`.

## State And Persistence
No state is retained. `runCmdAsync` creates an OS child process whose lifecycle is returned to the caller as `Process`; this file does not track or reap it.

## Dependencies And Integration Points
It depends on `ManagementFactory`, `ProcessBuilder`, SLF4J, and Hadoop annotations. It complements the richer `Shell` API when callers only need fire-and-return process launch.

## Risks
PID discovery is platform and JVM-name dependent. `JVM_PID` may be stale or invalid. Inherited IO can leak output to service logs and can couple child process lifetime to inherited descriptors. Wrapping launch errors as unchecked exceptions may surprise callers expecting `IOException`.

## Test Signals
Tests should cover valid/invalid `JVM_PID`, MXBean fallback parsing, null return on unparsable names, async launch success, and checked-to-unchecked exception conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProcessUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProgramDriver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProgramDriver.java

## Purpose
`ProgramDriver` is a small command dispatcher for Hadoop examples and tools. It maps user-visible command names to classes with static `main(String[])` methods and invokes the selected program.

## Important APIs, Types, And Functions
Important members are the `TreeMap<String,ProgramDescription> programs`, `addClass`, `run`, `driver`, `printUsage`, and nested `ProgramDescription`. The nested class stores a reflected `main` method and a help description.

## Control Flow
`addClass` resolves the target class's public `main(String[])` method and stores it by name. `run` validates that the first argument names a registered program, prints usage for missing or unknown names, shifts remaining arguments into a new array, invokes the target main, unwraps `InvocationTargetException`, and returns `0`. `driver` preserves the Hadoop 1.x API by calling `System.exit(-1)` on usage errors.

## State And Persistence
State is an in-memory sorted map of registered programs. There is no synchronization and no persistence.

## Dependencies And Integration Points
It depends on Java reflection and Hadoop annotations. It integrates with command-line entry points that want a single binary to expose many subcommands.

## Risks
Only public `main` methods are accepted. Exceptions from target programs propagate as their original cause. Concurrent mutation of `programs` is unsafe. Usage text goes to stdout, not stderr.

## Test Signals
Tests should cover registration, sorted usage output, unknown command handling, argument shifting, propagation of target exceptions, and `driver` exit behavior through process-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProgramDriver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progress.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progress.java

## Purpose
`Progress` models hierarchical task progress for MapReduce-style execution. A root node can contain weighted or equal phases, and leaf nodes report a normalized progress value.

## Important APIs, Types, And Functions
Key APIs are `addPhase`, `addPhases`, `startNextPhase`, `phase`, `complete`, `set`, `get`, `getProgress`, `setStatus`, and `toString`. Fields track status text, leaf progress, current phase index, child phases, parent, equal-weight mode, per-phase weight, and custom weight list.

## Control Flow
Adding phases creates child `Progress` nodes and either recalculates equal weight per child or records explicit weights. `set` clamps NaN, infinities, and out-of-range values into `[0,1]`. `get` walks to the root and recursively computes completed-phase contribution plus current child contribution. `complete` marks the node complete and advances the parent phase while deliberately releasing the child lock before locking the parent.

## State And Persistence
All state is in-memory and mostly protected with synchronized methods. There is no persistence. Parent links are stable after child creation.

## Dependencies And Integration Points
It depends on SLF4J and Hadoop annotations. `QuickSort` and MapReduce code use `Progressable`/progress reporting to avoid timeout assumptions during long operations.

## Risks
Mixing equal-weight and explicit-weight phases on one node can leave inconsistent weight lists. Explicit weights can sum above one; the code warns but still allows it. `phase()` can throw if `currentPhase` is out of range.

## Test Signals
Tests should cover nested weighted and unweighted progress, clamping, `complete` parent advancement, status rendering path, over-one weight warnings, and concurrent reads during completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progressable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progressable.java

## Purpose
`Progressable` is Hadoop's stable public callback interface for code that must report liveness or progress to the framework during long-running operations.

## Important APIs, Types, And Functions
The interface declares one method, `progress()`. Implementations decide how to propagate that signal.

## Control Flow
There is no built-in control flow. Callers invoke `progress()` opportunistically from loops or blocking operations. Framework implementations can reset timeout counters, update task status, or drive monitoring.

## State And Persistence
The interface owns no state and no persistence. State is entirely implementation-specific.

## Dependencies And Integration Points
It depends only on Hadoop annotations. It appears in utility algorithms such as `QuickSort.sort(..., Progressable)` and in Hadoop IO/MapReduce paths where repeated progress signals prevent false task timeouts.

## Risks
The contract does not specify idempotency, blocking behavior, or exception handling. Callers should assume implementations may be nontrivial and avoid invoking it while holding locks that could deadlock with framework callbacks.

## Test Signals
Tests generally use counting implementations to assert that long-running utilities call `progress()` and that exceptions or slow callbacks are handled according to the caller's own contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Progressable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProtoUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProtoUtil.java

## Purpose
`ProtoUtil` contains protobuf and Hadoop RPC wire helpers: protobuf varint decoding, IPC connection context construction, UGI reconstruction, RPC kind conversion, and RPC request header construction.

## Important APIs, Types, And Functions
Important APIs are `readRawVarint32`, `makeIpcConnectionContext`, `getUgi`, `convert(RPC.RpcKind)`, `convert(RpcKindProto)`, and `makeRpcRequestHeader`. The request header path integrates trace, caller context, authorization header, and optional alignment context state.

## Control Flow
`readRawVarint32` manually decodes up to five significant bytes and discards up to five upper bytes before declaring a malformed varint. Connection-context construction conditionally sends user fields based on auth method: Kerberos sends effective user, token sends none, simple sends effective and optional real user. Header construction sets core RPC fields, then conditionally attaches tracing, caller context, authorization bytes, and alignment state.

## State And Persistence
The class is stateless. It reads thread-local/current context from tracing, caller context, authorization context, and alignment context, then serializes it into protobuf messages.

## Dependencies And Integration Points
It depends on Hadoop IPC protobuf classes, `RPC`, `UserGroupInformation`, SASL auth methods, tracing, authorization context, and third-party protobuf `ByteString`.

## Risks
Wire compatibility is critical. Returning null for unknown enum conversions can defer failures. Auth-method-specific UGI elision must remain aligned with server-side authentication assumptions. Context propagation can leak caller or authorization metadata if set incorrectly.

## Test Signals
Tests should cover malformed varints, auth-method matrix for context fields, proxy-user reconstruction, enum round trips, trace/caller/authorization propagation, and alignment-context mutation of request headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ProtoUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32.java

## Purpose
`PureJavaCrc32` preserves Hadoop's public CRC32 class name while delegating normal checksum behavior to the JDK native `java.util.zip.CRC32`, which is faster on modern JVMs.

## Important APIs, Types, And Functions
The class extends `CRC32` and does not override update/reset/value methods. Its Hadoop-specific API is static `mod(long)`, which computes reduction by the CRC32 polynomial using the retained lookup table `T`.

## Control Flow
Checksum operations use inherited JDK behavior. `mod` splits the long into high and low words, indexes four slices of `T` from the low word's bytes, XORs the table results, and XORs the high word.

## State And Persistence
Per-instance checksum state is owned by the superclass. Static table `T` is immutable and retained for polynomial math compatibility. There is no persistence.

## Dependencies And Integration Points
It depends on `java.util.zip.CRC32` and Hadoop annotations. It integrates with Hadoop checksum code expecting the historical `PureJavaCrc32` type and `mod` helper.

## Risks
Behavior now depends on JDK CRC32 implementation, so compatibility must be checked across supported JDKs. The large static table is easy to corrupt mechanically. Subclassing `CRC32` preserves API but may differ from the legacy pure-Java performance/profile assumptions.

## Test Signals
Tests should compare values with known CRC32 vectors, exercise incremental and bulk updates through inherited methods, validate `reset`, and verify `mod(long)` against independently generated polynomial reductions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32C.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32C.java

## Purpose
`PureJavaCrc32C` preserves Hadoop's historical CRC32C checksum type while delegating checksum operations to JDK `CRC32C`, which is final and therefore wrapped rather than subclassed.

## Important APIs, Types, And Functions
The class implements `Checksum`. It delegates `update(int)`, `update(byte[])`, `update(byte[],int,int)`, `update(ByteBuffer)`, `getValue`, and `reset` to a private `CRC32C delegate`. Static `mod(long)` uses a retained CRC32C polynomial table `T`.

## Control Flow
All mutable checksum operations are direct pass-through calls to the delegate. `mod` mirrors the CRC32 version but uses the Castagnoli polynomial table.

## State And Persistence
Instance state lives inside the delegate. Static lookup table data is immutable. No persistent state exists.

## Dependencies And Integration Points
It depends on `java.util.zip.Checksum`, `CRC32C`, `ByteBuffer`, and Hadoop annotations. It integrates with Hadoop checksum paths that require CRC32C but still reference the older `PureJavaCrc32C` class.

## Risks
JDK `CRC32C` availability and behavior are now part of the contract. ByteBuffer update semantics, including position advancement, follow JDK behavior. Static polynomial data must stay exact for `mod` compatibility.

## Test Signals
Tests should cover standard CRC32C vectors, byte-array slices, ByteBuffer updates, reset behavior, multiple update forms producing identical values, and `mod(long)` consistency with generated CRC32C polynomial arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PureJavaCrc32C.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/QuickSort.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/QuickSort.java

## Purpose
`QuickSort` implements Hadoop's indexed introspective quicksort for `IndexedSortable` collections, with insertion sort for tiny ranges and heapsort fallback for deep recursion.

## Important APIs, Types, And Functions
It implements `IndexedSorter`. Public APIs are `sort(IndexedSortable,int,int)` and `sort(IndexedSortable,int,int,Progressable)`. Important helpers are `getMaxDepth`, `fix`, and `sortInternal`. A static `HeapSort` instance is the fallback sorter.

## Control Flow
Sorting reports progress once per `sortInternal` entry when a reporter is supplied. Ranges shorter than 13 are insertion-sorted. Larger ranges use median-of-three pivot setup, three-way partitioning that groups values equal to the pivot at both ends, and recursion on the smaller side first while iterating on the larger side to limit stack depth. If depth drops below zero, heapsort handles the range.

## State And Persistence
The sorter has no per-sort mutable state outside the call stack. It mutates the caller's indexed collection through `swap`.

## Dependencies And Integration Points
It depends on `IndexedSorter`, `IndexedSortable`, `HeapSort`, `Progressable`, and Hadoop annotations. It is useful for sortable views where copying into arrays is undesirable.

## Risks
Comparator consistency is mandatory. `getMaxDepth` rejects nonpositive ranges; callers passing equal bounds into `sort` can trigger an exception. Progress callbacks inside sorting can introduce latency or reentrancy concerns.

## Test Signals
Tests should cover empty/single ranges, duplicate-heavy data, already sorted and reverse data, fallback triggering through adversarial comparators, progress callback invocation, and sort correctness over custom indexed containers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/QuickSort.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimiting.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimiting.java

## Purpose
`RateLimiting` is Hadoop's minimal private abstraction for acquiring capacity from a rate limiter while reporting the time spent waiting as a `Duration`.

## Important APIs, Types, And Functions
The interface declares `Duration acquire(int requestedCapacity)`.

## Control Flow
There is no implementation in this file. The contract allows an implementation to grant a request even when capacity is not currently available and make a subsequent request block until capacity refills, matching Guava `RateLimiter` behavior.

## State And Persistence
The interface owns no state. Implementations maintain token-bucket or no-op state.

## Dependencies And Integration Points
It depends on `java.time.Duration` and Hadoop annotations. `RateLimitingFactory` provides the built-in unlimited and Guava-backed implementations. Object-store and throttling code can depend on this interface without importing Guava directly.

## Risks
The interface does not define validation for zero or negative requested capacity, fairness, interrupt handling, or whether returned duration is exact or rounded. Callers must understand implementation semantics.

## Test Signals
Tests should be implementation-focused: no-op returns zero duration, restricted limiters delay as expected, invalid capacity behavior is documented, and call sites account for returned wait durations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimiting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimitingFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimitingFactory.java

## Purpose
`RateLimitingFactory` is the only Hadoop common utility class that imports the shaded Guava `RateLimiter`, hiding that dependency behind the `RateLimiting` interface.

## Important APIs, Types, And Functions
Public APIs are `unlimitedRate()` and `create(int capacity)`. Internal implementations are `NoRateLimiting` and `RestrictedRateLimiting`. `INSTANTLY` is the shared zero-duration result.

## Control Flow
`create(0)` returns the singleton unlimited limiter. Other capacities create a `RateLimiter` at the requested permits per second. `RestrictedRateLimiting.acquire` calls Guava `acquire(requestedCapacity)`, receives seconds as a double, and converts to milliseconds in a `Duration`, returning the shared zero duration for no delay.

## State And Persistence
The unlimited limiter has no mutable state. Restricted instances hold Guava limiter state in memory. Nothing is persisted.

## Dependencies And Integration Points
It depends on shaded Guava, `Duration`, Hadoop annotations, and `RateLimiting`. It integrates with callers that need throttling without direct Guava API exposure.

## Risks
Negative capacity is passed to `RateLimiter.create` and will fail there. Wait time is truncated to milliseconds, losing submillisecond precision. `capacity == 0` means unlimited, not blocked. Requested capacity validation is delegated to Guava.

## Test Signals
Tests should verify singleton unlimited behavior, zero-duration no-op acquisitions, restricted acquisition delay and duration conversion, invalid capacity handling, and that no other common code imports Guava `RateLimiter` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RateLimitingFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidator.java

## Purpose
`ReadWriteDiskValidator` verifies a directory by checking directory validity, writing random bytes to a temporary file, reading them back, comparing content, and recording latency/failure metrics.

## Important APIs, Types, And Functions
The class implements `DiskValidator` and exposes `NAME = "read-write"` plus `checkStatus(File dir)`. It uses `ReadWriteDiskValidatorMetrics`, `DiskChecker.checkDir`, `Files.createTempFile`, `Files.write`, `Files.readAllBytes`, and `DiskErrorException`.

## Control Flow
`checkStatus` gets the metrics object for the directory, rejects non-directories, delegates permission/existence checks to `DiskChecker`, creates a temp file in the target directory, writes 16 random bytes while timing microseconds, reads the file while timing microseconds, compares byte arrays, and deletes the temp file in `finally`. IO failures and content mismatch increment failure metrics and throw `DiskErrorException`.

## State And Persistence
The validator has no instance state. A static `Random` supplies test bytes. It creates and deletes one temp file; failures during deletion are reported as disk-check failures.

## Dependencies And Integration Points
It integrates with Hadoop's disk validator framework and metrics2 through `ReadWriteDiskValidatorMetrics`.

## Risks
The random generator is shared but `Random` is thread-safe enough through synchronization in modern JDK internals; contention is possible. Deletion failure masks prior success as a disk failure. The 16-byte write tests basic IO, not capacity, fsync, or sustained performance.

## Test Signals
Tests should cover valid directories, non-directories, permission failures, read/write corruption simulation, metrics latency updates, failure counter updates, and cleanup failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidatorMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidatorMetrics.java

## Purpose
`ReadWriteDiskValidatorMetrics` registers and updates metrics for each directory checked by `ReadWriteDiskValidator`, including failure count, last failure time, and read/write latency quantiles.

## Important APIs, Types, And Functions
Important members are annotated `MutableCounterInt failureCount`, `MutableGaugeLong lastFailureTime`, `MetricsRegistry`, quantile intervals of one hour, one day, and ten days, `DIR_METRICS`, `getMetric`, `addWriteFileLatency`, `addReadFileLatency`, `sourceName`, and `diskCheckFailed`.

## Control Flow
`getMetric` synchronizes on the class, checks the directory-name cache, constructs metrics if absent, registers them with `DefaultMetricsSystem.instance()` using `sourceName(dirName)`, stores the result, and returns it. Latency methods add values to every configured quantile. `diskCheckFailed` increments the failure counter and sets last failure time to `System.nanoTime()`.

## State And Persistence
State is in-memory metrics objects cached by raw directory string. Metrics are exported through Hadoop metrics2 but not persisted by this class.

## Dependencies And Integration Points
It depends on metrics2 annotations and mutable metric types, `DefaultMetricsSystem`, `Interns.info`, and `ReadWriteDiskValidator`.

## Risks
Cache keys are unnormalized directory strings, so aliases can register duplicate sources. Source names include directory text and may contain characters problematic for sinks. `lastFailureTime` uses monotonic nano time, not wall-clock time. Cached metrics are never removed.

## Test Signals
Tests should assert per-directory caching, registration source names, quantile array setup, latency propagation to all quantiles, failure counter/gauge updates, and behavior when metrics system is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReadWriteDiskValidatorMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReflectionUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReflectionUtils.java

## Purpose
`ReflectionUtils` provides shared reflection, configuration injection, thread dump logging, object creation, serialization-copy, and inherited-member discovery utilities.

## Important APIs, Types, And Functions
Key APIs are `setConf`, `newInstance`, `setContentionTracing`, `printThreadInfo`, `logThreadInfo`, `getClass`, `copy`, `cloneWritableInto`, `getDeclaredFieldsIncludingInherited`, and `getDeclaredMethodsIncludingInherited`. Static state includes constructor cache, serialization factory, thread MXBean, previous log time, and thread-local clone buffers.

## Control Flow
`newInstance` validates constructor argument arity, fetches or caches an accessible constructor by class, instantiates, then injects configuration. `setConf` calls `Configurable.setConf` and reflectively supports legacy `JobConfigurable.configure(JobConf)`. Thread dump methods collect MXBean thread info and throttle logging by `previousLogTime`. Copy methods serialize to a thread-local output buffer, reset an input buffer over the same bytes, then deserialize into the destination.

## State And Persistence
Constructor and serialization-factory caches persist for the process and can pin classes. Thread-local buffers persist per thread. No disk persistence exists.

## Dependencies And Integration Points
It depends on Hadoop `Configuration`, `Configurable`, Writable/serialization APIs, MXBeans, reflection, and SLF4J/commons logging. It bridges common code and optional mapred classes.

## Risks
Constructor cache keys ignore constructor argument types, so using multiple constructors for one class can be unsafe. Static serialization factory may not reflect later configurations. Caches can retain classes. Reflection exceptions are wrapped as runtime failures.

## Test Signals
Tests should cover constructor caching, non-default constructor behavior, configuration injection, legacy mapred configuration, thread dump throttling, serialization copy correctness, cache clearing, and inherited member ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ReflectionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RunJar.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RunJar.java

## Purpose
`RunJar` unpacks and runs Hadoop job jars. It locates the target main class from a manifest or command line, prepares an isolated work directory, builds the classloader, invokes `main`, and cleans temporary files at shutdown.

## Important APIs, Types, And Functions
Important APIs are `main`, `run`, `unJar` overloads, deprecated `unJarAndSave`, `createWorkDirectory`, `directoryPermissions`, `userOnly`, and `createClassLoader`. Environment switches include `HADOOP_USE_CLIENT_CLASSLOADER`, `HADOOP_CLASSPATH`, `HADOOP_CLIENT_CLASSLOADER_SYSTEM_CLASSES`, and `HADOOP_CLIENT_SKIP_UNJAR`.

## Control Flow
`run` validates the jar file, reads `Main-Class` unless supplied, creates a secure temp directory, registers a shutdown hook to delete it, optionally unpacks the jar, creates either an `ApplicationClassLoader` or `URLClassLoader`, sets the context loader, loads the main class, shifts user args, and invokes `main`, unwrapping target exceptions. `unJar` checks canonical paths to prevent expanding entries outside the target directory.

## State And Persistence
Temporary unpacked files persist only until the shutdown hook deletes the work directory. Static configuration is read from environment variables at call time via methods.

## Dependencies And Integration Points
It integrates with `ShutdownHookManager`, `FileUtil`, Hadoop classloader isolation, commons `TeeInputStream`, jar APIs, and filesystem permissions.

## Risks
Jar execution is security-sensitive. Zip-slip protection and user-only temp permissions are essential. `System.exit` is used for usage/setup failures. Skipping unjar changes classpath assumptions around `classes/` and `lib/`. Shutdown cleanup may not run on hard kill.

## Test Signals
Tests should cover manifest and explicit main selection, argument shifting, zip-slip rejection, selective unpack regex, temp directory permissions on POSIX/ACL filesystems, client classloader env behavior, skip-unjar mode, and cleanup hook registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/RunJar.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SemaphoredDelegatingExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SemaphoredDelegatingExecutor.java

## Purpose
`SemaphoredDelegatingExecutor` wraps an `ExecutorService` so task submission blocks when a configured number of queued/running tasks is reached. It isolates semaphore backpressure from concrete thread-pool implementation.

## Important APIs, Types, And Functions
The class extends Guava `ForwardingExecutorService`. Important APIs are constructors, `submit` overloads, `execute`, `getAvailablePermits`, `getWaitingCount`, `getPermitCount`, and wrappers `RunnableWithPermitRelease` and `CallableWithPermitRelease`.

## Control Flow
Each `submit` acquires a semaphore permit while tracking acquisition duration, then delegates a wrapper task that releases the permit in `finally`. Interrupted acquisition returns an immediate failed future for `submit`. `execute` also acquires, but if interrupted it only restores interrupt state and still delegates a wrapped command. Bulk invoke methods are explicitly unimplemented.

## State And Persistence
State is an in-memory semaphore, delegate executor, permit count, and duration tracker factory. No persistence exists.

## Dependencies And Integration Points
It depends on shaded Guava forwarding/futures, Java concurrency, Hadoop IO statistics duration tracking, and store statistic name `ACTION_EXECUTOR_ACQUIRED`.

## Risks
The `execute` interruption path can submit without a permit and later release one, increasing permit count incorrectly. Delegate rejection after acquiring a permit can leak a permit because wrapping happens before delegate execution but no rejection cleanup exists. `invokeAll`/`invokeAny` throw runtime exceptions.

## Test Signals
Tests should cover blocking at permit limits, permit release after success/failure, interrupted submit behavior, interrupted execute permit accounting, delegate rejection, fairness mode, duration metric emission, and unsupported bulk operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SemaphoredDelegatingExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SequentialNumber.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SequentialNumber.java

## Purpose
`SequentialNumber` is a thread-safe abstract base for monotonically advanced ID generators backed by an `AtomicLong`.

## Important APIs, Types, And Functions
It implements `IdGenerator` and exposes `getCurrentValue`, `setCurrentValue`, `setIfGreater`, `nextValue`, `skipTo`, `equals`, and `hashCode`.

## Control Flow
`nextValue` atomically increments and returns the new value. `setIfGreater` CAS-loops until it either observes an existing value greater than or equal to the input or successfully swaps in the larger value. `skipTo` CAS-loops to a requested value but throws if it would move backwards. `setCurrentValue` is an unconditional store.

## State And Persistence
State is the atomic current value. There is no persistence; subclasses or callers must persist IDs if needed.

## Dependencies And Integration Points
It depends on `AtomicLong`, Hadoop annotations, and the `IdGenerator` contract. It is used by components needing simple sequential identifiers.

## Risks
`setCurrentValue` can move backwards and bypass monotonic guarantees. `equals` compares the `AtomicLong` object, not its contained value, so two generators with the same numeric value are not equal unless sharing the same atomic instance, which they never do in normal construction. Overflow is not checked.

## Test Signals
Tests should cover concurrent `nextValue`, `setIfGreater` races, `skipTo` backward rejection, unconditional reset behavior, overflow expectations, and equality/hash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SequentialNumber.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServicePlugin.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServicePlugin.java

## Purpose
`ServicePlugin` defines a private lifecycle extension point for Hadoop services such as NameNode and DataNode to load plugins that expose additional functionality, often through custom RPC protocols.

## Important APIs, Types, And Functions
The interface extends `Closeable` and declares `start(Object service)` and `stop()`. `close()` is inherited and left to implementations.

## Control Flow
The service instantiates plugins, starts them after the service itself starts, and stops them before the service shuts down. This file only defines the callback order contract; it does not enforce it.

## State And Persistence
The interface owns no state. Plugin implementations may manage resources, network servers, or persisted state.

## Dependencies And Integration Points
It depends on `Closeable` and Hadoop annotations. It integrates with service plugin loading mechanisms in HDFS and other daemon code.

## Risks
The service parameter is typed as `Object`, so implementations must cast carefully. The relationship between `stop` and `close` is not defined here. Exceptions and timeout handling are owned by plugin managers, not the interface.

## Test Signals
Tests should focus on service-side plugin managers: construction, lifecycle order, service object type, exception handling, stop/close invocation, and cleanup before daemon shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServicePlugin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServletUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServletUtil.java

## Purpose
`ServletUtil` contains small servlet/JSP helpers for Hadoop web UIs: basic HTML framing, request parameter normalization/parsing, footer generation, and raw servlet path extraction.

## Important APIs, Types, And Functions
Important APIs are `initHTML`, `getParameter`, `parseLongParam`, `htmlFooter`, `getRawPath`, and constant `HTML_TAIL`.

## Control Flow
`initHTML` sets `text/html`, obtains a writer, and writes a simple page header and stylesheet link. `getParameter` trims whitespace and maps empty strings to null. `parseLongParam` requires a parameter and parses it with `Long.parseLong`. `getRawPath` checks that `requestURI` starts with `servletName + "/"` and returns the substring after the servlet name without URL decoding.

## State And Persistence
There is no mutable state. `HTML_TAIL` includes the year captured at class initialization.

## Dependencies And Integration Points
It depends on Java servlet APIs, `HttpServletRequest`, `Calendar`, Hadoop annotations, and `Preconditions`. It is used by Hadoop web UI servlets and JSPs.

## Risks
`initHTML` writes unescaped titles directly into HTML, so callers must provide safe text. `parseLongParam` lets `NumberFormatException` propagate despite declaring `IOException`. `HTML_TAIL` year can become stale in long-running daemons across New Year.

## Test Signals
Tests should cover content type/header output, parameter trimming, missing and invalid long parsing, raw path extraction, precondition failures, and HTML escaping expectations at callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServletUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Sets.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Sets.java

## Purpose
`Sets` is Hadoop's private replacement for the Guava `Sets` helpers commonly needed in core code: constructing mutable sets, set algebra, concurrent sets, and expected-size hash capacity calculation.

## Important APIs, Types, And Functions
Key APIs are `newHashSet`, varargs/iterable/iterator overloads, `newTreeSet`, `newHashSetWithExpectedSize`, `intersection`, `union`, `difference`, `differenceInTreeSets`, `symmetricDifference`, and `newConcurrentHashSet`. Internal helpers include `capacity`, `addAll`, and `cast`.

## Control Flow
Factory methods create mutable `HashSet` or `TreeSet` instances, optionally adding all inputs. Set algebra methods null-check inputs, copy into new sets, perform retain/add/remove operations, and return unmodifiable results. `capacity` mirrors Guava/JDK sizing logic and rejects negative expected sizes.

## State And Persistence
The class is stateless. Returned collections are in-memory only; algebra results are unmodifiable snapshots, not live views.

## Dependencies And Integration Points
It depends on Java collections and Hadoop annotations. It allows common code to avoid direct Guava `Sets` dependency.

## Risks
Javadocs contain a few inaccurate return descriptions inherited from copied text. Raw comparable bounds on `newTreeSet` are loose. Hash-based algebra has undefined ordering and depends on equality semantics; `differenceInTreeSets` changes ordering assumptions.

## Test Signals
Tests should verify all constructors, null rejection, negative expected size, expected capacity edge cases, unmodifiable algebra results, deterministic tree difference ordering, concurrent set null rejection, and duplicate handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Sets.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Shell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Shell.java

## Purpose
`Shell` is Hadoop's central process-execution and platform-command utility. It builds OS-specific commands, validates Hadoop home/winutils, executes commands with timeout and stream handling, and tracks child shells for global cleanup.

## Important APIs, Types, And Functions
Important static APIs include OS detection flags, command builders for groups, permissions, ownership, symlinks, process signals, scripts, bash support, Hadoop home/bin/winutils resolution, `execCommand`, `destroyAllShellProcesses`, and `getMemlockLimit`. Instance APIs include `run`, abstract `getExecString`/`parseExecResult`, environment/working-directory setters, timeout state, `ShellCommandExecutor`, `ExitCodeException`, and `CommandExecutor`.

## Control Flow
Static initialization detects OS, validates Hadoop home, initializes winutils metadata, and probes `setsid`. `run` gates execution by interval and delegates to `runCommand`. `runCommand` builds a `ProcessBuilder`, optionally clears/injects env, starts the process under a Windows launch lock when needed, tracks it in a weak global map, schedules timeout destruction, drains stderr on a subject-inheriting thread, lets subclasses parse stdout, waits for exit, throws `ExitCodeException` for nonzero status, closes streams, destroys the process, and updates last-run time.

## State And Persistence
State includes cached static environment detection, child-shell weak map, per-instance process, exit code, timeout flags, environment, working directory, and interval timing. No persistence exists, but OS child processes and inherited resources are external state.

## Dependencies And Integration Points
It integrates with Hadoop `Time`, `StringUtils`, `SubjectInheritingThread`, platform binaries, Hadoop home layout, Windows `winutils.exe`, and many Hadoop filesystem/security call sites.

## Risks
Class initialization can perform filesystem and command probes. Command construction must quote safely, especially users and PIDs. Timeout uses `Process.destroy`, not forceful destroy. Output is buffered in memory by `ShellCommandExecutor`, so it suits small output only. `joinThread` can preserve interruption awkwardly while looping. Global process destruction is coarse.

## Test Signals
Tests should cover OS-specific command arrays, bash quoting, command length checks, Hadoop home and winutils validation errors, env inheritance, timeout behavior, stderr capture, nonzero exit exceptions, interval gating, child-shell cleanup, and process-group signal behavior with/without `setsid`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Shell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ShutdownHookManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ShutdownHookManager.java

## Purpose
`ShutdownHookManager` provides deterministic Hadoop shutdown hook ordering by registering one JVM hook and running registered hooks sequentially from highest priority to lowest, with per-hook timeouts.

## Important APIs, Types, And Functions
Important members are singleton `MGR`, static single-thread `EXECUTOR`, `addShutdownHook` overloads, `removeShutdownHook`, `hasShutdownHook`, `isShutdownInProgress`, `clearShutdownHooks`, `executeShutdown`, `getShutdownHooksInOrder`, `getShutdownTimeout`, and nested `HookEntry`.

## Control Flow
Static initialization registers a `SubjectInheritingThread` JVM shutdown hook. During shutdown it atomically marks shutdown in progress, calls `executeShutdown`, logs timing, then shuts down the executor. `executeShutdown` sorts hooks by descending priority, submits each to the single-thread executor, waits for its configured timeout, cancels on timeout, and logs failures. Add/remove operations reject changes once shutdown begins.

## State And Persistence
Registered hooks live in a synchronized in-memory set. Shutdown progress is an `AtomicBoolean`. No persistence exists.

## Dependencies And Integration Points
It depends on Hadoop configuration keys for default shutdown timeout, `HadoopExecutors`, Guava `ThreadFactoryBuilder`, `SubjectInheritingThread`, and service/daemon cleanup code such as `RunJar` temp deletion.

## Risks
Hooks with equal priority run in nondeterministic order. `HookEntry.equals` uses runnable identity, so wrapper objects matter. Timeout cancellation requires hooks to honor interruption. Static executor lifecycle means test isolation needs care.

## Test Signals
Tests should cover priority ordering, timeout minimum enforcement, timeout cancellation count, exception logging without aborting later hooks, add/remove rejection during shutdown, duplicate hook identity, and executor termination behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ShutdownHookManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ShutdownThreadsHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ShutdownThreadsHelper.java

## Purpose
`ShutdownThreadsHelper` provides small static helpers to interrupt/join individual threads and gracefully-then-forcefully shut down executor services.

## Important APIs, Types, And Functions
Important APIs are `shutdownThread(Thread)`, `shutdownThread(Thread,long)`, `shutdownExecutorService(ExecutorService)`, and `shutdownExecutorService(ExecutorService,long)`. The default wait is `SHUTDOWN_WAIT_MS = 3000`.

## Control Flow
Thread shutdown returns true for null, otherwise interrupts the thread and joins for the requested timeout. It returns false only if the current thread is interrupted while waiting. Executor shutdown returns true for null, calls `shutdown`, waits, calls `shutdownNow` if needed, and waits again before returning whether termination completed.

## State And Persistence
The class has no mutable state. It changes external thread/executor lifecycle state.

## Dependencies And Integration Points
It depends on Java concurrency and SLF4J. It is useful in daemon and test cleanup paths.

## Risks
`shutdownThread` returns true even if the target thread remains alive after the join timeout. It does not restore the interrupt status of the caller when interrupted. Executor shutdown propagates `InterruptedException` for callers to handle.

## Test Signals
Tests should cover null inputs, cooperative and uncooperative threads, interrupted waiter behavior, executor graceful termination, forced shutdown path, second await timeout, and caller interrupt preservation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ShutdownThreadsHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalLogger.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalLogger.java

## Purpose
`SignalLogger` installs handlers for common UNIX termination signals so Hadoop logs which signal caused process exit before delegating to the previous handler.

## Important APIs, Types, And Functions
The enum singleton `INSTANCE` exposes `register(Logger)`. Internal `Handler` implements `SignalUtil.Handler`, stores the logger and previous handler, and handles `TERM`, `HUP`, and `INT`.

## Control Flow
`register` rejects repeated registration, marks registered, iterates the signal names, installs a new `Handler` through `SignalUtil.handle`, records successfully installed names, logs debug on failures, and logs the final registration list. On signal receipt, the handler logs an error with signal number/name and invokes the previous handler.

## State And Persistence
The singleton keeps a boolean `registered` flag. Installed signal handlers mutate JVM process signal state. There is no persistence.

## Dependencies And Integration Points
It depends on SLF4J, Hadoop annotations, and `SignalUtil`'s dynamic bridge to `sun.misc.Signal`.

## Risks
The registered flag is not synchronized, so concurrent registration can race. If the previous handler is null or problematic, delegating may fail. Signal APIs are non-standard and may be unavailable under some JVMs/modules/platforms.

## Test Signals
Tests should cover single-registration enforcement, successful and failed signal installations, log content on handler invocation, delegation to previous handler, and behavior when `sun.misc.Signal` bindings are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalUtil.java

## Purpose
`SignalUtil` wraps non-public JDK signal APIs through Hadoop dynamic binding utilities so the rest of Hadoop can handle and raise signals without direct compile-time dependency on `sun.misc.Signal`.

## Important APIs, Types, And Functions
Important pieces are dynamic bindings for `sun.misc.Signal`, `sun.misc.SignalHandler`, constructor, static `handle`, static `raise`, handler `handle`, nested `Signal`, nested `Handler`, and `JdkSignalHandlerImpl`.

## Control Flow
Static initializers load classes and bind constructors/methods. `Signal(String)` creates a JDK signal delegate and binds get-number/name calls. `Signal(Object)` validates delegate type. `JdkSignalHandlerImpl(Handler)` creates a dynamic proxy implementing JDK `SignalHandler`; proxy `handle` calls the Hadoop handler with a wrapped signal and delegates other methods reflectively. `handle` installs a proxy and returns the previous handler wrapped. `raise` invokes the JDK raise method.

## State And Persistence
State is dynamic method metadata and wrapper delegates. Installing handlers mutates process-level signal handler state.

## Dependencies And Integration Points
It depends on Hadoop `BindingUtils`, `DynConstructors`, `DynMethods`, `Preconditions`, Java reflection/proxy APIs, and the JDK's internal signal classes when present. `SignalLogger` is its main local consumer.

## Risks
Non-public JDK APIs can be inaccessible under module restrictions or alternate JVMs. Static dynamic binding failures may surface at class initialization or first use. Proxy fallback for non-handle methods assumes the user handler has matching methods.

## Test Signals
Tests should cover signal name construction, delegate wrapping validation, equality/hash/toString, handler install returning previous handler, proxy invocation, raise behavior, and unavailable-class failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StopWatch.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StopWatch.java

## Purpose
`StopWatch` is a simple closeable monotonic elapsed-time accumulator measured in nanoseconds, with an injectable `Timer` for tests.

## Important APIs, Types, And Functions
Important APIs are constructors, `isRunning`, `start`, `stop`, `reset`, `now(TimeUnit)`, `now()`, `toString`, and `close`. State fields are `timer`, `isStarted`, `startNanos`, and `currentElapsedNanos`.

## Control Flow
`start` rejects already-running watches, records current monotonic time, and marks running. `stop` rejects stopped watches, adds elapsed nanos since `startNanos`, and marks stopped. `reset` clears elapsed time and stops. `now` returns accumulated elapsed plus current running delta when active, or accumulated elapsed when stopped. `close` stops only if running.

## State And Persistence
All state is per-instance memory. There is no synchronization and no persistence.

## Dependencies And Integration Points
It depends on Hadoop `Timer`, Java `TimeUnit`, and `Closeable`. It is useful with try-with-resources for scoped timing.

## Risks
The class is not thread-safe. Time conversion truncates according to `TimeUnit.convert`. Reusing a running watch across `close` silently stops it, while explicit double stop/start misuse throws.

## Test Signals
Tests should use a fake `Timer` to verify start/stop accumulation, reset, running `now`, conversion truncation, `toString`, close behavior, and illegal state exceptions for double start or stop-before-start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StopWatch.java -->
