# subset-b-007373 Research

This grouped report covers the Hadoop utility sources assigned to `subset-b-007373`. Each source file has a marker-delimited section so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StringInterner.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StringInterner.java

Purpose: `StringInterner` centralizes string interning choices for Hadoop callers. It exposes a strong Guava interner for values that should be retained and a JVM-backed `String.intern()` path for weak-style canonicalization that does not keep a separate Hadoop strong map.

Important APIs/types/functions: `strongIntern(String)` returns `null` for `null` and otherwise stores the canonical value in `STRONG_INTERNER`. `weakIntern(String)` returns `null` for `null` and otherwise calls `sample.intern()`. `internStringsInArray(String[])` mutates the input array in place by weak-interning every element and returns the same array.

Control flow: all public methods are small null-guarded wrappers. The array method loops linearly over indices and delegates per element to `weakIntern`, so `null` array elements survive as `null`.

State and persistence behavior: the only persistent process state is static `STRONG_INTERNER`, which retains every strongly interned string until class unloading. Weak interning delegates lifetime and canonical storage to the JVM string pool.

Dependencies and integration points: depends on Hadoop third-party Guava `Interner`/`Interners` and Hadoop audience/stability annotations. It is useful for configuration keys, paths, and repeated identifiers across Hadoop components.

Risks: `strongIntern` can create unbounded process memory retention if fed high-cardinality or user-controlled values. `internStringsInArray` mutates caller-owned arrays and does not check the array itself for `null`. `weakIntern` uses JVM global string-pool semantics, so behavior depends on the runtime rather than Hadoop-owned pruning.

Test signals: useful tests should assert null preservation, array mutation, object identity for duplicate values, and memory-sensitive callers should prefer weak interning for unbounded domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StringInterner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StringUtils.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StringUtils.java

Purpose: `StringUtils` is Hadoop Common's broad string helper collection. It covers exception rendering, hostname simplification, locale-stable formatting, hex/URI/path conversion, time formatting, comma/newline parsing, escaping, startup/shutdown log messages, binary-size parsing and formatting, token replacement, stack-trace formatting, command-line list mutation, case handling, alpha checks, word wrapping, and simple non-empty checks.

Important APIs/types/functions: constants include `SHUTDOWN_HOOK_PRIORITY`, platform-specific environment variable patterns, `ENV_VAR_PATTERN`, `STRING_COLLECTION_SPLIT_EQUALS_INVALID_ARG`, `emptyStringArray`, `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`. Formatting helpers include `stringifyException`, `simpleHostname`, `format`, `formatPercent`, `byteToHexString`, `hexStringToByte`, `formatTimeDiff`, `formatTime`, `formatTimeSortable`, `getFormattedTimeWithDiff`, `byteDesc`, and deprecated `humanReadableInt`/`limitDecimalTo2`. Parsing helpers include `getStrings`, `getStringCollection`, `getTrimmedStringCollection`, `getTrimmedStringCollectionSplitByEquals`, `getTrimmedStrings`, `getTrimmedStringsSplitByEquals`, `split`, `findNext`, `escapeString`, and `unEscapeString`. `TraditionalBinaryPrefix` maps K/M/G/T/P/E binary prefixes and provides `string2long` and `long2String`. Operational helpers include `startupShutdownMessage`, `createStartupShutdownMessage`, `replaceTokens`, `popOptionWithArgument`, `popOption`, `popFirstNonOption`, `toLowerCase`, `toUpperCase`, `equalsIgnoreCase`, `isAlpha`, `wrap`, and `hasLength`.

Control flow: most methods are stateless transformations. Split/escape handling scans characters, treats a separator as literal when preceded by an odd number of escape characters, removes trailing empty fields, and throws on illegal unescaped separators or dangling escapes. Collection parsing uses `StringTokenizer` for delimiter-based tokenization or regex split for comma/newline and equals-separated values. Startup logging records host/version/build details, registers UNIX signal logging when possible, and installs a shutdown hook that logs and shuts down log4j. Binary prefix parsing trims, detects a trailing non-digit as a prefix, checks multiplication overflow, and formats using exact division or rounded decimal output.

State and persistence behavior: the class is static and stateless except for registration side effects in `startupShutdownMessage`, which adds a shutdown hook and may register signal handlers. `TraditionalBinaryPrefix` is enum state only. Methods that accept `List<String>` for CLI parsing mutate that list by removing consumed tokens.

Dependencies and integration points: depends on Apache Commons Lang, `FastDateFormat`, Hadoop `Path`, `NetUtils`, `SignalLogger`, `ShutdownHookManager`, `VersionInfo`, Hadoop `Preconditions`, log4j shutdown, and shaded Guava `InetAddresses`. Many Hadoop daemons and CLI tools use this class for generic option processing, logs, and configuration parsing.

Risks: `uriToString(URI[])` assumes a non-empty array and will fail on empty arrays. `byteToHexString(byte[], start, end)` relies on caller-valid bounds and uses `String.format` per byte, which is not optimized for hot paths. `getTrimmedStringsSplitByEquals` uses `String.split` without a negative limit, so trailing empty values can disappear before validation; callers rely on `getTrimmedStringCollectionSplitByEquals` to reject invalid pairs. `removeSpecificPerms` is not here, but similar bit operations elsewhere require precise masks. Startup logging can expose classpath/build details. `wrap` handles only space character `32`, not all Unicode whitespace. Locale-stable case conversion intentionally uses English and can differ from user locale expectations.

Test signals: existing tests should cover escaped comma splitting, invalid escapes, key-value parsing rejection, binary-prefix overflow and rounding, CLI option removal before/after `--`, startup message content stability, case conversion, and wrapping edge cases. Integration tests around daemon startup should observe shutdown hook/logging side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/StringUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfo.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfo.java

Purpose: `SysInfo` defines the public evolving abstraction for querying host resource information across operating systems.

Important APIs/types/functions: `newInstance()` chooses `SysInfoLinux` when `Shell.LINUX` is true, `SysInfoWindows` when `Shell.WINDOWS` is true, and throws `UnsupportedOperationException` otherwise. Abstract methods expose total/available virtual and physical memory, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU percentage, vcores used, aggregate network bytes, and aggregate storage bytes.

Control flow: the class performs no measurement itself. It is a dispatch and contract layer; concrete implementations decide caching and refresh behavior.

State and persistence behavior: `SysInfo` has no fields. Concrete instances may cache OS readings.

Dependencies and integration points: depends on `Shell` platform detection and the Linux/Windows implementations. Yarn resource monitors and daemon metrics can use this interface without platform-specific branching.

Risks: unsupported platforms fail at instance creation. The API returns primitive values with implementation-specific sentinel values such as `-1` for unavailable data, so callers must not assume every metric is populated.

Test signals: tests should verify platform dispatch under mocked shell flags and caller handling of unavailable metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoLinux.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoLinux.java

Purpose: `SysInfoLinux` implements `SysInfo` by parsing Linux procfs and sysfs files: `/proc/meminfo`, `/proc/cpuinfo`, `/proc/stat`, `/proc/net/dev`, `/proc/diskstats`, and `/sys/block/<disk>/queue/hw_sector_size`.

Important APIs/types/functions: constructors allow real paths or test-supplied file paths plus jiffy length. Public metrics implement all `SysInfo` getters. Internal readers include `readProcMemInfoFile`, `readProcCpuInfoFile`, `readProcStatFile`, `readProcNetInfoFile`, `readProcDisksInfoFile`, `readDiskBlockInformation`, `safeParseLong`, `getCurrentTime`, `setReadCpuInfoFile`, and `getJiffyLengthInMillis`. Static `PAGE_SIZE` and `JIFFY_LENGTH_IN_MILLIS` come from `getconf`.

Control flow: memory and CPU topology files are cached after first read unless memory availability explicitly requests a reread. `/proc/stat`, network, and disk counters are reread on each relevant getter. CPU usage is computed by `CpuTimeTracker` from cumulative user/nice/system jiffies and wall time, then divided by logical processor count for percentage or by 100 for vcores used. Disk stats skip loop and ram devices, cache per-disk sector sizes, and multiply sector counts by the sector size.

State and persistence behavior: instance fields cache procfs paths, jiffy length, parsed memory totals/free values, CPU counts/frequency, network and disk counters, read-once flags, `CpuTimeTracker`, and a synchronized `perDiskSectorSize` map. There is no persistence beyond process memory.

Dependencies and integration points: depends on Java NIO file reads, regex patterns, `ShellCommandExecutor` for `getconf`, `CpuTimeTracker`, and SLF4J. It integrates with system metrics and resource monitoring in Linux deployments.

Risks: parser regexes reflect specific Linux procfs formats and may miss device names or newer fields. `safeParseLong` converts invalid/overflowing memory values to zero, which avoids crashes but may under-report. CPU frequency stores the last `cpu MHz` line seen. `getCpuUsagePercentage` divides by `getNumProcessors`; malformed CPU info producing zero processors could be problematic. Disk device filtering and the diskstats regex exclude partitions and may not cover NVMe/mapper naming consistently. File closing is manual rather than try-with-resources.

Test signals: tests should supply fake procfs files for memory variants including `Inactive(file)`, hardware-corrupted and huge pages, malformed swap values, CPU topology, jiffy-based CPU deltas, network loopback exclusion, disk sector fallback, and missing file behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoLinux.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoWindows.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoWindows.java

Purpose: `SysInfoWindows` implements `SysInfo` by invoking `winutils systeminfo` and parsing a comma-separated metrics line.

Important APIs/types/functions: public getters cover all `SysInfo` metrics. Internal methods include `now`, `reset`, `getSystemInfoInfoFromShell`, and synchronized `refreshIfNeeded`. `REFRESH_INTERVAL_MS` throttles shell refreshes to once per second.

Control flow: every getter calls `refreshIfNeeded`. Refresh compares monotonic time to `lastRefreshTime`, snapshots the previous cumulative CPU time, resets all metrics to `-1`, executes `winutils systeminfo`, parses the first CRLF-terminated line into 11 fields, and computes aggregate CPU usage from cumulative CPU delta over refresh interval. CPU percentage divides aggregate usage by processor count; vcores used divides by 100.

State and persistence behavior: instance fields cache the latest shell-reported memory, CPU, storage, and network counters plus the last refresh timestamp. Failures leave metrics at `-1` until the next successful refresh.

Dependencies and integration points: depends on `Shell.getWinUtilsFile`, `ShellCommandExecutor`, `Time.monotonicNow`, and `StringUtils.stringifyException`. It serves Windows deployments through the shared `SysInfo` contract.

Risks: parsing depends on exact comma count and CRLF output from `winutils systeminfo`. The first refresh cannot compute CPU usage because there is no previous cumulative value. If `numProcessors` remains `-1` or zero due to partial parsing, percentage math can be misleading. Shell execution errors are logged and converted into unavailable values.

Test signals: tests should mock command output with correct/incorrect field counts, verify refresh throttling, first-sample CPU unavailability, second-sample CPU computation, and error handling when `winutils` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SysInfoWindows.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ThreadUtil.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ThreadUtil.java

Purpose: `ThreadUtil` provides thread sleep/join helpers and classpath resource loading with explicit error messages.

Important APIs/types/functions: `sleepAtLeastIgnoreInterrupts(long)` sleeps until wall-clock elapsed time reaches the requested duration while logging interruptions. `joinUninterruptibly(Thread)` repeatedly joins until the target terminates and restores interrupt status before returning. `getResourceAsStream(String)` uses the current thread context classloader; `getResourceAsStream(ClassLoader, String)` loads from an explicit classloader and throws `IOException` for null loaders or missing resources.

Control flow: sleep recomputes remaining time after every interrupt. Join loops until `Thread.join()` succeeds, tracks whether any interrupt occurred, and re-interrupts in `finally`. Resource loading validates the loader then checks for a null stream.

State and persistence behavior: stateless beyond logging. Methods may alter the current thread interrupt status on return from `joinUninterruptibly`.

Dependencies and integration points: depends on `Time.now` and SLF4J. `VersionInfo` uses the resource helpers; many daemon/test threads can use the join helper.

Risks: sleep uses wall-clock `Time.now`, so clock changes can distort elapsed sleep; monotonic time would be safer. Ignoring interrupts can delay shutdown. Resource streams are returned open and must be closed by callers.

Test signals: tests should cover interrupt restoration for joins, missing resource exceptions, null classloader exceptions, and sleep behavior under repeated interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ThreadUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Time.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Time.java

Purpose: `Time` centralizes wall-clock and monotonic time utilities plus a Hadoop-standard timestamp formatter.

Important APIs/types/functions: `now()` returns `System.currentTimeMillis`. `monotonicNow()` returns `System.nanoTime()` converted to milliseconds. `monotonicNowNanos()` returns raw `System.nanoTime`. `formatTime(long)` formats milliseconds with a thread-local `SimpleDateFormat` pattern `yyyy-MM-dd HH:mm:ss,SSSZ`. `getUtcTime()` returns the current UTC calendar time in milliseconds.

Control flow: calls are direct wrappers, except `DATE_FORMAT` lazily creates a formatter per thread.

State and persistence behavior: static thread-local formatters persist per thread until thread termination. No external persistence.

Dependencies and integration points: used throughout Hadoop for interval measurement and human-readable logs. `Timer` delegates to it and system monitoring code uses monotonic time for refresh intervals.

Risks: `now()` is explicitly unsuitable for durations because wall time can move. `formatTime` uses the formatter default timezone rather than forcing UTC; `getUtcTime` only affects returned current time. `monotonicNow` may be negative and callers must handle arbitrary origin values.

Test signals: tests should verify monotonic wrapper use for intervals, formatting pattern stability, and timezone expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Time.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Timer.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Timer.java

Purpose: `Timer` is an overridable object wrapper around `Time`, intended for dependency injection in code that needs test-controlled clocks.

Important APIs/types/functions: instance methods `now`, `monotonicNow`, and `monotonicNowNanos` delegate to `Time`.

Control flow: no branching; subclasses can override methods to inject fake time.

State and persistence behavior: no fields and no persistence.

Dependencies and integration points: integrates with code that would otherwise call static time methods directly, improving testability for timeout and retry logic.

Risks: callers must choose wall-clock versus monotonic APIs correctly; the wrapper does not enforce duration-safe usage.

Test signals: unit tests can subclass `Timer` and verify consumers honor injected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Timer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Tool.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Tool.java

Purpose: `Tool` is Hadoop's stable CLI application contract for programs that accept generic Hadoop command-line options and carry a `Configuration`.

Important APIs/types/functions: it extends `Configurable` and declares `int run(String[] args) throws Exception`.

Control flow: implementers receive application-specific arguments after `ToolRunner` removes generic Hadoop options.

State and persistence behavior: state is supplied by the `Configurable` configuration implementation in concrete tools; `Tool` itself has no fields.

Dependencies and integration points: pairs with `GenericOptionsParser`, `ToolRunner`, `Configured`, MapReduce jobs, shells such as `KeyShell`, and test utilities invoking command-like classes.

Risks: implementers must treat `args` as post-generic-option arguments, not raw process arguments. Exceptions are allowed to propagate, so entrypoints need exit-code handling.

Test signals: tests should instantiate tools through `ToolRunner` to verify generic options update configuration and only remaining args reach `run`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Tool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ToolRunner.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ToolRunner.java

Purpose: `ToolRunner` executes `Tool` implementations after generic Hadoop option parsing, while setting common CLI audit/caller context.

Important APIs/types/functions: `run(Configuration, Tool, String[])` is the main entrypoint. `run(Tool, String[])` delegates using the tool's existing configuration. `printGenericCommandUsage(PrintStream)` delegates to `GenericOptionsParser`. `confirmPrompt(String)` repeatedly reads from `System.in` until it receives yes/no input.

Control flow: `run` installs a default `CallerContext` of `CLI` if absent, notes the tool in `CommonAuditContext`, creates a new `Configuration` when needed, parses generic options with `GenericOptionsParser`, sets the resulting configuration on the tool, then invokes `tool.run` with remaining arguments. `confirmPrompt` writes to stderr, reads characters until newline/EOF, accepts y/yes or n/no case-insensitively, and loops on invalid input.

State and persistence behavior: modifies static/thread-local caller context and audit context, mutates the tool's configuration reference, and consumes process stdin for prompts.

Dependencies and integration points: depends on `Configuration`, `GenericOptionsParser`, `CallerContext`, and `CommonAuditContext`. It is the standard launcher path for Hadoop CLI tools.

Risks: `tool` is not null-checked. `confirmPrompt` can block forever on non-interactive input that is not EOF and can repeatedly emit invalid input messages. Caller context is only set when absent; nested invocations inherit existing context.

Test signals: tests should verify generic options removal, configuration mutation, caller/audit context behavior, and prompt parsing for yes/no/invalid/EOF paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ToolRunner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/UTF8ByteArrayUtils.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/UTF8ByteArrayUtils.java

Purpose: `UTF8ByteArrayUtils` provides byte-level search helpers for UTF-8 encoded byte arrays, primarily for separator scanning without decoding to `String`.

Important APIs/types/functions: `findByte(byte[], int, int, byte)` returns the first matching byte in `[start,end)`. `findBytes(byte[], int, int, byte[])` returns the first occurrence of a byte sequence. `findNthByte(byte[], int, int, byte, int)` finds the nth occurrence within a bounded region. `findNthByte(byte[], byte, int)` scans the whole array.

Control flow: all methods use straightforward nested loops and return `-1` on no match. The nth-byte method repeatedly calls `findByte` starting after the previous match.

State and persistence behavior: stateless and allocation-free except call-stack locals.

Dependencies and integration points: depends only on Hadoop annotations. It is useful in text input parsing where delimiters are ASCII bytes embedded in UTF-8 data.

Risks: no input validation for null arrays, negative offsets, end beyond length, or empty pattern semantics. `findBytes` with an empty pattern returns `start` because the inner loop succeeds immediately. The methods do byte matching only and do not validate UTF-8 boundaries.

Test signals: tests should cover start/end bounds, missing matches, repeated delimiters, nth occurrence, empty pattern behavior, and delimiter bytes inside multibyte UTF-8 sequences if callers care.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/UTF8ByteArrayUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionInfo.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionInfo.java

Purpose: `VersionInfo` loads build metadata from `<component>-version-info.properties` and exposes the Hadoop Common version, revision, branch, build date/user/url, source checksum, protobuf compiler version, and compile platform.

Important APIs/types/functions: constructor `VersionInfo(String component)` loads a properties resource. Protected `_get*` methods read properties with `"Unknown"` defaults. Static `COMMON_VERSION_INFO` backs public static getters such as `getVersion`, `getRevision`, `getBuildVersion`, and `getCompilePlatform`. `main` prints version information and the containing jar.

Control flow: construction opens the resource through `ThreadUtil.getResourceAsStream`, loads `Properties`, logs a warning on `IOException`, and closes via `IOUtils.closeStream`. Public static getters delegate to the common singleton.

State and persistence behavior: build metadata is cached in a `Properties` instance for the life of the class. If loading fails, the cache remains mostly empty and getters return `"Unknown"`.

Dependencies and integration points: depends on `ThreadUtil`, `IOUtils`, SLF4J, and `ClassUtil`. `StringUtils.createStartupShutdownMessage` includes `VersionInfo` data in daemon startup logs.

Risks: missing or malformed resource files degrade silently to `"Unknown"` values after logging. The singleton is initialized at class load, so classpath issues are fixed for the process. `main` writes build details to stdout, which is intended for CLI use.

Test signals: tests should provide classpath resources, verify default values when absent, and assert printed output contains version and jar location.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionUtil.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionUtil.java

Purpose: `VersionUtil` wraps Hadoop's Maven-compatible `ComparableVersion` for comparing version strings.

Important APIs/types/functions: `compareVersions(String, String)` constructs two `ComparableVersion` instances and returns `compareTo`.

Control flow: direct object construction and comparison with no extra validation.

State and persistence behavior: stateless.

Dependencies and integration points: depends on `ComparableVersion`, matching Maven version ordering semantics used by compatibility checks.

Risks: null or unusual version strings are handled according to `ComparableVersion`, not this wrapper. Callers must interpret negative/zero/positive return values correctly.

Test signals: tests should cover numeric versions, qualifiers such as snapshot/alpha, equality normalization, and null behavior if callers can pass nulls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/VersionUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Waitable.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Waitable.java

Purpose: `Waitable<T>` is a tiny condition-backed handoff object that lets one side wait until a non-null value is provided.

Important APIs/types/functions: constructor stores a `Condition`. `await()` waits while `val` is null and returns the value. `provide(T)` sets `val` and calls `signalAll`. `hasVal()` and `getVal()` expose current state.

Control flow: `await` uses a loop around `Condition.await()` to handle spurious wakeups. `provide` performs a single assignment and notification.

State and persistence behavior: stores one in-memory value and the caller-supplied condition. Once provided, the value is not cleared or replaced-protected.

Dependencies and integration points: depends on `java.util.concurrent.locks.Condition`; callers must pair it with the associated lock.

Risks: the class does not acquire or validate the condition's lock. Calling `await` or `provide` without holding the lock required by the `Condition` will throw `IllegalMonitorStateException` or race. `provide(null)` wakes waiters but leaves `hasVal` false and `await` will continue waiting. Fields are not volatile, so lock discipline is required for visibility.

Test signals: tests should cover proper lock usage, spurious wake resilience, interrupt propagation from `await`, `provide(null)` behavior, and visibility of `hasVal/getVal` under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Waitable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/WeakReferenceMap.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/WeakReferenceMap.java

Purpose: `WeakReferenceMap<K,V>` maps keys to weakly referenced values and recreates values on demand, offering an alternative to long-lived strong maps or `ThreadLocal` storage where values may be reclaimed by GC.

Important APIs/types/functions: constructor accepts a non-null factory and optional `referenceLost` callback. `get(K)` resolves current value, removes and reports cleared references, then calls `create`. `create(K)` builds a strong local value, stores it as a weak reference, retrieves and resolves the map value, and retries if GC or a race loses the value during creation. `put`, `remove`, `containsKey`, `lookup`, `resolve`, `prune`, `clear`, `size`, `getReferenceLostCount`, and `getEntriesCreatedCount` provide map operations and counters.

Control flow: reads use `ConcurrentHashMap`. `get` first resolves without locking; on cleared weak reference it conditionally removes the old reference and calls `noteLost`. Creation increments a counter, requires a non-null factory result, writes a new weak reference, retrieves the current map entry, and loops if the resolved value is null. `prune` iterates the concurrent map and removes entries whose weak references have cleared.

State and persistence behavior: state is in-memory only: a concurrent map of weak references, factory callback, optional loss callback, atomic counters, and a `LogExactlyOnce` for creation-time reference loss. Values can disappear whenever no strong references exist outside the map.

Dependencies and integration points: depends on Java weak references, concurrent collections, atomics, Java functional interfaces, SLF4J, `LogExactlyOnce`, and Hadoop audience annotations. It is intended for cache-like integration points where recreation is acceptable.

Risks: map `size()` includes cleared weak references until get/remove/prune cleans them. Concurrent `create` calls for the same key can construct multiple values; the last put wins and losers may be discarded. Callback side effects run synchronously in caller threads. Values must tolerate recreation and identity changes. `put(key, null)` stores a weak reference to null and subsequent `get` creates a new value.

Test signals: tests should force GC-cleared references, verify `prune` and lost counters/callbacks, exercise concurrent creates, assert non-null factory enforcement, and verify returned value matches the current map value under races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/WeakReferenceMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/XMLUtils.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/XMLUtils.java

Purpose: `XMLUtils` centralizes secure XML/XSLT factory creation and a stylesheet transformation helper to reduce XXE and external-resource exposure.

Important APIs/types/functions: constants name JAXP/SAX security features. `transform(InputStream, InputStream, Writer)` applies an XSLT stylesheet using a secure transformer factory. `newSecureDocumentBuilderFactory`, `newSecureSAXParserFactory`, `newSecureTransformerFactory`, and `newSecureSAXTransformerFactory` create configured factories. `bestEffortSetAttribute` and `setOptionalSecureTransformerAttributes` set external DTD/stylesheet access restrictions when supported.

Control flow: parser factories enable `FEATURE_SECURE_PROCESSING`, disallow doctype declarations, disable external DTD loading and external entity resolution, and for DOM disable entity reference node creation. Transformer factories enable secure processing and then attempt optional external-access attributes. Unsupported optional attributes flip static `AtomicBoolean` flags to avoid repeated attempts.

State and persistence behavior: two static atomic flags remember whether the JVM transformer supports optional attributes. No XML data is persisted by the utility.

Dependencies and integration points: depends on JAXP DOM/SAX/transform APIs, SLF4J, and XML SAX exceptions. Tests and Hadoop code parsing XML configuration or servlet output should use these factories.

Risks: optional transformer attributes are best-effort; on unsupported runtimes the class logs at debug and proceeds with only secure processing. `transform` accepts arbitrary stylesheet and XML streams, so security depends on the configured factory and caller-controlled inputs. Factories may throw if a parser implementation does not support required features.

Test signals: existing `TestXMLUtils` references secure DOM parsing. Tests should include XXE/doctype rejection, disabled external entities, transformer external access behavior, and fallback when optional attributes are unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/XMLUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ZKUtil.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ZKUtil.java

Purpose: `ZKUtil` parses Hadoop ZooKeeper ACL and authentication configuration strings and resolves secret-bearing configuration indirection through files.

Important APIs/types/functions: `parseACLs(String)` parses comma-separated `scheme:id:perm` entries into ZooKeeper `ACL`s. `parseAuth(String)` parses comma-separated `scheme:auth` entries into `ZKAuthInfo`. `resolveConfIndirection(String)` reads file contents when a value starts with `@`. `removeSpecificPerms(int,int)` removes permission bits by XOR. Nested `ZKAuthInfo`, `BadAclFormatException`, and `BadAuthFormatException` carry parsed auth and validation failures.

Control flow: ACL parsing trims and omits empty comma components, validates first/last colon positions, builds `Id` from scheme and id substrings, and converts permission characters `r/w/c/d/a` into ZooKeeper permission bits. Auth parsing splits each component on the first colon and encodes auth bytes as UTF-8. Indirection trims the path after `@`, reads the file as UTF-8, and trims content.

State and persistence behavior: stateless. It reads local files when indirection is used and returns auth byte arrays held by callers.

Dependencies and integration points: depends on ZooKeeper `ZooDefs`, `ACL`, `Id`, Hadoop `HadoopIllegalArgumentException`, shaded Guava `Splitter`/`Files`, and Hadoop `Lists`. Used by HA failover and `ZKCuratorManager` to secure znodes.

Risks: `removeSpecificPerms` uses XOR, which toggles bits rather than strictly clearing bits when `remove` contains permissions absent from `perms`; callers must pass a subset mask. ACL/auth values may contain secrets and should not be logged. File indirection allows local file reads based on config; permissions and path validation are external concerns. ACL parser allows colons inside the id by using first/last colon, which is intentional for principals but must be tested.

Test signals: `TestZKUtil` covers empty/null ACLs/auths, malformed ACL/auth, permission removal, valid ACLs, and auth parsing. Additional tests should check file indirection trimming and the XOR semantics for non-subset masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ZKUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/BloomFilter.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/BloomFilter.java

Purpose: `BloomFilter` implements a classic mutable Bloom filter over a `BitSet`, providing probabilistic set membership with no false negatives before destructive operations such as `not`.

Important APIs/types/functions: constructors support Writable deserialization and explicit `vectorSize`, `nbHash`, and `hashType`. `add(Key)` sets all hashed positions. `membershipTest(Key)` checks all hashed positions. `and`, `or`, `xor`, and `not` mutate this filter. `getVectorSize`, `toString`, `write`, `readFields`, and private `getNBytes` provide introspection and serialization.

Control flow: add/test call `HashFunction.hash`, clear the hash function no-op, and iterate `nbHash` positions. Logical operations validate non-null compatible `BloomFilter` instances with matching vector size and hash count. Serialization writes the `Filter` header then packs bits into bytes using little bit order within each byte; deserialization reconstructs the `BitSet`.

State and persistence behavior: in-memory state is inherited filter dimensions/hash function plus a mutable `BitSet`. Persistent state is Hadoop `Writable` data: filter header plus packed bit vector.

Dependencies and integration points: extends `Filter`, uses `Key`, `HashFunction`, `BitSet`, and Hadoop Writable data streams. Public/stable for HDFS and MapReduce-style probabilistic filtering.

Risks: not thread-safe. Logical compatibility does not verify `hashType`, only vector size and hash count. `not` invalidates normal Bloom filter no-false-negative semantics. Serialization format must remain compatible with old `Filter` header behavior.

Test signals: tests should cover add/test, null key exceptions, logical operations compatibility failures, bit-level read/write round trips, and hash-type mismatch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/BloomFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/CountingBloomFilter.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/CountingBloomFilter.java

Purpose: `CountingBloomFilter` implements a counting Bloom filter using 4-bit counters packed into `long` words, supporting approximate counts and deletion.

Important APIs/types/functions: `add(Key)` increments hashed buckets up to `BUCKET_MAX_VALUE` 15. `delete(Key)` verifies membership and decrements buckets between 1 and 14. `membershipTest`, `approximateCount`, `and`, `or`, `not`, `xor`, `toString`, `write`, and `readFields` implement filter behavior and serialization. `buckets2words` maps vector size to 64-bit storage count.

Control flow: each hashed position maps to `wordNum = h >> 4` and `bucketShift = (h & 0x0f) << 2`. Add saturates at 15. Delete first performs a probabilistic membership test and then decrements only non-saturated buckets. Approximate count returns the minimum counter across hashes.

State and persistence behavior: mutable `long[] buckets` plus inherited filter metadata. Writable output writes inherited header followed by all bucket words.

Dependencies and integration points: extends `Filter`, uses `Key` and Hadoop data streams. Suitable for Hadoop components needing approximate membership plus removal.

Risks: delete can create false negatives when membership was a false positive or counters are shared. Saturated buckets are never decremented, preserving overflow but skewing counts. Logical operations use bitwise AND/OR on packed counters, which is not the same as min/max counter algebra. `not` and `xor` are unsupported.

Test signals: tests should cover counter saturation, deletion of absent keys, approximate count bounds, serialization round trip, and unsupported operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/CountingBloomFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/DynamicBloomFilter.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/DynamicBloomFilter.java

Purpose: `DynamicBloomFilter` grows by adding rows of standard Bloom filters once the active row reaches a configured record threshold.

Important APIs/types/functions: constructor accepts vector size, hash count/type, and per-row threshold `nr`. `add(Key)` inserts into the active row or creates a new row. `membershipTest(Key)` checks each row. `and`, `or`, `xor`, `not`, `toString`, `write`, and `readFields` operate across the row matrix. Private `addRow` and `getActiveStandardBF` manage matrix growth.

Control flow: insert obtains the last row when `currentNbRecord < nr`; otherwise it appends a new `BloomFilter`, resets `currentNbRecord`, inserts, then increments. Membership returns true if any row matches. Logical operations require another `DynamicBloomFilter` with same vector size, hash count, row count, and `nr`, then delegate row-by-row.

State and persistence behavior: stores `nr`, `currentNbRecord`, and an array of mutable `BloomFilter` rows. Writable state serializes inherited metadata, threshold, current record count, row count, and each row.

Dependencies and integration points: extends `Filter` and composes `BloomFilter`.

Risks: `membershipTest(null)` returns true, unlike other Bloom implementations that throw on null; this can hide caller bugs. `currentNbRecord` tracks only the latest row and does not deduplicate keys, so repeated adds drive growth. Logical operations require identical row counts, limiting combining independently grown filters. Not thread-safe.

Test signals: tests should cover row growth at threshold, null membership behavior, serialization preserving rows/current count, and compatibility checks for logical operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/DynamicBloomFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Filter.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Filter.java

Purpose: `Filter` is the abstract Writable base for Hadoop Bloom-style filters, defining common metadata and bulk add operations.

Important APIs/types/functions: protected fields are `vectorSize`, `hash`, `nbHash`, and `hashType`. Abstract methods include `add`, `membershipTest`, `and`, `or`, `xor`, and `not`. Bulk `add` overloads accept `List<Key>`, `Collection<Key>`, and `Key[]`. `write` and `readFields` serialize a versioned header.

Control flow: constructors initialize hash metadata and create a `HashFunction`. Bulk add methods null-check the container and loop over keys. `readFields` supports old unversioned formats by treating a positive first int as `nbHash` and defaulting `hashType` to Jenkins; otherwise it requires current negative `VERSION`.

State and persistence behavior: inherited in-memory metadata drives hashing. Writable state persists header values and reconstructs `HashFunction` on read; subclasses append their own state.

Dependencies and integration points: depends on Hadoop `Writable`, Hadoop hash implementations, and `HashFunction`.

Risks: old-format compatibility must be preserved. Bulk add checks only the container, not individual null keys. `hashType` compatibility is not enforced by all subclasses' logical operations.

Test signals: tests should include header round trips, old-format reads, invalid version rejection, and bulk add null handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Filter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/HashFunction.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/HashFunction.java

Purpose: `HashFunction` adapts a Hadoop `Hash` implementation into `k` bounded Bloom filter positions.

Important APIs/types/functions: constructor validates positive `maxValue` and `nbHash`, resolves `Hash.getInstance(hashType)`, and rejects unknown hash types. `hash(Key)` returns an `int[]` of positions. `clear()` is a no-op retained for API symmetry.

Control flow: hashing extracts key bytes, rejects null and empty byte arrays, then repeatedly hashes the same bytes using the previous hash as seed (`initval`) and maps each result with `Math.abs(initval % maxValue)`.

State and persistence behavior: stores immutable-ish max value, hash count, and hash implementation reference after construction. No external persistence.

Dependencies and integration points: depends on `Key` and `org.apache.hadoop.util.hash.Hash` implementations such as Jenkins/Murmur.

Risks: `Math.abs(Integer.MIN_VALUE)` remains negative, but because modulo by positive `maxValue` occurs first, only a remainder of `Integer.MIN_VALUE` would be problematic; Java remainder magnitude is below divisor, so this is effectively safe except theoretical edge cases when maxValue permits that remainder. Distribution depends on chained seeding. Not synchronized, but current `clear` is no-op and hash implementations must be safe for use pattern.

Test signals: tests should verify constructor validation, unknown hash rejection, empty key rejection, deterministic positions, and bounds for all returned positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/HashFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Key.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Key.java

Purpose: `Key` is the WritableComparable key representation for Bloom filters, storing raw bytes plus a weight used by retouched filters.

Important APIs/types/functions: constructors set bytes with default weight `1.0` or explicit weight. `set`, `getBytes`, `getWeight`, `incrementWeight`, `equals`, `hashCode`, `write`, `readFields`, and `compareTo` implement state access, serialization, and ordering.

Control flow: `set` rejects null byte arrays and stores the reference directly. Comparison first orders by byte-array length, then byte values, then casts weight difference to `int`. Serialization writes byte length, bytes, and double weight.

State and persistence behavior: mutable byte-array reference and mutable weight. Writable state persists both.

Dependencies and integration points: implements Hadoop `WritableComparable` and is consumed by all Bloom filter implementations.

Risks: byte arrays are not defensively copied, so external mutation changes key identity/hash. `compareTo` casts double difference to int, so small weight differences under 1.0 compare as equal even when `hashCode` differs, potentially violating sorted collection expectations. `hashCode` XORs byte and weight hashes and is weak for collisions.

Test signals: tests should cover serialization, equality/hash consistency for exact weights, mutable array effects, comparison ordering, and fractional weight comparison behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/Key.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RemoveScheme.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RemoveScheme.java

Purpose: `RemoveScheme` defines constants for selective-clearing strategies used by `RetouchedBloomFilter`.

Important APIs/types/functions: constants are `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.

Control flow: no executable code; consumers switch on the short constants.

State and persistence behavior: static constants only.

Dependencies and integration points: implemented by `RetouchedBloomFilter` to select which bit to clear for known false positives.

Risks: as an interface of constants, any implementing class exposes these names. Invalid short values are handled by `RetouchedBloomFilter` with `AssertionError`.

Test signals: retouched filter tests should exercise each scheme and invalid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RemoveScheme.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RetouchedBloomFilter.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RetouchedBloomFilter.java

Purpose: `RetouchedBloomFilter` extends `BloomFilter` with false-positive tracking and selective bit clearing to remove selected false positives while accepting introduced false negatives.

Important APIs/types/functions: `add(Key)` records keys in `keyVector` for every hashed bit. `addFalsePositive` overloads record known false positives in `fpVector`. `selectiveClearing(Key, short)` chooses a bit using `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, or `RATIO` and clears it. Helpers include `randomRemove`, `minimumFnRemove`, `maximumFpRemove`, `ratioRemove`, `clearBit`, `removeKey`, `computeRatio`, `getWeight`, and `createVector`. Writable methods persist base bits plus false-positive vectors, key vectors, and ratios.

Control flow: insertion sets bits and appends the key to per-position synchronized lists. False-positive insertion appends to `fpVector` positions but does not set bits. Selective clearing verifies the target currently tests as a member, hashes it, selects an index according to weighted lists, then clears the bit and removes affected keys/false positives from all their hashed lists.

State and persistence behavior: inherited `BitSet` plus arrays of synchronized `List<Key>` for recorded keys and false positives, a ratio array, and lazily initialized `Random`. Serialization writes every list and ratio after the base Bloom filter state.

Dependencies and integration points: extends `BloomFilter` and implements `RemoveScheme`; uses `Key` weights to estimate false-negative/false-positive tradeoffs.

Risks: `randomRemove` returns an index in `[0, nbHash)`, not a hashed bit position, while other schemes return positions from the hashed vector; this means random clearing can clear an unrelated low-index bit. The synchronized lists are not used with external synchronization during iteration/removal, so compound operations are not thread-safe. Stored `Key` objects are mutable, which can corrupt list removal semantics. Serialization can be large because it stores per-bit key lists.

Test signals: tests should cover all selective schemes, especially random index semantics, list cleanup after clearing, serialization with populated vectors, null handling, and false-negative tradeoffs after clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/bloom/RetouchedBloomFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGet.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGet.java

Purpose: `AsyncGet<R,E>` defines a pollable asynchronous result abstraction whose `get` can time out before the underlying computation is complete.

Important APIs/types/functions: `get(long, TimeUnit)` returns a possibly null result or throws implementation exception `E`, `TimeoutException`, or `InterruptedException`. `isDone()` reports completion. Nested `Util.wait(Object,long,TimeUnit)` maps timeout semantics to `Object.wait`.

Control flow: implementations provide actual completion logic. Utility wait blocks indefinitely for negative timeout, returns immediately for zero, and waits `unit.toMillis(timeout)` for positive values.

State and persistence behavior: interface only; no state.

Dependencies and integration points: used by `AsyncGetFuture` to adapt pollable operations to a `Future` API.

Risks: `Util.wait` requires the caller to hold the object's monitor and truncates sub-millisecond timeouts through `toMillis`. Zero timeout means no wait. Implementations must consistently throw `TimeoutException` rather than blocking beyond timeout.

Test signals: tests should verify timeout semantics, indefinite waits, interrupt propagation, and `isDone` consistency for implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGetFuture.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGetFuture.java

Purpose: `AsyncGetFuture<T,E>` adapts an `AsyncGet` into Guava's `AbstractFuture`, performing lazy polling when `get`, timed `get`, or `isDone` is invoked.

Important APIs/types/functions: constructor stores the `AsyncGet`. `callAsyncGet(long, TimeUnit)` is the core polling method. Overrides `get()`, `get(timeout, unit)`, and `isDone()` trigger polling before delegating to `AbstractFuture`.

Control flow: `called` is an `AtomicBoolean` that allows only one in-flight call to `asyncGet.get`. If polling times out, the flag resets so later calls can retry. If polling returns a value, `set` completes the future. Any non-timeout throwable completes the future exceptionally. Timed `get` polls with the supplied timeout and then calls `super.get(0, MILLISECONDS)`.

State and persistence behavior: in-memory future state comes from `AbstractFuture`, plus `called` and the underlying async object. No persistence.

Dependencies and integration points: depends on shaded Guava `AbstractFuture`, Java `Future` semantics, and SLF4J trace logging.

Risks: `isDone()` can perform a nonblocking poll and has side effects. Timed `get` may spend the entire timeout in `asyncGet.get`, then immediately time out on the future if no result was set. Catching `Throwable` means severe errors are captured as future failures. Concurrent callers that lose the `called` CAS delegate immediately to `AbstractFuture`, which may block or time out independently.

Test signals: tests should cover retry after timeout, exception propagation, cancellation behavior, concurrent callers, null successful results, and side effects from `isDone`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/AsyncGetFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/ExecutorHelper.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/ExecutorHelper.java

Purpose: `ExecutorHelper` provides shared after-execute exception extraction for Hadoop executor subclasses.

Important APIs/types/functions: package-private `logThrowableFromAfterExecute(Runnable, Throwable)` logs debug context, handles JDK behavior where `afterExecute` receives null for failed `Future` tasks, and logs any extracted throwable at warn.

Control flow: if throwable is null and the runnable is a completed `Future`, it calls `get` to surface `ExecutionException`, interruption, or other throwables. Interruptions re-interrupt the current thread. Non-null throwable is logged.

State and persistence behavior: stateless except logging.

Dependencies and integration points: called by `HadoopThreadPoolExecutor` and `HadoopScheduledThreadPoolExecutor`.

Risks: calling `Future.get()` in `afterExecute` is guarded by `isDone`, but custom Future implementations could still behave unexpectedly. Warnings expose task exception details. Package-private scope limits reuse.

Test signals: tests should submit failing `Runnable`/`Callable` tasks to Hadoop executors and verify exceptions are logged and interrupt status is restored after interrupted `get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/ExecutorHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopExecutors.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopExecutors.java

Purpose: `HadoopExecutors` is a factory class for Hadoop executor services that add task exception logging, plus a bounded shutdown helper.

Important APIs/types/functions: factory methods create cached, fixed, scheduled, single-thread, and single-thread scheduled executors. Hadoop variants return `HadoopThreadPoolExecutor` or `HadoopScheduledThreadPoolExecutor`; single-thread variants delegate to JDK `Executors` to preserve exact wrapper semantics. `shutdown(ExecutorService, Logger, long, TimeUnit)` performs graceful then forced shutdown.

Control flow: factory methods mirror JDK executor parameters. Shutdown returns for null, calls `shutdown`, waits once, calls `shutdownNow` if needed, waits a second time, logs success or error, handles interruption by logging and forcing shutdown, and rethrows unexpected exceptions.

State and persistence behavior: no class state. Created executor instances own runtime queues and threads.

Dependencies and integration points: depends on Java concurrent executors and SLF4J logger supplied by callers. Used wherever Hadoop wants standard executor construction with better exception logging.

Risks: fixed thread pools use unbounded `LinkedBlockingQueue`, which can grow without backpressure. Cached pools can create unbounded threads like JDK cached pools. Shutdown does not restore interrupt status after catching `InterruptedException`. Log message spelling has a minor typo but no behavioral impact.

Test signals: tests should verify factory types, exception logging via subclasses, shutdown graceful/forced paths, null shutdown no-op, and interruption handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopExecutors.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopScheduledThreadPoolExecutor.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopScheduledThreadPoolExecutor.java

Purpose: `HadoopScheduledThreadPoolExecutor` extends `ScheduledThreadPoolExecutor` to log task execution context and surface exceptions from scheduled tasks.

Important APIs/types/functions: constructors mirror superclass variants for core pool size, thread factory, and rejected execution handler. `beforeExecute` logs debug thread/runnable information. `afterExecute` delegates to superclass then `ExecutorHelper.logThrowableFromAfterExecute`.

Control flow: scheduled tasks run according to superclass behavior; hooks add logging and exception extraction.

State and persistence behavior: executor state is inherited from `ScheduledThreadPoolExecutor`; no additional fields except static logger.

Dependencies and integration points: created by `HadoopExecutors.newScheduledThreadPool`.

Risks: only logs exceptions; it does not change task failure semantics. Debug logging calls `r.getClass().getName()` and assumes non-null runnable supplied by executor. Scheduled executor queue behavior remains JDK behavior.

Test signals: tests should schedule failing callables/runnables and verify `afterExecute` extracts exceptions; constructor variants should preserve thread factory and rejection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopScheduledThreadPoolExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopThreadPoolExecutor.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopThreadPoolExecutor.java

Purpose: `HadoopThreadPoolExecutor` extends `ThreadPoolExecutor` to add debug execution logging and reliable task exception logging.

Important APIs/types/functions: constructors mirror superclass variants for queue, thread factory, and rejected execution handler. `beforeExecute` logs debug context. `afterExecute` delegates to superclass and then `ExecutorHelper.logThrowableFromAfterExecute`.

Control flow: normal `ThreadPoolExecutor` scheduling and lifecycle are unchanged; hooks only observe and log.

State and persistence behavior: all runtime state is inherited; this class adds only static logging.

Dependencies and integration points: created by `HadoopExecutors` cached/fixed factory methods.

Risks: final class cannot be subclassed for additional behavior. Logging uncaught task exceptions does not retry or propagate to submitters beyond normal `Future` semantics. Queue/thread limits come from caller/factory choices.

Test signals: tests should submit failing execute and submit tasks and assert exception extraction/logging, plus verify custom factories/handlers are honored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/HadoopThreadPoolExecutor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/SubjectInheritingThread.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/SubjectInheritingThread.java

Purpose: `SubjectInheritingThread` restores JAAS `Subject` propagation for Hadoop-created threads on Java versions where plain `Thread` no longer inherits the current subject.

Important APIs/types/functions: constructors mirror common `Thread` constructors while storing the target in `hadoopTarget`. `start()` is final and captures `SubjectUtil.current()` when the runtime does not already inherit subjects. `work()` is the overridable payload method. `run()` is final and executes `work` under `SubjectUtil.doAs(startSubject, PrivilegedAction)` when needed.

Control flow: callers either pass a `Runnable` or subclass and override `work`. On start, the current subject is captured before the new thread begins. In the new thread, `run` wraps `work` with the captured subject unless `SubjectUtil.THREAD_INHERITS_SUBJECT` says the JVM already handles propagation.

State and persistence behavior: stores `startSubject` and `hadoopTarget` per thread object. No persistence beyond thread lifetime.

Dependencies and integration points: depends on JAAS `Subject`, `PrivilegedAction`, and Hadoop `SubjectUtil`. Search results show integration in configuration reconfiguration, metrics, Unix domain socket watcher/tests, HA stream pumping, IPC client/server threads, service launcher shutdown, and security tests.

Risks: subclasses must override `work`, not `run`; `run` is final to enforce subject restoration. Some constructors call a superclass constructor with a target for API compatibility but actual execution uses `hadoopTarget`, so behavior must stay aligned. Capturing subject in `start` means changes after construction but before start are honored.

Test signals: `TestSubjectPropagation` covers override and runnable modes. Broader tests should run on JVMs with and without native subject inheritance and verify nested/newly started threads observe expected subject.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/SubjectInheritingThread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/package-info.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/package-info.java

Purpose: package documentation declares `org.apache.hadoop.util.concurrent` as support for concurrent execution.

Important APIs/types/functions: no executable types; package annotations mark it `InterfaceAudience.Private` and `InterfaceStability.Unstable`.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: applies package-level API audience/stability to concurrency helpers including async adapters, executor factories, and subject-inheriting threads.

Risks: private/unstable annotations communicate that external consumers should not depend on compatibility.

Test signals: no direct tests needed beyond annotation/package compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/concurrent/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/curator/ZKCuratorManager.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/curator/ZKCuratorManager.java

Purpose: `ZKCuratorManager` wraps Apache Curator/ZooKeeper setup and common znode operations for Hadoop components, including ACL/auth loading, SSL and Kerberos configuration, recursive root creation, safe transaction fencing, and data/children/ACL helpers.

Important APIs/types/functions: manager APIs include constructor, `getCurator`, `close`, static `getZKAcls`, static `getZKAuths`, `start` overloads, `getACL`, `getData`, `getStringData`, `setData`, `getChildren`, `exists`, `create`, `createRootDirRecursively`, `delete`, `getNodePath`, `safeCreate`, `safeDelete`, `safeSetData`, and `createTransaction`. Nested `SafeTransaction` builds Curator transaction operations with a fencing znode created first and deleted last. Nested `HadoopZookeeperFactory` configures server principal, JAAS, Kerberos keytab/principal, SSL truststore/keystore, and creates `ZooKeeper` clients.

Control flow: `start` resolves the connect string from parameter or `CommonConfigurationKeys.ZK_ADDRESS`, reads retry/session settings, loads configured auths, optionally validates SSL config, builds a Curator client with a custom `HadoopZookeeperFactory`, starts it, and stores it. CRUD methods delegate directly to Curator builders. Recursive root creation splits an absolute path and creates each parent path if absent. Safe operations first check existence when appropriate, then open a `SafeTransaction`, enqueue the requested operation, and commit a multi-operation transaction with create-fence, requested operations, delete-fence.

State and persistence behavior: instance state is `Configuration` and a live `CuratorFramework` client. Persistent external state is ZooKeeper znodes, ACLs, data bytes, and fencing nodes. `HadoopZookeeperFactory.setJaasConfiguration` can mutate the JVM-global JAAS configuration.

Dependencies and integration points: depends on Curator, ZooKeeper, Hadoop `Configuration`, `CommonConfigurationKeys`, `SecurityUtil`, `JaasConfiguration`, `ZKUtil`, `Preconditions`, and `TruststoreKeystore`. The curator package is public/evolving but this manager is private; it is used by Hadoop components that coordinate through ZooKeeper.

Risks: `create(path)` checks existence before create, so concurrent creators can still race and receive create exceptions. `safeCreate`/`safeDelete` also perform prechecks outside the transaction. Fencing relies on the fencing path being unique/available and on transaction atomicity; stale existing fencing nodes cause failures. `SafeTransaction.commit` clears operations only after successful transaction, so failed commits leave the object with queued operations. SSL validation only checks non-empty strings; actual credentials are validated later. Global JAAS configuration changes can affect other ZooKeeper clients in the JVM. `removeSpecificPerms` risks remain in upstream ACL preparation.

Test signals: tests should use an embedded ZooKeeper/Curator server for start/auth/ACL behavior, recursive create, data versioned writes, delete with children, transaction fencing success and conflict, SSL missing config validation, and JAAS setup when SASL is enabled. Security tests should verify file-indirected auth/ACLs and no secret logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/curator/ZKCuratorManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/curator/package-info.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/curator/package-info.java

Purpose: package documentation declares `org.apache.hadoop.util.curator` as utilities for interacting with Curator ZooKeeper.

Important APIs/types/functions: no executable members; package annotations mark it `InterfaceAudience.Public` and `InterfaceStability.Evolving`.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: frames `ZKCuratorManager` as the package's Curator integration utility.

Risks: public/evolving means consumers may use the package but should expect API evolution.

Test signals: no direct tests beyond package compilation and annotation presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/curator/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/BindingUtils.java -->
# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/BindingUtils.java

Purpose: `BindingUtils` helps Hadoop code bind optional APIs through reflection while preserving clear availability checks and IOException unwrapping.

Important APIs/types/functions: `loadClass`, `loadClassSafely`, and `loadClass(ClassLoader,String)` resolve classes. `loadInvocation` builds a `DynMethods.UnboundMethod` or no-op method for optional instance/static invocation. `loadStaticMethod` requires the resolved method to be static. `noop`, `implemented`, `checkAvailable`, and `available` inspect method bindings. `extractIOEs(Supplier<T>)` unwraps `UncheckedIOException` into checked `IOException`.

Control flow: class loading catches `ClassNotFoundException` and returns null except for `loadClassSafely`, which wraps it in `RuntimeException`. Method loading uses `DynMethods.Builder(...).impl(...).orNoop().build()`, logs found/missing at debug, and returns a no-op when source class is absent. Static loading verifies `method.isStatic()` with `checkState`. `implemented` returns false on the first no-op.

State and persistence behavior: stateless utility class with static logger.

Dependencies and integration points: depends on `DynMethods` in the same dynamic package, SLF4J, Hadoop `Preconditions.checkState`, and Java `UncheckedIOException`. It supports compatibility layers that must run across multiple Hadoop/API versions.

Risks: missing optional methods become no-ops unless callers explicitly call `checkAvailable`, which can hide integration gaps. `loadStaticMethod` calls `isStatic` even for no-op methods; behavior depends on `DynMethods` no-op implementation. `extractIOEs` only unwraps `UncheckedIOException`, not other runtime wrappers.

Test signals: tests should cover absent classes, absent methods returning no-ops, static/non-static enforcement, `implemented` with mixed methods, `checkAvailable` failures, and IOException extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/dynamic/BindingUtils.java -->
