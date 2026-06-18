# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 37165-38826

## Chunk Scope

This chunk is the final slice of the Hadoop 0.18.3 JDiff API XML file. It starts in the closing documentation for `org.apache.hadoop.util.GenericOptionsParser`, then covers the remaining public `org.apache.hadoop.util` API through `XMLUtils`, ending with the closing `</package>` and `</api>` tags.

Because the source is generated JDiff XML rather than implementation code, control-flow, state, persistence, and risk notes are inferred from public signatures, visibility, inheritance, synchronized/static markers, declared exceptions, fields, and embedded API documentation.

## Purpose

The chunk records Hadoop 0.18.3 utility APIs used by command-line entry points, generic option parsing, typed reflection, in-memory sorting, host include/exclude lists, progress tracking, shell command execution, string/byte/time formatting, tool launch wrappers, build version reporting, and XSLT transformation. It is a compatibility surface: downstream consumers can diff method names, overloads, return types, checked exceptions, constants, deprecations, and package placement across Hadoop releases.

The utilities here are mostly framework glue rather than distributed filesystem implementations. They connect Hadoop command-line programs to `Configuration`, provide reusable sort contracts for index-addressed collections, expose small runtime/introspection helpers, and wrap operating-system or JVM services in Hadoop-facing APIs.

## Important APIs and Types

### Generic command-line integration

The chunk begins with the final documentation for `GenericOptionsParser`. The visible docs show the standard command shape:

- `bin/hadoop command [genericOptions] [commandOptions]`
- generic options may mutate `Configuration` objects passed into constructors.
- implementation is based on Commons CLI.
- examples include `dfs -fs`, `dfs -D`, `dfs -conf`, `job -D`, `job -jt`, local job tracker selection, and `jar -libjars -archives -files`.

This ties the later `Tool` and `ToolRunner` APIs to `Configuration` mutation and to common Hadoop launcher behavior.

### `GenericsUtil`

`org.apache.hadoop.util.GenericsUtil` is a public helper for Java generics:

- `getClass(T)` returns a typed `Class<T>` for an object.
- `toArray(Class<T>, List<T>)` converts a list to a typed array using an explicit component class.
- `toArray(List<T>)` converts a non-empty list to a typed array but documents `ArrayIndexOutOfBoundsException` if the list is empty, advising the explicit-class overload for empty lists.

The API exists to work around Java's erased generic array creation limits.

### Sort contracts: `IndexedSortable`, `IndexedSorter`, `HeapSort`, `QuickSort`, and `MergeSort`

`IndexedSortable` is the core collection contract for index-addressed sorting. It exposes:

- `compare(int i, int j)` with `Comparable`-compatible semantics.
- `swap(int i, int j)` to exchange entries at logical indices.

`IndexedSorter` is the algorithm contract:

- `sort(IndexedSortable s, int l, int r)` sorts `[l, r)`.
- `sort(IndexedSortable s, int l, int r, Progressable rep)` performs the same sort while periodically reporting progress.

`HeapSort` is a final public `IndexedSorter` implementation with `sort` overloads. `QuickSort` is also a final public `IndexedSorter`; it exposes protected static `getMaxDepth(int)` returning `2 * ceil(log(n))`, and its docs state that quicksort falls back to `HeapSort` if recursion depth exceeds that bound. `MergeSort` is an older public class constructed with `Comparator<IntWritable>` and exposes `mergeSort(int[] src, int[] dest, int low, int high)`.

The important integration contract is that sort algorithms only call `compare` and `swap`; storage layout stays private to the `IndexedSortable`.

### Host and native/platform helpers

`HostsFileReader` is constructed from include and exclude host file paths and exposes:

- `refresh()` with `IOException`.
- `getHosts()` returning `Set<String>`.
- `getExcludedHosts()` returning `Set<String>`.

This is a lightweight stateful reader for daemon host admission/exclusion lists.

`NativeCodeLoader` exposes:

- static `isNativeCodeLoaded()`.
- `getLoadNativeLibraries(JobConf)`.
- `setLoadNativeLibraries(JobConf, boolean)`.

The docs say it loads native Hadoop code such as `libhadoop.so`, falling back to bundled Linux i386 native code or Java implementations where appropriate. The JobConf accessors gate native-library usage per job.

`PlatformName` exposes static `getPlatformName()` and `main(String[])` for reporting the complete Java VM platform name.

`VersionInfo` exposes build metadata:

- `getVersion()`, `getRevision()`, `getDate()`, `getUser()`, `getUrl()`, and `getBuildVersion()`.
- `main(String[])`.

The docs tie it to package info and `HadoopVersionAnnotation`.

### Jar and program launch helpers

`PrintJarMainClass` is a micro-application with `main(String[])` that prints the main class name from a jar file.

`ProgramDriver` provides a small registry-driven command dispatcher:

- `addClass(String name, Class mainClass, String description)` registers a named program and may throw `Throwable`.
- `driver(String[] args)` reads `args[0]`, finds the named program, and invokes that program's `main` with the remaining arguments. It declares `Throwable` to propagate reflection and target program failures.

`RunJar` is the main Hadoop job-jar launcher utility:

- static `unJar(File jarFile, File toDir)` unpacks a jar and throws `IOException`.
- static `main(String[] args)` runs a Hadoop job jar and throws `Throwable`; docs say the main class may come from the jar manifest or from the command line.

Together these classes provide Hadoop's command-dispatch path from shell commands and jars into Java `main` methods.

### Priority queue

`PriorityQueue` is an abstract public heap-style queue over `Object` values. Subclasses must implement protected abstract `lessThan(Object a, Object b)`. It exposes:

- protected final `initialize(int maxSize)`.
- public final `put(Object)` that adds in logarithmic time and may throw an array bounds runtime failure if over capacity.
- public `insert(Object)` that adds only if the queue is not full or the candidate is not less than the current top.
- public final `top()`, `pop()`, `adjustTop()`, `size()`, and `clear()`.

Docs state the least element is returned in constant time and put/pop are logarithmic. `adjustTop()` is an optimization for cases where the current top object mutates.

### Progress reporting

`Progress` models a tree of execution phases:

- constructor creates a root node.
- `addPhase(String status)` adds a named child.
- synchronized `addPhase()` adds an unnamed child.
- synchronized `startNextPhase()` advances at the current tree level.
- synchronized `phase()` returns the current child node.
- `complete()` completes a node and advances its parent.
- synchronized `set(float)` sets progress on a leaf.
- synchronized `get()` returns overall root progress.
- synchronized `setStatus(String)` updates status.
- `toString()` renders current state.

`Progressable` is the callback interface with `progress()`. Its documentation emphasizes that long operations must report progress so the framework does not assume timeout/failure.

The sort APIs, job output streams, and long-running Hadoop components can use `Progressable` as a common liveness signal.

### Reflection and diagnostics

`ReflectionUtils` provides framework-level object construction and thread diagnostics:

- static `setConf(Object, Configuration)` sets configuration on configurable objects when applicable.
- static `newInstance(Class<?>, Configuration)` creates and configures an object.
- static `setContentionTracing(boolean)` toggles thread contention tracing.
- static `printThreadInfo(PrintWriter, String)` prints thread information and stack traces.
- static `logThreadInfo(Log, String, long)` logs stack traces at INFO no more often than `minInterval`.
- static generic `getClass(T)` returns the correctly typed `Class<T>`.

It depends on `Configuration`, Hadoop `Configurable` behavior by implication, and Commons Logging for logged diagnostics.

### Servlet utilities

`ServletUtil` contains static helpers for Hadoop's web UIs:

- `initHTML(ServletResponse, String)` returns a `PrintWriter` after writing the initial HTML header and can throw `IOException`.
- `getParameter(ServletRequest, String)` returns a request parameter or `null` if it only contains whitespace.
- `htmlFooter()` returns an HTML footer.
- public static final `HTML_TAIL` exposes the footer fragment.

This is JSP/servlet glue rather than storage logic.

### Shell command execution

`Shell` is an abstract base class for running Unix commands, optionally gated by a minimum interval. Public/protected API includes:

- constructors `Shell()` and `Shell(long interval)`.
- static command builders `getGROUPS_COMMAND()`, `getGET_PERMISSION_COMMAND()`, and `getUlimitMemoryCommand(JobConf)`.
- protected `setEnvironment(Map<String,String>)`.
- protected `setWorkingDirectory(File)`.
- protected `run()` which checks whether a command should execute and runs it if needed.
- protected abstract `getExecString()` returning command and arguments.
- protected abstract `parseExecResult(BufferedReader)` for parsing process output.
- public `getProcess()` and `getExitCode()`.
- static `execCommand(String[])` for simple command execution returning output.

Public fields document platform/command integration: `LOG`, `USER_NAME_COMMAND`, `SET_PERMISSION_COMMAND`, `SET_OWNER_COMMAND`, `SET_GROUP_COMMAND`, and `WINDOWS`.

`Shell.ExitCodeException` extends `IOException`, adds an exit code, and exposes `getExitCode()`. `Shell.ShellCommandExecutor` is a concrete nested executor with constructors for command only, command plus working directory, and command plus directory plus environment. It exposes `execute()`, `getOutput()`, and concrete implementations of `getExecString()` and `parseExecResult()`. Its docs say output is stored as-is and should be small.

The `getUlimitMemoryCommand(JobConf)` docs make this class an integration point for MapReduce child process limits, especially Hadoop Pipes and Streaming. It may return `null` on non-Unix platforms or when no limit is specified.

### String, byte, URI, path, and time utilities

`StringUtils` is a broad static utility class with public constants `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`. Methods include:

- `stringifyException(Throwable)` for stack trace strings.
- `simpleHostname(String)` for stripping a domain suffix after the first dot.
- `humanReadableInt(long)` for approximate 1024-based `k`, `m`, and `g` formatting.
- `formatPercent(double done, int digits)`.
- `arrayToString(String[])`.
- `byteToHexString(byte[])` and `hexStringToByte(String)`.
- `uriToString(URI[])`, `stringToURI(String[])`, and `stringToPath(String[])`.
- `formatTimeDiff(long finishTime, long startTime)`.
- `getFormattedTimeWithDiff(DateFormat, long finishTime, long startTime)`.
- `getStrings(String)` and `getStringCollection(String)` for comma-separated values.
- `split(String)` and `split(String, char escapeChar, char separator)`.
- `escapeString(String)` and `escapeString(String, char escapeChar, char charToEscape)`.
- `unEscapeString(String)` and `unEscapeString(String, char escapeChar, char charToEscape)`.
- `getHostname()`.
- `startupShutdownMessage(Class, String[], Log)`.

It integrates with `java.net.URI`, `org.apache.hadoop.fs.Path`, `java.text.DateFormat`, and Commons Logging. The escaping/splitting API is important because comma-separated config values can contain escaped separators.

### Tool and ToolRunner

`Tool` is a public interface extending `org.apache.hadoop.conf.Configurable` and declaring `run(String[] args)` returning an exit code and throwing `Exception`. Its docs define the standard Hadoop application pattern: `ToolRunner` handles generic command-line options and the application handles only custom arguments after `Configuration` has been processed.

`ToolRunner` exposes:

- static `run(Configuration, Tool, String[])`, which parses generic arguments, sets the tool's possibly modified configuration, invokes `Tool.run`, and returns its exit code.
- static `run(Tool, String[])`, equivalent to `run(tool.getConf(), tool, args)`.
- static `printGenericCommandUsage(PrintStream)`.

This is the main public integration between command-line parsing, `Configuration`, and reusable Hadoop application entry points.

### XML transformation

`XMLUtils` exposes static `transform(InputStream styleSheet, InputStream xml, Writer out)`, throwing `TransformerConfigurationException` and `TransformerException`. It wraps JAXP/XSLT transformation for Hadoop callers.

## Control Flow and Behavioral Contracts

The visible control flow is API-level:

- Hadoop command launchers pass raw shell arguments into `GenericOptionsParser` or `ToolRunner`; generic options mutate `Configuration`, and remaining arguments reach the application-specific `Tool.run`.
- `ProgramDriver` dispatches by matching the first command-line token against a registered class and reflectively invoking that class's main method.
- `RunJar` unpacks a jar, determines a main class from manifest or arguments, and invokes it as a Hadoop job entry point.
- Sorting flows through `IndexedSorter.sort`, which manipulates client-owned storage only through `IndexedSortable.compare` and `swap`; `QuickSort` may switch to `HeapSort` after a computed recursion-depth limit.
- Progress flows from long-running algorithms or operations through `Progressable.progress()`, while hierarchical tasks can update a `Progress` tree with phases, leaf percentages, and statuses.
- Reflection-based construction flows through `ReflectionUtils.newInstance`, followed by configuration injection through `setConf`.
- Shell command execution flows through `Shell.run()` or `ShellCommandExecutor.execute()`: compute command array, apply environment/working directory, start a process, parse output, track process and exit code, and surface non-zero exits through an IOException subtype.
- String list parsing flows through escape-aware split/unescape helpers so values containing separator characters can round-trip.
- XML transformation flows from stylesheet input and XML input into a writer via JAXP transformer APIs.

## State and Persistence Behavior

Most classes in this chunk are stateless static helpers, but several maintain process-local state:

- `HostsFileReader` stores include and exclude host sets loaded from configured files; `refresh()` updates that in-memory view and can fail with `IOException`.
- `PriorityQueue` stores a bounded heap of object references after `initialize(maxSize)`. It does not persist contents and depends on subclass ordering.
- `Progress` stores a mutable tree of phases, current child position, leaf progress values, and optional status strings. Several mutators/accessors are synchronized, indicating shared-thread usage.
- `Shell` instances store command execution interval, environment, working directory, current process, and last exit code. `ShellCommandExecutor` additionally stores captured command output.
- `ReflectionUtils.logThreadInfo` has a `minInterval` contract, implying process-level throttling of repeated thread-dump logging.
- `NativeCodeLoader` reflects process-level native library load state while the JobConf accessors persist per-job policy in configuration.
- `VersionInfo` reads build metadata packaged with the Hadoop distribution rather than mutating runtime state.
- `StringUtils` conversion helpers are stateless, but `startupShutdownMessage` emits persistent log records for daemon lifecycle events.
- `XMLUtils.transform` writes transformed XML to the supplied writer but owns no persistent repository state.

No distributed filesystem metadata or durable data layout is defined in this chunk; durable effects are limited to host files read by `HostsFileReader`, shell commands executed by `Shell`, log output, jar extraction by `RunJar.unJar`, and XML output written through `XMLUtils`.

## Dependencies and Integration Points

Key dependencies visible from signatures and docs include:

- Hadoop configuration and MapReduce: `Configuration`, `Configurable`, `JobConf`, `Tool`, `ToolRunner`, `Progressable`, and `Path`.
- Hadoop IO primitives: `IntWritable` in the `MergeSort` comparator signature.
- Java runtime and IO: `Class`, reflection-based main invocation, `File`, `InputStream`, `BufferedReader`, `PrintWriter`, `PrintStream`, `Writer`, `IOException`, `URI`, `DateFormat`, and `Process`.
- Java collections: `List<T>`, `Set<String>`, `Map<String,String>`, `Collection<String>`, and `Comparator`.
- Servlet APIs: `ServletRequest` and `ServletResponse`.
- Logging: `org.apache.commons.logging.Log`.
- XML transformation: `javax.xml.transform.TransformerConfigurationException` and `TransformerException`.
- Commons CLI, mentioned in `GenericOptionsParser` docs.
- Operating-system commands and platform checks in `Shell`, including Unix user/group/permission commands, `ulimit`, and Windows detection.

Integration points are broad: CLI tools use `ToolRunner`; MapReduce streaming or pipes child processes can use `Shell.getUlimitMemoryCommand`; sort-heavy Hadoop internals can provide `IndexedSortable`; daemons can expose progress through `Progress` and `Progressable`; web consoles can use `ServletUtil`; release/version commands can use `VersionInfo`; and build/doc tooling can use `XMLUtils`.

## Risks and Edge Cases

- This chunk is generated API XML, so it does not expose implementation internals such as exact parser options, heap array layout, shell stderr handling, thread-dump throttling storage, or native library load attempts.
- The range starts in the middle of `GenericOptionsParser` documentation, so constructor and method signatures for that class must be reconciled from the previous chunk.
- `GenericsUtil.toArray(List<T>)` is unsafe for empty lists and explicitly documents `ArrayIndexOutOfBoundsException`.
- `PriorityQueue.put(Object)` can exceed `maxSize` and throw a runtime array bounds failure; callers needing bounded top-N behavior should use `insert(Object)`.
- `PriorityQueue.adjustTop()` assumes only the top object changed; using it after changing another element can corrupt ordering.
- `IndexedSortable.compare` must be consistent and `swap` must correctly mutate the backing collection; sort algorithms have no other way to validate storage state.
- `QuickSort` fallback behavior means tests should cover recursion-depth protection, not just average-case sorting.
- `HostsFileReader.refresh()` may observe partially written host files or fail on missing/unreadable paths; exposed getters return sets whose mutability is not documented in the XML.
- `NativeCodeLoader` behavior is platform-sensitive and may silently fall back to Java implementations depending on library availability and job configuration.
- `ProgramDriver.driver` and `RunJar.main` declare `Throwable`, so caller-side error boundaries must handle reflection failures and arbitrary application exceptions.
- `Shell` is platform-sensitive: many constants are Unix commands, while `WINDOWS` and `getUlimitMemoryCommand` indicate different behavior on Windows/Cygwin/non-Unix systems.
- `ShellCommandExecutor` docs expect small output; using it for large command output risks memory pressure.
- `Shell.execCommand` covers simple cases only; callers needing custom parsing, environment, working directory, or interval gating should use subclasses.
- `StringUtils` comma escaping must be used consistently; mixing raw `arrayToString` with escape-aware `split` can corrupt values containing commas or escape characters.
- `hexStringToByte(String)` implies output length is `hex.length()/2`; odd-length or invalid hex input behavior is not visible here.
- `getFormattedTimeWithDiff` returns an empty string for finish time zero and omits differences when start time is zero, which can surprise display code.
- `ToolRunner.run(Tool, String[])` depends on `tool.getConf()`; a tool with null or improperly initialized configuration may differ from `run(Configuration, Tool, String[])`.
- Servlet HTML helpers may produce fixed fragments; escaping behavior for titles and parameters is not visible in the API XML.
- `XMLUtils.transform` exposes raw transformer exceptions; callers must handle stylesheet compilation and runtime transform failures.

## Test Signals

Useful tests inferred from this API slice include:

- `ToolRunner` tests for generic option parsing with `-D`, `-conf`, `-fs`, `-jt`, `-libjars`, `-files`, and `-archives`, verifying configuration mutation and preservation of application arguments.
- `Tool` integration tests that `ToolRunner.run` injects the modified configuration before invoking `run`.
- `GenericsUtil` tests for typed array creation with non-empty lists, empty lists with explicit class, and documented failure for empty implicit-class conversion.
- `IndexedSorter` contract tests for `HeapSort` and `QuickSort` over custom `IndexedSortable` implementations, including empty ranges, singleton ranges, duplicates, reverse order, progress callbacks, and quicksort fallback depth.
- `MergeSort` tests around comparator behavior for `IntWritable`-indexed arrays if this legacy sorter remains used.
- `HostsFileReader` tests for include/exclude parsing, refresh after file changes, missing files, duplicate hosts, whitespace/comments if supported by implementation, and getter isolation from internal mutable sets.
- `NativeCodeLoader` tests for `isNativeCodeLoaded` under absent/present native libraries and JobConf get/set policy round trips.
- `ProgramDriver` tests for successful dispatch, unknown command handling, empty args, argument shifting, duplicate registration, and propagation of target main exceptions.
- `RunJar` tests for manifest main-class discovery, explicit main-class override, jar unpacking, nested resources, missing main class, and cleanup/error behavior.
- `PriorityQueue` tests for capacity, ordering, `insert` rejection when full, `top`, `pop`, `adjustTop`, `clear`, and subclass `lessThan` edge cases.
- `Progress` tests for phase-tree aggregation, synchronized add/start/phase/set/get behavior, status rendering, completion advancing parent nodes, and `toString`.
- `Progressable` timeout/liveness tests in components that accept a progress callback.
- `ReflectionUtils` tests for configuring `Configurable` objects, constructing default constructors, failure on missing constructors, typed class return, thread-info printing, and `logThreadInfo` minimum interval throttling.
- `ServletUtil` tests for HTML header/footer generation and blank-parameter-to-null behavior.
- `Shell` tests for command arrays, environment and working directory application, interval gating, stdout parsing, exit code reporting, non-zero exit exceptions, static `execCommand`, platform command builders, and memory-limit command construction from JobConf.
- `StringUtils` tests for exception stringification, hostname simplification, human-readable integer boundaries, percentage precision, byte/hex round trips, URI/path array conversion, time-diff formatting including zero and negative cases, comma-separated parsing, escaping/unescaping custom separators, hostname fallback, and startup/shutdown log content.
- `VersionInfo` tests for non-empty packaged version, revision/date/user/url/build-version fields and `main` output.
- `XMLUtils` tests for successful XSLT transformation, stylesheet compilation failure, XML transform failure, writer propagation, and stream ownership expectations.

## Chunk Boundary Notes

The previous chunk is required to complete `GenericOptionsParser` signatures and any earlier `org.apache.hadoop.util` classes. This chunk ends the `org.apache.hadoop.util` package and the entire JDiff API file, so final merge should treat `XMLUtils` as complete here and preserve that no later package content follows.
