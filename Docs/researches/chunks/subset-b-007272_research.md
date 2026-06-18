# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 43568-44778

## Scope

This chunk is the closing section of the Hadoop 0.18.1 JDiff API XML for package `org.apache.hadoop.util`. It starts in the tail of `PriorityQueue`, then covers public API metadata for `ProgramDriver`, `Progress`, `Progressable`, `QuickSort`, `ReflectionUtils`, `RunJar`, `ServletUtil`, `Shell` and nested shell helper classes, `StringUtils`, `Tool`, `ToolRunner`, `VersionInfo`, and `XMLUtils`. The file is an API snapshot, so it documents signatures, visibility, exceptions, fields, inheritance, and Javadoc text rather than Java implementation bodies.

## Purpose

The covered APIs form Hadoop's common utility layer around command dispatch, progress reporting, indexed sorting, reflective object construction, jar launching, web UI helpers, operating-system command execution, string and time formatting, generic command-line option integration, build metadata, and XML transformation.

Within the source tree this JDiff XML is used for API comparison and compatibility tracking. The practical behavioral contract described by this chunk is the public Hadoop 0.18.1 utility surface that downstream tools, examples, MapReduce applications, JSPs, and server startup code could compile against.

## Important APIs, Types, and Functions

### `PriorityQueue` tail

The chunk begins with the final `clear()` method and class documentation for `org.apache.hadoop.util.PriorityQueue`. The class maintains a partial ordering so the least element can be found in constant time, while `put()` and `pop()` are logarithmic. Because the start of the class is outside this range, this chunk only establishes the clearing behavior and high-level performance contract.

### Program and progress utilities

- `ProgramDriver` is a registry and dispatcher for executable programs. `addClass(String name, Class mainClass, String description)` registers a named class, and `driver(String[] args)` uses `args[0]` to find a registered program and invoke its `main` method with the remaining arguments. Both methods can throw broad reflection or program exceptions through `Throwable`.
- `Progress` models hierarchical execution phases. A root is created with the public constructor, children are added with `addPhase()` or `addPhase(String status)`, `startNextPhase()` advances among siblings, `phase()` returns the current child, `complete()` advances the parent, `set(float)` records leaf progress, `get()` reports root progress, and `setStatus(String)` attaches status text. Several mutating/read methods are synchronized, indicating intended use from concurrently observed execution paths.
- `Progressable` is a single-method callback interface with `progress()`. Long-running clients call it to tell the Hadoop framework that work is still active and avoid timeout assumptions.

### Sorting and reflection

- `QuickSort` is a final `IndexedSorter` implementation. It sorts an `IndexedSortable` range with `sort(s, p, r)` and has an overload accepting a `Progressable` reporter. The protected static `getMaxDepth(int)` returns `2 * ceil(log(n))`; when recursion depth falls below that limit the algorithm switches to `HeapSort`, making the API an introsort-style quicksort wrapper.
- `ReflectionUtils` centralizes reflective construction and diagnostics. `setConf(Object, Configuration)` injects configuration into configurable objects, `newInstance(Class<?>, Configuration)` creates and configures objects, `setContentionTracing(boolean)` toggles contention diagnostics, `printThreadInfo(PrintWriter, String)` and `logThreadInfo(Log, String, long)` dump thread stacks, and generic `getClass(T)` returns a correctly typed `Class<T>`.

### Launching, servlets, shell, and strings

- `RunJar` provides `unJar(File, File)` and `main(String[])`. It unpacks job jars and runs the main class from the manifest or command line.
- `ServletUtil` exposes `initHTML(ServletResponse, String)`, `getParameter(ServletRequest, String)`, `htmlFooter()`, and public constant `HTML_TAIL`. It standardizes simple servlet/JSP page setup and treats all-whitespace request parameters as absent.
- `Shell` is an abstract base for running Unix commands with optional re-execution throttling. Static helpers expose command arrays for groups and permissions and derive a `ulimit` memory command from a `JobConf`. Subclasses set environment and working directory, implement `getExecString()` and `parseExecResult(BufferedReader)`, and call protected `run()`. Public inspection methods expose the current `Process` and exit code. `execCommand(String[])` is a simple static command execution helper.
- `Shell.ExitCodeException` extends `IOException` with `getExitCode()`, preserving failed process status.
- `Shell.ShellCommandExecutor` is a concrete nested shell runner for fixed commands, optional working directory, and optional environment. `execute()` runs it, `getOutput()` returns captured output, and the Javadoc warns that output is stored as-is and should be small.
- `StringUtils` is a broad static helper class. APIs cover exception stack traces, simple hostnames, human-readable powers-of-1024 integers, percentages, comma-joined arrays, byte/hex conversion, URI and `Path` conversion, elapsed-time formatting, date-plus-duration formatting, comma-separated string collections, escaped splitting, escaping/unescaping separators, hostname lookup without throwing, and startup/shutdown logging. Public constants define comma and escape characters.

### Tooling, version, and XML APIs

- `Tool` extends `Configurable` and defines `run(String[] args): int`. Its Javadoc establishes the Hadoop command-line convention: `ToolRunner` handles generic Hadoop options and the tool handles application-specific options.
- `ToolRunner` provides `run(Configuration, Tool, String[])`, `run(Tool, String[])`, and `printGenericCommandUsage(PrintStream)`. It integrates with `GenericOptionsParser`, mutates or creates the `Configuration`, sets it on the `Tool`, then delegates to `Tool.run`.
- `VersionInfo` exposes static build metadata: Hadoop version, source-control revision, build date, build user, repository URL, combined build version, and a `main(String[])` printer.
- `XMLUtils.transform(InputStream styleSheet, InputStream xml, Writer out)` applies a stylesheet to XML and declares `TransformerConfigurationException` and `TransformerException`.

## Control Flow

`ProgramDriver` flow is registry first, dispatch later: callers register named classes, then `driver()` reads the first command-line token, locates the matching class, and reflectively invokes its `main` entry point. Errors are intentionally not narrowed, because program code and reflection can both fail.

`Progress` flow is tree-shaped. Application code builds phases, descends to the current `phase()`, sets leaf progress, and calls `complete()` or `startNextPhase()` to advance. The root `get()` aggregates subphase state into a single float for reporting.

`QuickSort` flow is range-based sorting over an `IndexedSortable`. It uses quicksort until the maximum recursion depth is exhausted, then falls back to `HeapSort`; the reporter overload allows long sorts to call back through `Progressable`.

`Shell` flow is template-method based. Subclasses provide a command vector and parser, optional environment and working directory are configured on the base, `run()` decides whether the interval allows execution, starts the process, exposes it through `getProcess()`, parses stdout through `parseExecResult()`, and records the exit code. `ShellCommandExecutor` supplies the common parser that captures all output into a string.

`ToolRunner` flow is the standard Hadoop CLI path: parse generic options with a `Configuration`, set the resulting configuration on the `Tool`, call `Tool.run(args)`, and return its integer exit status.

## State and Persistence Behavior

The XML itself is static API metadata and has no runtime state. The described Java APIs, however, imply several stateful components:

- `ProgramDriver` holds an in-memory registry of command names, classes, and descriptions.
- `Progress` holds an in-memory tree of phases, current phase indexes, status strings, and progress floats. Some methods are synchronized, but `complete()` and `toString()` are not marked synchronized in this API snapshot.
- `ReflectionUtils` likely maintains static diagnostic state for contention tracing and last-log throttling, based on the exposed toggles and `logThreadInfo(..., minInterval)`.
- `Shell` instances hold command execution state: environment, working directory, last execution timing, current process, exit code, and parsed output in subclasses. `ShellCommandExecutor` additionally persists captured command output in memory.
- `StringUtils`, `RunJar`, `ServletUtil`, `ToolRunner`, `VersionInfo`, and `XMLUtils` are primarily stateless static helpers, except for interactions with files, servlet responses, logs, configuration objects, and build metadata resources.

Persistent external effects are limited to helper behavior: `RunJar.unJar` writes extracted jar contents to a directory, shell commands may mutate the host depending on the command, servlet utilities write HTTP response content, `startupShutdownMessage` writes logs, and XML transforms write to the supplied `Writer`.

## Dependencies and Integration Points

These APIs sit at the intersection of Hadoop Common, MapReduce, servlet UI code, logging, and Java platform services:

- Hadoop types: `Configuration`, `Configurable`, `JobConf`, `Path`, `IndexedSortable`, `IndexedSorter`, `HeapSort`, `GenericOptionsParser`, `Tool`, and `Progressable`.
- Java platform types: reflection `Class`, `Throwable`, `Process`, `File`, `BufferedReader`, `IOException`, `PrintWriter`, `PrintStream`, `DateFormat`, `URI`, collections, servlet request/response interfaces, and JAXP transformer exceptions.
- External/common libraries: `org.apache.commons.logging.Log`.
- Operational integration: `Shell` assumes Unix-like command semantics for many constants but exposes `WINDOWS` and returns `null` for memory-limit commands on non-Unix/Cygwin/Windows platforms.
- Application integration: MapReduce applications implement `Tool`, delegate generic option handling to `ToolRunner`, report activity through `Progressable`, and may rely on `StringUtils` and `VersionInfo` for diagnostics and UI output.

## Risks and Edge Cases

- `ProgramDriver` exposes `Throwable` from both registration and dispatch. Callers need top-level error handling so one example program does not terminate a larger launcher without diagnostics.
- `Progressable` is a liveness signal. Missing or infrequent `progress()` calls around long operations can still trigger framework timeouts.
- `Progress` synchronization is mixed. The API marks several phase/progress methods synchronized, but not every public method is synchronized, so concurrent status rendering and updates need tests for consistent output.
- `QuickSort` depends on correct `IndexedSortable.compare` and `swap` implementations. Bad comparator ordering can cause incorrect results, while the heap fallback is only useful if the recursion-depth guard is correct.
- `ReflectionUtils.newInstance` relies on accessible no-argument construction and optional configuration injection. Misconfigured classes, security managers, or missing constructors can fail at runtime.
- `RunJar.unJar` is security-sensitive because jar entries can contain unexpected paths. The API snapshot does not show path traversal defenses, so implementation review and tests are important.
- `ServletUtil.initHTML` and `htmlFooter` generate HTML, while `getParameter` only trims whitespace semantics. Callers still need escaping for user-provided values.
- `Shell` is platform-sensitive and command-injection-sensitive. APIs accept raw command arrays, environment maps, and working directories; callers must avoid constructing commands from untrusted strings.
- `ShellCommandExecutor` stores command output in memory and is documented for small output only. Large stdout streams can cause memory pressure.
- `StringUtils.hexStringToByte` depends on even-length, valid hex input; malformed strings should be tested. Escaped split/unescape helpers must handle trailing escape characters, escaped escape characters, and empty tokens.
- `ToolRunner` mutates the `Tool` configuration after parsing generic options. Tools that read configuration in constructors can observe stale values.
- `VersionInfo` depends on build/package metadata being present in the runtime artifact; development or shaded jars may report missing or placeholder values.
- `XMLUtils.transform` surfaces transformer exceptions directly and writes to caller-owned streams, so partial output on transformation failure is possible.

## Test Signals

Useful validation for this API area should include:

- JDiff/API checks confirming these classes, methods, fields, visibility, checked exceptions, and inheritance relationships remain stable for Hadoop 0.18.1 compatibility.
- `ProgramDriver` registration and dispatch tests for successful command routing, unknown command usage behavior, empty arguments, and propagation of exceptions thrown by target `main`.
- `Progress` tree tests for nested phase aggregation, named statuses, `complete()`, `startNextPhase()`, concurrent `set()`/`get()`, and `toString()` output.
- `Progressable` timeout-oriented integration tests around long-running map/reduce, filesystem, or sort operations.
- `QuickSort` tests over empty, singleton, sorted, reverse-sorted, duplicate-heavy, and adversarial comparator ranges, with a reporter that verifies progress callbacks.
- `ReflectionUtils` tests for `Configurable` and non-`Configurable` classes, constructor failure, typed `getClass`, thread-info printing, and min-interval throttling in `logThreadInfo`.
- `RunJar` tests for manifest main class, command-line main class, missing main class, jar extraction, duplicate entries, nested directories, and unsafe jar entry names.
- `ServletUtil` tests for response content type/header generation, whitespace-only request parameters, normal parameters, and footer output.
- `Shell` tests for environment and working directory propagation, nonzero exit status and `ExitCodeException`, output capture, interval gating, Windows/null ulimit behavior, and large-output boundaries.
- `StringUtils` tests for stack trace stringification, hostname simplification, percentage and byte formatting, byte/hex round trips, URI/path conversion, escaped split/escape/unescape edge cases, and elapsed-time formatting including negative intervals.
- `Tool`/`ToolRunner` integration tests for generic option parsing, configuration mutation, application arguments preserved after generic parsing, return-code propagation, and printed generic usage.
- `VersionInfo` tests against known build metadata resources and fallback behavior when metadata is absent.
- `XMLUtils.transform` golden-output tests plus invalid stylesheet/XML failure tests.
