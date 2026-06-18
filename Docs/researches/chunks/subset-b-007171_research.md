# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 36790-37921

## Scope

This chunk is a JDiff API snapshot segment from Apache Hadoop Common 2.8.0. It starts in the tail of `org.apache.hadoop.util.Shell`, covers all visible APIs for `StringInterner`, `SysInfo`, `Tool`, `ToolRunner`, and the public `org.apache.hadoop.util.bloom` classes in this file, then ends with empty package stubs for `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash`.

The source is generated compatibility metadata, not implementation code. The useful research surface is therefore the public/protected API contract: type names, inheritance, implemented interfaces, constructors, method signatures, parameters, return types, checked exceptions, static/final/synchronized/abstract flags, deprecation text, fields, and Javadocs.

## Purpose

The `Shell` tail exposes Hadoop's cross-platform shell execution constants and state fields. These constants encode operating-system detection, command names used by file-permission/link utilities, Windows process-launch constraints, Hadoop home/winutils discovery, and shell-output parsing conventions used by callers that invoke native commands.

`StringInterner` provides Hadoop-local string canonicalization with strong and weak retention modes. It exists as a performance/memory-management alternative to `String.intern()`, especially for large Hadoop processes that repeatedly store equal strings.

`SysInfo` defines an abstract system-resource metrics plugin. It presents a platform-neutral contract for memory, CPU, vcore, network, and storage counters, with `newInstance()` selecting an OS-specific implementation or throwing when the platform cannot be determined.

`Tool` and `ToolRunner` define the standard Hadoop command-line application pattern. A `Tool` receives generic Hadoop options through `Configuration` handling and then runs application-specific arguments. `ToolRunner` wires `GenericOptionsParser`, configuration mutation, generic usage output, and yes/no prompting around the application `run` method.

The `org.apache.hadoop.util.bloom` package exposes probabilistic set-membership data structures: standard, counting, dynamic, and retouched Bloom filters, plus the hash adapter and removal-scheme constants used by retouched filters. These APIs are compact serialization-aware utilities for approximate membership tests and related network/cache protocols.

## Important APIs, Types, and Functions

### `org.apache.hadoop.util.Shell` Tail

- `WINDOWS_MAX_SHELL_LENGTH` is a public static final `int` documenting the Windows maximum command-line length from KB830473.
- `WINDOWS_MAX_SHELL_LENGHT` is the deprecated misspelled alias. The deprecation explicitly directs callers to `WINDOWS_MAX_SHELL_LENGTH`, so binary compatibility with older callers is intentionally retained.
- `USER_NAME_COMMAND`, `SET_PERMISSION_COMMAND`, `SET_OWNER_COMMAND`, `SET_GROUP_COMMAND`, `LINK_COMMAND`, and `READ_LINK_COMMAND` are public static final command-name strings used by shell-backed user, permission, ownership, group, hard/symbolic link, and readlink operations.
- `WindowsProcessLaunchLock` is a public static final `Object` used as a synchronization object for Windows `CreateProcess` launches.
- `osType` exposes the parsed `Shell.OSType`, and boolean platform flags `WINDOWS`, `SOLARIS`, `MAC`, `FREEBSD`, `LINUX`, `OTHER`, and `PPC_64` expose common branch predicates.
- `ENV_NAME_REGEX` documents the accepted environment-variable name pattern. `TOKEN_SEPARATOR_REGEX` documents the token separator used to parse shell-tool output.
- Protected instance fields `timeOutInterval` and `inheritParentEnv` carry per-shell execution policy: timeout duration and whether child processes inherit parent environment variables.
- `WINUTILS` is a deprecated nullable `String` path to `winutils`; the Javadoc warns callers must check for null and directs new callers to exception-raising getters such as `getWinUtilsPath()` and `getWinUtilsFile()`.
- `isSetsidAvailable` advertises whether `setsid` exists on the current platform.

### `StringInterner`

- Public constructor `StringInterner()` is visible, though the useful operations are static.
- `strongIntern(String sample)` returns the canonical equal string while retaining a strong reference, preventing garbage collection of the representative instance.
- `weakIntern(String sample)` returns the canonical equal string while retaining only a weak reference, allowing the representative instance to be garbage-collected.
- Class Javadoc positions this as equivalent in behavior to `String.intern()` while avoiding permanent-generation memory pressure.

### `SysInfo`

- `SysInfo` is an abstract public base class with a public constructor.
- `newInstance()` returns the default OS implementation and may throw `UnsupportedOperationException` when the OS cannot be determined.
- Abstract memory methods return byte counts: `getVirtualMemorySize()`, `getPhysicalMemorySize()`, `getAvailableVirtualMemorySize()`, and `getAvailablePhysicalMemorySize()`.
- Abstract CPU methods return processor and usage information: `getNumProcessors()`, `getNumCores()`, `getCpuFrequency()` in kHz, `getCumulativeCpuTime()` in milliseconds, `getCpuUsagePercentage()` from 0 to 100 or `-1` unavailable, and `getNumVCoresUsed()` from 0 to number of vcores or `-1` unavailable.
- Abstract I/O counter methods return aggregate byte counters: `getNetworkBytesRead()`, `getNetworkBytesWritten()`, `getStorageBytesRead()`, and `getStorageBytesWritten()`.

### `Tool`

- `Tool` is a public interface extending `org.apache.hadoop.conf.Configurable`.
- `run(String[] args)` returns an integer exit code and throws generic `Exception`.
- Javadocs define the intended pattern: delegate generic Hadoop command-line options to `ToolRunner`, read the processed `Configuration` from `getConf()`, then process only custom arguments in the tool implementation.
- The example references MapReduce types such as `JobConf`, `JobClient`, `RunningJob`, mapper/reducer classes, and `Path`, but those are documentation examples rather than signatures in this chunk.

### `ToolRunner`

- Public constructor `ToolRunner()` is visible.
- `run(Configuration conf, Tool tool, String[] args)` parses generic Hadoop arguments, sets the tool's possibly modified configuration, then calls `Tool.run(String[])` and returns that exit code.
- `run(Tool tool, String[] args)` delegates to the configuration-bearing overload using `tool.getConf()`.
- `printGenericCommandUsage(PrintStream out)` writes usage text for generic Hadoop options.
- `confirmPrompt(String prompt)` prints a prompt and returns true only for case-insensitive `y` or `yes`; it throws `IOException`.
- Class Javadoc identifies `GenericOptionsParser` as the parser integration and says application-specific options are passed through unmodified.

### `BloomFilter`

- `BloomFilter` extends `Filter` and is public, non-final, and concrete.
- Constructors include a default constructor for `readFields` and `BloomFilter(int vectorSize, int nbHash, int hashType)`.
- Mutating and query APIs include `add(Key)`, `membershipTest(Key)`, boolean-vector operations `and(Filter)`, `or(Filter)`, `xor(Filter)`, complement `not()`, `toString()`, and `getVectorSize()`.
- Serialization APIs are `write(DataOutput)` and `readFields(DataInput)`, both throwing `IOException`.
- Javadocs define standard Bloom-filter semantics: compact set-membership representation, linear construction cost, false positives possible, and false negatives not expected for normal add-only use.

### `CountingBloomFilter`

- `CountingBloomFilter` extends `Filter` and is public final.
- Constructors mirror `BloomFilter`: default for deserialization and `CountingBloomFilter(int vectorSize, int nbHash, int hashType)`.
- It supports `add(Key)`, `delete(Key)`, `membershipTest(Key)`, `approximateCount(Key)`, boolean-vector operations `and(Filter)`, `or(Filter)`, `xor(Filter)`, complement `not()`, `toString()`, and writable serialization with `write`/`readFields`.
- `delete(Key)` documents an invariant: if the key does not belong to the filter, nothing happens.
- `approximateCount(Key)` estimates how many times a key was added. The Javadoc warns that inserting the same key more than 15 times overflows all associated filter positions and increases error rates. It can return zero for absent keys, the true count with probability tied to the error rate, a higher count due to collisions, or a lower count if underflow occurred after deletes.

### `DynamicBloomFilter`

- `DynamicBloomFilter` extends `Filter` and is public concrete.
- Constructors include a zero-argument serialization constructor and `DynamicBloomFilter(int vectorSize, int nbHash, int hashType, int nr)`, where `nr` is the maximum number of keys per row.
- APIs include `add(Key)`, `membershipTest(Key)`, `and(Filter)`, `or(Filter)`, `xor(Filter)`, `not()`, `toString()`, `write(DataOutput)`, and `readFields(DataInput)`.
- Javadocs describe a matrix of standard Bloom-filter rows. When the active row reaches its key threshold, adding another key creates a new row. Membership is true when all hash positions are set in any row.

### `HashFunction`

- `HashFunction` is public final and constructs a multi-output hash adapter.
- Constructor `HashFunction(int maxValue, int nbHash, int hashType)` bounds returned hash values and selects the underlying hash algorithm type from `org.apache.hadoop.util.hash.Hash`.
- `hash(Key)` returns an `int[]` of hash positions for a key.
- `clear()` is explicitly documented as a no-op.

### `RemoveScheme`

- `RemoveScheme` is a public interface used by retouched Bloom filters.
- Constants are public static final `short` values:
  - `RANDOM`: randomly select a bit to reset.
  - `MINIMUM_FN`: select the reset bit expected to generate the minimum number of false negatives.
  - `MAXIMUM_FP`: select the reset bit expected to remove the maximum number of false positives.
  - `RATIO`: select a bit balancing maximum false-positive removal with minimum false-negative introduction.

### `RetouchedBloomFilter`

- `RetouchedBloomFilter` extends `BloomFilter`, implements `RemoveScheme`, and is public final.
- Constructors include a default `readFields` constructor and `RetouchedBloomFilter(int vectorSize, int nbHash, int hashType)`.
- It exposes `add(Key)` plus several overloads of `addFalsePositive`: one `Key`, `Collection`, `List`, and `Key[]`.
- `addFalsePositive(Key)` documents a null invariant: null false-positive information is ignored.
- `selectiveClearing(Key k, short scheme)` applies one of the `RemoveScheme` strategies to remove a false-positive key from the filter.
- It serializes with `write(DataOutput)` and `readFields(DataInput)`, both throwing `IOException`.
- Class Javadoc defines the retouched-filter tradeoff: remove selected false positives while introducing random false negatives and eliminating some other false positives.

### Empty Packages

- `org.apache.hadoop.util.curator` and `org.apache.hadoop.util.hash` appear as empty package elements at the end of the chunk. The `hash` package is still referenced by Bloom filter constructors through `org.apache.hadoop.util.hash.Hash`, but this particular XML slice does not expose hash package members.

## Control Flow

The XML itself has no executable control flow. The exposed contracts imply several runtime flows:

- Shell-backed operations branch on static platform detection (`osType`, `WINDOWS`, `LINUX`, and peers), choose platform-specific commands or winutils paths, optionally synchronize Windows process creation on `WindowsProcessLaunchLock`, apply timeout and environment inheritance policy from each `Shell` instance, and parse results using token separators.
- String interning is lookup-oriented: callers provide a sample string, the interner checks an equal representative, returns the representative, and either retains it strongly or weakly depending on the selected API.
- `SysInfo.newInstance()` chooses a platform plugin, after which resource consumers poll abstract methods for point-in-time or cumulative metrics. Missing CPU/vcore usage can be represented by `-1` instead of an exception.
- `ToolRunner.run(conf, tool, args)` constructs or uses a `Configuration`, runs generic option parsing, mutates the configuration visible to the tool, calls `tool.setConf(...)`, then invokes `tool.run(...)`. `run(tool, args)` is a convenience path through `tool.getConf()`.
- `confirmPrompt` is synchronous user interaction: print prompt, read input, normalize case, and return true for affirmative `y`/`yes`.
- Basic Bloom-filter flow hashes a `Key` into several positions, sets positions on `add`, checks all positions on `membershipTest`, and combines compatible filters with boolean operations.
- Counting Bloom-filter flow replaces bits with counters. `add` increments hashed buckets, `delete` decrements only when the key is considered present, and `approximateCount` computes the lower observed counter bound while accepting collision and underflow error.
- Dynamic Bloom-filter flow searches for an active row below the `nr` threshold during `add`; if no active row exists, it allocates another Bloom-filter row and inserts there. Membership checks all rows.
- Retouched Bloom-filter flow records known false positives, then `selectiveClearing` chooses a bit to clear according to `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, or `RATIO`.
- Writable flow for Bloom filters is explicit and mutable: default constructors create empty shells for deserialization, then `readFields(DataInput)` populates state; `write(DataOutput)` emits the current state.

## State and Persistence Behavior

The JDiff file persists public API metadata for compatibility checking across Hadoop releases. It does not persist runtime application state.

The `Shell` fields represent a mixture of immutable static process state and mutable per-instance policy. Platform flags, command constants, winutils discovery, setsid availability, and token regexes are global API state. `timeOutInterval` and `inheritParentEnv` are protected mutable instance fields that subclasses and shell runners can use to govern child-process behavior.

`StringInterner` state is a process-local canonicalization cache. Strong interning deliberately keeps representative strings alive for the life of the backing cache, while weak interning allows representatives to disappear when no other references remain. Neither form is a durable persistence mechanism.

`SysInfo` represents live system state rather than durable state. Memory and usage values are snapshots; CPU time and byte counters are cumulative counters since system or interface start, depending on the platform implementation. The abstract contract must tolerate unavailable usage by returning `-1` for selected methods.

`Tool` state is carried mainly through the inherited `Configurable` contract. `ToolRunner` mutates and injects the `Configuration`, so command-line parsing can affect downstream filesystem, security, MapReduce, and application settings before `run` executes.

Bloom-filter classes are persistence-sensitive because they implement Hadoop writable-style serialization. Persisted state includes vector size, hash count, hash algorithm type, bit/counter/matrix contents, dynamic row counts and thresholds, and retouched false-positive bookkeeping. Default constructors explicitly exist to support `readFields`, so deserialization relies on mutable instances.

Approximate structures carry probabilistic state. Bloom filters persist compact membership approximations, not original key sets. Counting filters persist counters but can overflow at repeated counts above the documented small-count range. Retouched filters intentionally trade selected false-positive removal for possible false negatives, so persisted cleared bits affect future membership results.

## Dependencies and Integration Points

This chunk integrates with Java runtime APIs including `String`, `Object`, arrays, primitive numeric types, `java.io.DataInput`, `java.io.DataOutput`, `java.io.IOException`, `java.io.PrintStream`, and Java collections (`Collection`, `List`).

Hadoop integration points include:

- `org.apache.hadoop.conf.Configurable` and `Configuration` for the `Tool`/`ToolRunner` command-line contract.
- `GenericOptionsParser`, referenced by `Tool` and `ToolRunner` Javadocs, as the parser for generic Hadoop options.
- `org.apache.hadoop.util.Shell.OSType` and OS-specific native-command facilities for shell execution.
- Hadoop's Windows support and `winutils`, with the deprecated nullable `WINUTILS` field replaced by exception-raising getter methods outside this chunk.
- `org.apache.hadoop.util.bloom.Filter` and `Key`, which are base abstractions for every Bloom-filter implementation in this slice.
- `org.apache.hadoop.util.hash.Hash`, referenced by hash-type parameters and `HashFunction`, even though the package body is empty in this exact range.
- Hadoop `Writable` conventions through `write(DataOutput)` and `readFields(DataInput)`.

Operational integration points are broad. Shell constants are used by filesystem and utility code that shells out for permission, ownership, group, link, username, `setsid`, and Windows process behavior. `SysInfo` feeds resource monitoring and scheduler-style decisions. `Tool` and `ToolRunner` are the common entrypoint pattern for Hadoop CLI tools. Bloom filters can integrate with caches, map files, network membership summaries, or any code needing compact approximate membership checks.

## Risks and Edge Cases

- This chunk starts mid-`Shell`; method contracts such as actual command execution and winutils getter signatures are outside the assigned line range. Final file-level research must reconcile adjacent chunks before making complete claims about `Shell`.
- JDiff exposes signatures and Javadocs, not implementation bodies. Exact synchronization, validation, serialization layout, hash mixing, and exception messages require source-code validation beyond this XML.
- `WINDOWS_MAX_SHELL_LENGHT` is intentionally misspelled and deprecated. Removing it would break older compiled callers even though the correctly spelled constant exists.
- `WINUTILS` is nullable and deprecated because missed null checks caused support issues. Callers still using it can fail later with null dereferences or unclear Windows errors.
- Public static platform booleans are process-global snapshots; tests or code that expect them to change after `os.name` mutation will be fragile.
- Shell command constants encode platform assumptions. Missing native commands, different command output formats, environment variable parsing differences, or Windows command-line length limits can break callers.
- `WindowsProcessLaunchLock` being public exposes an internal synchronization object. External misuse could introduce lock contention or deadlock with process launches.
- Strong string interning can become a memory leak when applied to high-cardinality or unbounded input. Weak interning avoids that retention but cannot promise long-lived identity stability after garbage collection.
- `SysInfo` values are platform dependent and may be unavailable, stale, permission-limited, or differently scoped in containers. Callers must handle `-1` usage values and `UnsupportedOperationException` from `newInstance()`.
- `ToolRunner.run(Tool, String[])` depends on `tool.getConf()`. Tools with null or mutable shared configurations need predictable initialization.
- `Tool.run` can throw generic `Exception`, so command wrappers need consistent exit-code mapping and logging policies.
- `confirmPrompt` is interactive and can block automation if used in non-interactive contexts.
- Bloom filters have false positives by design. Counting filters add deletion support but introduce overflow and underflow risks. Retouched filters can introduce false negatives intentionally. Dynamic filters grow row state, so serialized size and query cost can increase as more keys are added.
- Boolean operations on filters require compatible vector sizes, hash counts, and hash types. The XML does not show validation details, so misuse may surface as runtime exceptions or invalid probabilistic results.
- `HashFunction.clear()` is a no-op; callers expecting it to reset hidden state will be disappointed.

## Test Signals

Useful validation around this API slice should include:

- JDiff or compatibility tests that verify public fields, deprecated aliases, constructors, method signatures, checked exceptions, and inheritance remain stable for Hadoop Common 2.8.0.
- Cross-platform `Shell` tests for OS detection flags, Windows command-length behavior, `WINUTILS` null/error paths, `setsid` availability, command constants, environment-name validation, timeout behavior, and parent-environment inheritance.
- Concurrency tests around Windows process launch synchronization if Windows execution paths are exercised.
- `StringInterner` tests for identity canonicalization, null/input edge behavior if defined by implementation, strong retention, and weak-reference cleanup under garbage collection.
- `SysInfo` tests using platform fixtures or mocks for memory sizes, CPU counts, CPU usage unavailable values, cumulative CPU time, and network/storage byte counters. Containerized environments should be covered separately from bare-metal assumptions.
- `ToolRunner` tests for generic option parsing, configuration injection into `Tool`, pass-through of application arguments, null configuration behavior, exit-code propagation, exception propagation, generic usage output, and `confirmPrompt` yes/no parsing.
- Bloom-filter tests for add/query semantics, expected false-positive behavior, no false negatives for standard add-only filters, boolean operations on compatible filters, rejection or failure on incompatible filters, `getVectorSize`, `toString`, and writable round trips.
- Counting Bloom-filter tests for delete invariants, approximate counts, absent keys, repeated insertions near and above the documented 15-count overflow threshold, and underflow behavior after deletes.
- Dynamic Bloom-filter tests for row creation once `nr` is reached, membership across multiple rows, serialization preserving row matrix state, and boolean operations with similarly shaped filters.
- Retouched Bloom-filter tests for false-positive recording overloads, null handling, each `RemoveScheme` strategy, selective clearing effects, introduced false-negative risk, and serialization of retouched state.
