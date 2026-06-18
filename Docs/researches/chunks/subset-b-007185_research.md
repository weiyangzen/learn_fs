# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.3.xml lines 36810-38433

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.3. It starts mid-entry in the tail of `org.apache.hadoop.util.Shell`, beginning inside the symbolic-link command method, then covers the later `Shell` command helpers, fields, and class documentation. It continues through `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, `VersionInfo`, and most of the visible `org.apache.hadoop.util.bloom` package. The chunk ends at the close of the API document after empty package markers for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`.

The source is generated compatibility metadata, not implementation source. The research value is the stable API contract: public/protected signatures, declared exceptions, visibility, abstract/final/static flags, deprecation markers, inherited/implemented types, fields, and Javadocs.

## Purpose

The `Shell` portion documents Hadoop's base abstraction for portable subprocess execution. It exposes command-construction helpers for symlinks, readlink, process liveness, signal delivery, script naming/execution, Hadoop home and binary discovery, Windows `winutils` lookup, bash probing, environment and working-directory injection, timeout state, and simple static command execution.

The common utility classes provide runtime support used throughout Hadoop. `StringInterner` offers strong and weak string canonicalization. `SysInfo` abstracts host-level resource metrics. `Tool` and `ToolRunner` define the standard command-line application lifecycle with Hadoop generic option parsing and configuration injection. `VersionInfo` exposes build metadata embedded in Hadoop artifacts.

The Bloom filter package documents compact probabilistic set-membership structures. It includes a plain Bloom filter, counting Bloom filter, dynamic Bloom filter, retouched Bloom filter, hash projection helper, and retouching scheme constants. These APIs support compact membership summaries with Hadoop-style serialization hooks.

## Important APIs, Types, and Functions

### Shell Tail

- The chunk begins inside the method entry for a symbolic-link command helper that accepts `target` and `link` strings and returns a command to create symbolic links.
- `getReadlinkCommand(String link)` returns a platform command for reading a symlink target.
- `getCheckProcessIsAliveCommand(String pid)` returns a `kill -0`-style command or equivalent for checking process liveness.
- `getSignalKillCommand(int code, String pid)` returns a command for sending a signal to a process.
- `getEnvironmentVariableRegex()` returns the regex used to match environment-variable references.
- `appendScriptExtension(File parent, String basename)` and `appendScriptExtension(String basename)` infer `.cmd` on Windows and `.sh` elsewhere.
- `getRunScriptCommand(File script)` returns the platform script runner, using `cmd` on Windows and `bash` otherwise.
- `getHadoopHome()` returns the Hadoop home directory and throws `IOException` if it cannot be located.
- `getQualifiedBin(String executable)` and `getQualifiedBinPath(String executable)` fully qualify Hadoop binaries from known bin locations and verify existence. The path variant also exposes canonicalization `IOException`.
- `hasWinutilsPath()`, `getWinUtilsPath()`, and `getWinUtilsFile()` are the supported `winutils` discovery API. The getters deliberately fail with exceptions when the path cannot be resolved.
- `checkIsBashSupported()` returns bash availability and can throw `InterruptedIOException`.
- Protected instance mutators `setEnvironment(Map)` and `setWorkingDirectory(File)` configure subprocess execution context.
- Protected `run()` executes the shell command if interval gating says it is needed. Subclasses provide `getExecString()` and parse stdout in `parseExecResult(BufferedReader)`.
- Runtime inspection methods include `getEnvironment(String)`, `getProcess()`, `getExitCode()`, and `isTimedOut()`.
- Static `execCommand(...)` overloads run simple command arrays with optional environment and timeout, returning stdout as `String` and throwing `IOException`.
- Public fields include `LOG`, Hadoop home property/env names, Windows command-length constants, the deprecated misspelled `WINDOWS_MAX_SHELL_LENGHT`, `USER_NAME_COMMAND`, `WindowsProcessLaunchLock`, `osType`, OS booleans, `PPC_64`, `ENV_NAME_REGEX`, Unix command names, deprecated nullable `WINUTILS`, `isSetsidAvailable`, and `TOKEN_SEPARATOR_REGEX`.
- Protected instance fields `timeOutInterval` and `inheritParentEnv` expose timeout and environment inheritance state to subclasses.

### Common Utility Classes

- `StringInterner.strongIntern(String)` returns a representative equal string retained by strong reference. `weakIntern(String)` returns a representative equal string that can be garbage collected when no strong references remain.
- `SysInfo` is abstract. `newInstance()` returns the default OS-specific implementation or throws `UnsupportedOperationException` if the OS cannot be determined.
- `SysInfo` declares metrics for total/available virtual memory, total/available physical memory, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, vcores used, aggregate network bytes read/written, and aggregate storage bytes read/written.
- `Tool` extends `org.apache.hadoop.conf.Configurable` and defines `run(String[] args) throws Exception`, returning a process-style exit code. Its contract asks applications to delegate generic Hadoop options to `ToolRunner`.
- `ToolRunner.run(Configuration, Tool, String[])` parses generic arguments, sets the possibly modified configuration on the tool, and invokes `Tool.run`.
- `ToolRunner.run(Tool, String[])` delegates through the tool's current configuration. `printGenericCommandUsage(PrintStream)` emits generic option help, and `confirmPrompt(String)` returns true only for case-insensitive `y` or `yes`.
- `VersionInfo` has a protected component-name constructor and protected instance getters for version, revision, branch, date, user, URL, source checksum, build version, and protoc version.
- Static `VersionInfo` methods expose the Hadoop build metadata and a `main(String[])` entry point for reporting it.

### Bloom Filter APIs

- `BloomFilter` extends `Filter`. It has a default constructor for `readFields` and a `(int vectorSize, int nbHash, int hashType)` constructor. Public methods include `add(Key)`, `membershipTest(Key)`, logical `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, `toString()`, `getVectorSize()`, and `write(DataOutput)`/`readFields(DataInput)`.
- `CountingBloomFilter` is `final` and extends `Filter`. It supports `add(Key)`, `delete(Key)`, `membershipTest(Key)`, `approximateCount(Key)`, logical operations, string rendering, and serialization. The docs warn that adding the same key more than 15 times can overflow its buckets and raise error rates.
- `DynamicBloomFilter` extends `Filter` and adds a `(int vectorSize, int nbHash, int hashType, int nr)` constructor, where `nr` is the per-row threshold for recorded keys. It grows by adding Bloom filter rows.
- `HashFunction` is `final`; its constructor binds `maxValue`, `nbHash`, and `hashType`. `hash(Key)` returns multiple bounded integer positions, while `clear()` is documented as a no-op.
- `RemoveScheme` is a constants interface for retouched filters. It defines `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` is `final`, extends `BloomFilter`, and implements `RemoveScheme`. It records known false positives through overloads accepting a single `Key`, `Collection`, `List`, or `Key[]`; `selectiveClearing(Key, short)` applies a removal scheme; `write` and `readFields` persist retouched state.

## Control Flow

The XML has no method bodies, but the API contracts imply important execution paths.

`Shell` subclasses configure environment and working directory, then call `run()`. The base class obtains the command vector from `getExecString()`, launches the process, tracks timeout/exit/process state, and delegates stdout parsing to `parseExecResult(BufferedReader)`. Static `execCommand` is the short path for callers that only need to execute a command array and receive output.

Platform-sensitive shell flow depends on static OS detection. OS booleans, script extension helpers, `winutils` accessors, bash support checks, `setsid` availability, Unix command names, and Windows process-launch locking all shape how Hadoop starts and controls subprocesses on different hosts.

`ToolRunner` is the standard CLI flow. Generic Hadoop options are parsed into a `Configuration`, that configuration is installed on the `Tool`, and remaining application arguments are passed to `Tool.run`. Exit code and exception behavior are owned by the called tool and propagated by `ToolRunner`.

`SysInfo` flow starts with `newInstance()` selecting an OS implementation, after which clients poll resource values. Metrics are snapshots or counters, not persistent application state.

Bloom filter flow starts by binding vector size, number of hashes, and hash type. `add(Key)` hashes a key to positions and mutates the backing vector, counters, rows, or retouched metadata. `membershipTest(Key)` hashes the same key and tests whether the relevant state indicates possible membership. Logical operations combine compatible filters. Serialization flows through `write(DataOutput)` and `readFields(DataInput)`.

`CountingBloomFilter.delete(Key)` is documented as a no-op if the key is not believed present. `DynamicBloomFilter.add(Key)` inserts into an active row until the row threshold is reached, then creates a new row. `RetouchedBloomFilter.selectiveClearing` uses recorded false-positive information and a `RemoveScheme` to reset selected bits, intentionally trading away the classic no-false-negatives Bloom filter guarantee.

## State and Persistence Behavior

This JDiff file persists the 2.8.3 API surface for compatibility checks. It does not persist Hadoop runtime data.

`Shell` has process-local mutable state for environment overrides, working directory, timeout interval, parent environment inheritance, current `Process`, exit code, and timeout status. Static state caches platform classification, command names, `winutils` resolution, bash/setsid capability, and global Windows process launch synchronization. These values are not durable, but they affect every component that shells out in the current JVM.

`StringInterner` keeps canonical string representatives in memory. Strong interning can intentionally retain high-cardinality strings for the lifetime of the cache, while weak interning allows reclamation.

`SysInfo` exposes host resource state. Capacity metrics, utilization percentages, cumulative CPU time, and byte counters are runtime observations of the host and can change between calls. The docs explicitly allow unavailable sentinel values for CPU usage and vcore usage.

`ToolRunner` mutates the `Tool`'s in-memory `Configuration` before invoking `run`. Any durable effects come from the tool implementation, not from the `ToolRunner` API itself.

`VersionInfo` exposes immutable build-time metadata: version, revision, branch, date, user, source URL, checksum, build version, and protoc version.

Bloom filter classes have explicit persistence through `write(DataOutput)` and `readFields(DataInput)`. Durable state includes inherited filter parameters, bit vectors or counters, dynamic filter rows and row thresholds, hash settings, and retouched false-positive metadata. Serialized compatibility depends on stable layout and stable hash-position behavior.

## Dependencies and Integration Points

The visible APIs depend on Java platform types such as `String`, primitive arrays, `File`, `Process`, `BufferedReader`, `PrintStream`, `IOException`, `InterruptedIOException`, `FileNotFoundException`, `DataInput`, `DataOutput`, `Collection`, `List`, and `Map`.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configurable` and `Configuration` for `Tool`/`ToolRunner` configuration propagation.
- `org.apache.hadoop.util.GenericOptionsParser`, referenced as the generic command-line option parser used by `ToolRunner`.
- `org.apache.hadoop.util.Shell.OSType`, referenced by the `Shell.osType` field.
- SLF4J through `Shell.LOG`.
- `org.apache.hadoop.util.bloom.Filter` and `Key`, which define the base Bloom filter contract and key representation used by all filter variants in this chunk.
- `org.apache.hadoop.util.hash.Hash`, referenced by Bloom constructors and `HashFunction` as the hash implementation selector.
- Hadoop `Writable`-style serialization through `write(DataOutput)` and `readFields(DataInput)`.

Package integration is also visible. `org.apache.hadoop.util` is documented as common utilities. `org.apache.hadoop.util.bloom` contains the probabilistic data structures. `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` appear as empty package elements in this line range, signaling package presence in the JDiff document but no public API entries in this chunk.

## Risks and Edge Cases

- The range begins mid-method and mid-class. The complete `Shell` API requires reconciliation with the previous chunk.
- JDiff metadata cannot show implementation details such as command quoting, stream draining, timeout enforcement, environment merging, synchronization granularity, or serialized byte layout.
- `Shell.WINUTILS` is deprecated because it can be null. The preferred getters fail explicitly and are safer for callers that cannot tolerate late null dereferences.
- The misspelled `WINDOWS_MAX_SHELL_LENGHT` is deprecated but remains public for binary/source compatibility.
- Shell command helpers return string arrays, but callers still need to avoid unsafe command construction, platform-specific path assumptions, and commands that hang beyond intended timeout bounds.
- `WindowsProcessLaunchLock` is public global synchronization state; external misuse can serialize or block unrelated Windows process launches.
- `Tool.run` throws broad `Exception`, so users of the API need clear policies for logging, exit codes, and exception-to-process-result mapping.
- `ToolRunner.confirmPrompt` is interactive and can block automation if stdin is not controlled.
- `SysInfo.newInstance()` can fail on unsupported OS detection, and some metrics can be unavailable.
- `StringInterner.strongIntern` can create memory-retention issues for high-cardinality or untrusted input.
- Bloom filters naturally permit false positives. `RetouchedBloomFilter` can also create false negatives by design.
- `CountingBloomFilter` has a documented overflow edge when a key is inserted more than 15 times, and deletion/underflow can make approximate counts lower than the real count.
- Logical Bloom operations are only meaningful on compatible filters with matching vector sizes, hash counts, and hash types. This compatibility is implied by the data structure even where not fully stated in this slice.
- `DynamicBloomFilter` memory and serialized size grow with insert volume as new rows are added. Poor threshold sizing can produce unexpectedly large state.
- The `RemoveScheme.RATIO` Javadoc contains a typo in "false positve"; the constant spelling is still the compatibility-relevant surface.

## Test Signals

Useful validation for this chunk should include:

- API compatibility checks for every visible constructor, method, field, visibility flag, abstract/final/static marker, checked exception, implemented interface, and deprecation string.
- Shell tests for symlink/readlink command construction, process liveness and signal command construction, environment-variable regex, script extension and runner selection, Hadoop home lookup, qualified bin lookup, `winutils` present/absent behavior, bash support probing, and deprecated field presence.
- Shell execution tests for environment injection, parent-environment inheritance, working-directory selection, interval-gated `run`, stdout parsing delegation, timeout marking, exit-code capture, process exposure, nonzero exits, interrupted timeouts, and `IOException` propagation.
- Platform tests for OS booleans, `PPC_64`, Windows command-length constants including the deprecated misspelling, `WindowsProcessLaunchLock`, `setsid` availability, and token-separator parsing.
- `StringInterner` tests for identity reuse, equality preservation, strong-cache retention, weak-cache reclamation expectations, and null handling according to implementation behavior.
- `SysInfo` tests for OS-specific `newInstance` selection, unsupported OS failure, sane nonnegative memory/core/frequency values where available, `-1` unavailable sentinels for CPU/vcore metrics, and monotonic cumulative counters.
- `Tool`/`ToolRunner` tests for generic option parsing into `Configuration`, modified configuration injection, pass-through application args, null configuration handling, exit-code propagation, exception propagation, usage printing, and `confirmPrompt` yes/no parsing.
- `VersionInfo` tests for non-null static metadata, build-version composition, protoc version exposure, component-specific protected getters through a test subclass, and stable `main` output.
- Bloom filter tests for add/membership round trips, tolerated false positives, no false negatives for plain filters, vector-size reporting, string rendering, compatible logical operations, and serialization round trips.
- Counting filter tests for delete no-op on absent keys, approximate counts under normal additions, collision behavior, overflow behavior after repeated additions over 15, and underflow/false-negative behavior after deletes.
- Dynamic filter tests for row creation at `nr`, membership across rows, serialization preserving all rows, and logical operations against compatible dynamic filters.
- `HashFunction` tests for deterministic positions, expected number of hashes, bounds under `maxValue`, different hash-type behavior, and `clear()` being a no-op.
- Retouched filter tests for all false-positive registration overloads, null false-positive no-op behavior, each `RemoveScheme`, targeted false-positive reduction, expected false-negative tradeoff, and serialization preserving retouched metadata.

## Cross-Chunk Notes

This chunk must be merged with the preceding chunk to complete `org.apache.hadoop.util.Shell`, because line 36810 starts after the method entry has already begun. This chunk reaches the end of the 2.8.3 JDiff XML API document, so there is no later chunk after the empty `curator` and `hash` package markers.
