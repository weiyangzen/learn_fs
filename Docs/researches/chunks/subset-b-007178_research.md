# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.2.xml lines 36766-38218

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.8.2. It starts inside the tail of `org.apache.hadoop.util.Shell`, then covers `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, `VersionInfo`, and the visible `org.apache.hadoop.util.bloom` classes through the end of the XML API document. The final packages `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` are present but empty in this slice.

The source is generated API metadata rather than implementation code. The research surface is the public/protected compatibility contract: type names, inheritance, implemented interfaces, method signatures, checked exceptions, fields, deprecation markers, abstract/final/static/synchronized attributes, and embedded Javadocs.

## Purpose

The `Shell` portion documents Hadoop's portable command-execution base class and OS/platform constants. It supports subprocess execution, environment and working-directory injection, timeout tracking, Windows-specific `winutils` discovery, bash support checks, and static convenience command execution.

The `org.apache.hadoop.util` portion documents common runtime support APIs. `StringInterner` provides strong and weak string interning without relying on JVM permanent-generation behavior. `SysInfo` abstracts host resource metrics for schedulers and monitoring code. `Tool` and `ToolRunner` define Hadoop's command-line application contract and generic-option parsing flow. `VersionInfo` exposes build metadata for Hadoop components.

The `org.apache.hadoop.util.bloom` portion documents probabilistic membership data structures used where compact set summaries are useful. It includes basic Bloom filters, counting filters with deletion and approximate counts, dynamic filters that grow by adding rows, retouched filters that trade selected false positives for possible false negatives, hash projection helpers, and retouching scheme constants.

## Important APIs, Types, and Functions

### Shell Tail

- `Shell.checkIsBashSupported()` returns a boolean and can throw `InterruptedIOException`, making bash availability a probed platform feature rather than an assumed constant.
- Protected mutators `setEnvironment(Map)` and `setWorkingDirectory(File)` configure the next command invocation context.
- Protected `run()` executes the command when interval gating permits. Subclasses provide the command via abstract `getExecString()` and parse stdout through abstract `parseExecResult(BufferedReader)`.
- Runtime inspection methods include `getEnvironment(String)`, `getProcess()`, `getExitCode()`, and `isTimedOut()`.
- Static `execCommand(...)` overloads execute simple command arrays with optional environment and timeout, returning command output as `String` and throwing `IOException` on failures.
- Public constants and fields expose platform and shell behavior: `SYSPROP_HADOOP_HOME_DIR`, `ENV_HADOOP_HOME`, `WINDOWS_MAX_SHELL_LENGTH`, deprecated misspelling `WINDOWS_MAX_SHELL_LENGHT`, `USER_NAME_COMMAND`, `WindowsProcessLaunchLock`, `osType`, OS booleans (`WINDOWS`, `SOLARIS`, `MAC`, `FREEBSD`, `LINUX`, `OTHER`), `PPC_64`, environment-name regex, Unix command names for permission/owner/group/link/readlink, `WINUTILS`, `isSetsidAvailable`, and `TOKEN_SEPARATOR_REGEX`.
- Instance state exposed as protected fields includes `timeOutInterval` and `inheritParentEnv`.

### Common Util Classes

- `StringInterner.strongIntern(String)` returns an equal representative string held by a strong reference. `weakIntern(String)` does the same while allowing garbage collection when no strong references remain.
- `SysInfo.newInstance()` returns the default OS-specific implementation or throws `UnsupportedOperationException` if the OS cannot be determined.
- `SysInfo` declares abstract metrics for total and available virtual/physical memory, logical processors, physical cores, CPU frequency, cumulative CPU time, CPU usage percentage, vcores used, aggregate network bytes read/written, and aggregate storage bytes read/written.
- `Tool` extends `Configurable` and defines `run(String[] args) throws Exception` returning a process-style exit code. Its Javadoc establishes the convention that generic Hadoop options should be delegated to `ToolRunner`, while tool-specific args are handled by the implementation.
- `ToolRunner.run(Configuration, Tool, String[])` parses generic arguments, sets the possibly modified `Configuration` on the `Tool`, and invokes `Tool.run`. `ToolRunner.run(Tool, String[])` delegates through the tool's own configuration.
- `ToolRunner.printGenericCommandUsage(PrintStream)` emits generic option help, and `ToolRunner.confirmPrompt(String)` returns true for case-insensitive `y`/`yes` user responses.
- `VersionInfo` has a protected component-name constructor plus protected instance getters such as `_getVersion`, `_getRevision`, `_getBranch`, `_getDate`, `_getUser`, `_getUrl`, `_getSrcChecksum`, `_getBuildVersion`, and `_getProtocVersion`.
- Static `VersionInfo` accessors expose Hadoop version, Git revision, branch, compile date, build user, source URL, source checksum, composite build version, protoc version, and a `main(String[])` reporting entry point.

### Bloom Filter APIs

- `BloomFilter` extends `Filter`. It has a zero-arg deserialization constructor and `(int vectorSize, int nbHash, int hashType)` constructor. Methods include `add(Key)`, boolean `membershipTest(Key)`, logical operations `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, `toString()`, `getVectorSize()`, and `Writable`-style `write(DataOutput)`/`readFields(DataInput)`.
- `CountingBloomFilter` is `final` and extends `Filter`. It adds `delete(Key)` and `approximateCount(Key)` to the normal filter operations. The Javadocs warn that repeated insertion of the same key more than 15 times can overflow all associated buckets and significantly raise error rates.
- `DynamicBloomFilter` extends `Filter` and adds a constructor `(int vectorSize, int nbHash, int hashType, int nr)`, where `nr` is the per-row threshold for recorded keys. It exposes the same add, membership, logical-operation, string, and serialization methods as the base Bloom filter contract.
- `HashFunction` is `final` and maps a `Key` into multiple integer positions. Its constructor binds `maxValue`, `nbHash`, and `hashType`; `hash(Key)` returns the generated positions; `clear()` is documented as a no-op.
- `RemoveScheme` is a constants interface for retouched Bloom filters. It defines `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO` selection schemes.
- `RetouchedBloomFilter` is `final`, extends `BloomFilter`, and implements `RemoveScheme`. It can record known false positives through overloads accepting one `Key`, a `Collection`, a `List`, or a `Key[]`; `selectiveClearing(Key, short)` applies one of the removal schemes; it also preserves `write`/`readFields` serialization hooks.

## Control Flow

The XML itself has no executable runtime flow, but the APIs imply several operational paths:

- Shell subclasses configure environment and working directory, call `run()`, provide the command vector through `getExecString()`, then parse process output through `parseExecResult(BufferedReader)`. Static `execCommand` bypasses subclassing for simple command execution.
- Shell platform flow first detects OS type and derived booleans, then selects platform-specific helpers such as `winutils`, bash checks, `setsid`, or Unix command names. Windows process launch is guarded by a public synchronization object.
- Tool execution flows through `ToolRunner`: generic options are parsed into a `Configuration`, the tool receives that configuration through `Configurable`, and application-specific arguments are passed to `Tool.run`.
- Prompt confirmation is synchronous and user-input driven; `confirmPrompt` writes a prompt and treats only `y` or `yes` as affirmative.
- Version reporting reads build metadata for the component represented by the `VersionInfo` instance or static Hadoop-common singleton and exposes it through static getters or `main`.
- `SysInfo` clients call `newInstance()` to get the OS implementation, then poll resource counters and capacities. Implementations are expected to return `-1` for unavailable CPU usage and vcore metrics where documented.
- Bloom filter construction configures vector size, hash count, and hash implementation. `add(Key)` hashes a key to positions and mutates filter state; `membershipTest(Key)` hashes the same key and tests the relevant vector/counter state; logical operations combine compatible filters.
- Counting filter deletion first relies on membership semantics; the documented invariant says deletion is a no-op if the key does not belong to the filter.
- Dynamic Bloom filters route insertion into an active row when the row cardinality threshold has not been reached, otherwise they create a new row and insert there. Membership succeeds if any row contains all positions for the key.
- Retouched Bloom filter flow records false-positive keys, then `selectiveClearing` chooses a bit to reset according to the requested `RemoveScheme`, reducing selected false positives while possibly creating false negatives.

## State and Persistence Behavior

This JDiff XML persists API metadata for release compatibility checks. It does not itself store Hadoop runtime state.

`Shell` carries mutable per-instance execution state such as command environment, working directory, timeout interval, parent-environment inheritance, current `Process`, exit code, and timeout status. Its static fields cache platform detection, command names, `winutils` discovery, and bash/setsid capabilities. These are process-local, not durable state, but changing them or their interpretation affects every Hadoop component that shells out.

`StringInterner` maintains representative string instances. Strong interning intentionally retains strings for the life of the interner cache, while weak interning allows collection. The state is memory-resident and can affect heap retention and object identity assumptions, though equality semantics remain string equality.

`SysInfo` is a polling abstraction over operating-system counters. The metrics are host-state snapshots, not persisted application data, and their monotonicity differs by metric: cumulative CPU time and byte counters are expected to increase, while available memory and utilization percentages vary over time.

`ToolRunner` mutates the `Tool` configuration before calling `run`, so generic command-line options become part of the tool's in-memory `Configuration`. Tool implementations may persist that configuration or use it to create files/jobs, but persistence is outside this API.

`VersionInfo` exposes build-time metadata embedded in Hadoop artifacts. The public API treats version, revision, branch, date, user, URL, checksum, and protoc version as immutable build facts.

Bloom filter classes have explicit persistence through `write(DataOutput)` and `readFields(DataInput)`. Their durable state includes vector size, hash count/type through the inherited `Filter` contract, and implementation-specific vectors/counters/rows/false-positive metadata. Compatibility depends on preserving serialized layout and the hash behavior used to map keys to positions.

`CountingBloomFilter` stores bounded counters rather than bits; the Javadocs imply small counter buckets with overflow risk above 15 additions of the same key. `DynamicBloomFilter` persists multiple rows and per-row occupancy thresholds. `RetouchedBloomFilter` persists normal Bloom vector state plus false-positive tracking needed for selective clearing.

## Dependencies and Integration Points

This slice integrates with Java `File`, `Process`, `BufferedReader`, `InterruptedIOException`, `IOException`, `FileNotFoundException`, `DataInput`, `DataOutput`, `PrintStream`, collections, and primitive arrays/strings.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration` and `Configurable` for `Tool`/`ToolRunner` generic option handling and tool configuration propagation.
- `org.apache.hadoop.util.GenericOptionsParser`, referenced by `Tool` and `ToolRunner` docs as the parser for Hadoop generic command-line options.
- `org.apache.hadoop.util.Shell.OSType`, referenced by the `Shell.osType` field.
- `org.apache.hadoop.util.bloom.Filter` and `Key`, which provide the base filter contract and key representation consumed by all Bloom filter variants in this chunk.
- `org.apache.hadoop.util.hash.Hash`, referenced by Bloom constructors and `HashFunction` as the source of hash implementation type constants.
- Hadoop serialization conventions through `write(DataOutput)` and `readFields(DataInput)`, aligning Bloom filters with `Writable`-style persistence even though the inherited interface is outside this chunk.
- SLF4J through `Shell.LOG`.

At the package level, `org.apache.hadoop.util` is documented as common utilities. `org.apache.hadoop.util.bloom` integrates probabilistic set summaries with Hadoop's serialization and hash utilities. The empty `curator` and `hash` package elements indicate package presence in the JDiff document, but their public types are outside this line range or absent from the generated API.

## Risks and Edge Cases

- This chunk begins mid-class inside `Shell`; earlier constructors, helper methods, nested enums/classes, and fields must be merged from the previous chunk before making a complete `Shell` report.
- JDiff exposes signatures and Javadocs only. Exact subprocess handling, stream draining, timeout enforcement, environment merging, command quoting, and error-message behavior require implementation-source validation.
- `Shell.WINUTILS` is deprecated because it can be null. Callers that use the field without null checks can fail late; the Javadocs prefer exception-raising getters such as `getWinUtilsPath()` or `getWinUtilsFile()`.
- The misspelled `WINDOWS_MAX_SHELL_LENGHT` remains public and deprecated for compatibility. Removing it would break consumers compiled against the older typo.
- Static shell execution accepts command arrays and optional environment maps. Callers still need to avoid untrusted command construction, platform-specific quoting assumptions, and commands that can hang beyond intended timeouts.
- `WindowsProcessLaunchLock` exposes a global synchronization point. Incorrect use by external callers can serialize or block unrelated process launches.
- `Tool.run` throws broad `Exception`, so callers need clear exit-code and exception policy. Tools that parse generic options themselves can diverge from Hadoop CLI conventions.
- `ToolRunner.confirmPrompt` is unsuitable for noninteractive automation unless stdin behavior is controlled.
- `SysInfo.newInstance()` can throw `UnsupportedOperationException`, and some metrics are documented to return unavailable sentinel values. Schedulers or monitors must handle missing platform support.
- `StringInterner.strongIntern` can retain unbounded distinct strings if applied to high-cardinality or attacker-controlled input.
- Bloom filters inherently permit false positives. Counting filter deletion can create underflow-related false negatives, and `approximateCount` may undercount after underflow or overcount due to collisions.
- `CountingBloomFilter` has documented overflow risk when adding the same key more than 15 times, which can raise error rates for both that key and other keys.
- Logical operations (`and`, `or`, `xor`, `not`) are only meaningful for compatible filters with matching vector sizes, hash counts, and hash types; this compatibility requirement is implied by Bloom filter algebra but not fully spelled out in this slice.
- `DynamicBloomFilter` grows by adding rows, so memory and serialized size scale with insert volume. Poor `nr` sizing can trade lower false-positive rate for unexpectedly large state.
- `RetouchedBloomFilter.selectiveClearing` deliberately introduces possible false negatives. It must not be used where Bloom filters are relied on for the standard "no false negatives" guarantee.
- The `RemoveScheme.RATIO` documentation contains a typo ("false positve"), but the constant name is the compatibility-relevant API.

## Test Signals

Useful validation for this API surface should include:

- Shell tests for environment injection, parent-environment inheritance, working-directory selection, interval-gated `run`, timeout marking, exit-code capture, process exposure, stdout parsing delegation, and `IOException` propagation.
- Platform tests for OS-type detection, Windows command-length constants including deprecated typo compatibility, `winutils` absent/present behavior, bash support checks, `setsid` availability, and token-separator parsing.
- Static command tests for `execCommand` overloads with and without environment maps and timeouts, including nonzero exits, stderr handling, interrupted timeouts, and large output.
- `StringInterner` tests for equality and identity reuse, null behavior if supported by implementation, weak-entry reclamation expectations, and strong-cache retention behavior under repeated equal/different strings.
- `SysInfo` tests for OS-specific `newInstance` selection, unsupported OS failure, nonnegative memory/core/frequency counters where available, `-1` unavailable CPU/vcore sentinels, and monotonic cumulative byte/CPU counters.
- `Tool`/`ToolRunner` tests for generic option parsing into `Configuration`, setting the modified configuration on the tool, pass-through of tool-specific args, null configuration handling, exit-code propagation, exception propagation, usage printing, and prompt yes/no parsing.
- `VersionInfo` tests for static getter non-null values, build-version composition, protoc-version exposure, component-specific protected getter behavior through a test subclass, and `main` output stability.
- Bloom filter tests for add/membership round trips, known false-positive tolerance, no false negatives for plain Bloom filters, vector-size reporting, string rendering, and serialized round trips through `write`/`readFields`.
- Counting Bloom filter tests for delete no-op on absent keys, delete lowering membership/count for present keys, approximate count under collisions, repeated-add overflow behavior above 15, and underflow/false-negative behavior after excessive deletes.
- Dynamic Bloom filter tests for row creation at the `nr` threshold, membership across multiple rows, serialization preserving all rows, and logical operations across compatible dynamic filters.
- `HashFunction` tests for deterministic positions, number of returned hashes, bounds under `maxValue`, behavior for different hash types, and `clear()` being a no-op.
- Retouched Bloom filter tests for false-positive registration overloads (`Key`, `Collection`, `List`, `Key[]`), null false-positive no-op behavior, each `RemoveScheme` choice, selective-clearing reduction of targeted false positives, expected false-negative tradeoff, and serialization preserving retouched state.
- Compatibility tests should include golden serialized bytes for Bloom filter variants and API checks ensuring deprecated public fields such as `WINUTILS` and `WINDOWS_MAX_SHELL_LENGHT` remain present.

## Cross-Chunk Notes

The previous chunk is required to complete `org.apache.hadoop.util.Shell`; this chunk starts after a method that returns the `winutils` file and only includes the later shell methods and fields. This chunk reaches the end of the 2.8.2 JDiff XML API document, so there is no later chunk for this source file after the empty `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` package markers.
