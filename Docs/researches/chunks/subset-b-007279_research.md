# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 37175-38788

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.18.2, not Java implementation code. It starts inside `org.apache.hadoop.util.GenericsUtil`, then covers the rest of the `org.apache.hadoop.util` package through `XMLUtils`, and ends at the closing `</api>` marker. The XML records compatibility metadata: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The covered API surface is mostly Hadoop's utility layer: generic array helpers, indexed sorting contracts and sort implementations, host include/exclude file loading, native library loading flags, platform/build helpers, priority queue and progress tracking utilities, command dispatch and jar execution, servlet helpers, shell command execution, string/URI/path formatting helpers, the `Tool`/`ToolRunner` command-line contract, version metadata access, and XML transformation.

## Purpose and Major API Surface

`GenericsUtil` exposes generic type helpers: `getClass(T)` returns a correctly typed `Class<T>`, `toArray(Class<T>, List<T>)` converts a list using an explicit element class, and `toArray(List<T>)` infers the element class from the list but documents an `ArrayIndexOutOfBoundsException` risk for empty lists.

`IndexedSortable` and `IndexedSorter` define the abstraction used by Hadoop's in-place sort algorithms. `IndexedSortable` supplies address-based `compare(int, int)` and `swap(int, int)`. `IndexedSorter` sorts the half-open logical index range `[l, r)` and has an overload that periodically reports progress through `Progressable`.

`HeapSort` and `QuickSort` implement `IndexedSorter`. `HeapSort` is a final heap-sort implementation. `QuickSort` is a final quick-sort implementation with a protected static `getMaxDepth(int)` helper and Javadoc stating that it switches to `HeapSort` when recursion gets too deep.

`MergeSort` is a separate core merge-sort implementation constructed with a `Comparator<IntWritable>` and exposes `mergeSort(int[] src, int[] dest, int low, int high)`.

`HostsFileReader` reads host inclusion and exclusion files from constructor-provided paths. `refresh()` reloads the files and may throw `IOException`; `getHosts()` and `getExcludedHosts()` return the current host sets.

`NativeCodeLoader` is the native Hadoop library gate. `isNativeCodeLoaded()` reports whether `libhadoop` is loaded. `getLoadNativeLibraries(JobConf)` and `setLoadNativeLibraries(JobConf, boolean)` expose a per-job configuration switch controlling whether native libraries may be used when present.

`PlatformName`, `PrintJarMainClass`, and `VersionInfo` are small runtime/build helpers. `PlatformName.getPlatformName()` returns the JVM platform name and `main` prints it. `PrintJarMainClass.main` prints the main class from a jar. `VersionInfo` exposes Hadoop build metadata through `getVersion`, `getRevision`, `getDate`, `getUser`, `getUrl`, `getBuildVersion`, and `main`.

`PriorityQueue` is an abstract heap-like queue over `Object`. Subclasses provide `lessThan(Object,Object)` and must call protected final `initialize(int maxSize)`. Public final operations include `put`, `top`, `pop`, `adjustTop`, `size`, and `clear`; `insert` conditionally adds an element if the queue has capacity or the element is competitive with the current top.

`ProgramDriver` is a named program registry for example/application launchers. `addClass(String, Class, String)` records a runnable main class and description, and `driver(String[])` dispatches based on `args[0]`, invoking the target class's `main` with remaining arguments. Both can throw broad reflective or application errors.

`Progress` models hierarchical task progress. It creates a root node, supports adding named or unnamed phases, moving to the next phase, returning the current sub-phase, marking a node complete, setting leaf progress, computing root progress, setting status, and formatting state through `toString`. Several phase/progress/status methods are synchronized.

`Progressable` is the callback interface for long-running work to report liveness to Hadoop. The docs call out timeout avoidance for operations that otherwise appear stalled.

`ReflectionUtils` centralizes reflection helpers. `setConf(Object, Configuration)` injects configuration into configurable objects, `newInstance(Class<?>, Configuration)` constructs and initializes instances, `getClass(T)` returns a correctly typed class, and thread-diagnostic helpers enable contention tracing plus print or log stack information with an interval guard.

`RunJar` unpacks and runs Hadoop job jars. `unJar(File, File)` extracts a jar into a directory. `main(String[])` runs a job jar, using the manifest main class or a command-line main class when absent.

`ServletUtil` supplies web UI helpers: `initHTML(ServletResponse, String)` starts an HTML response and returns a `PrintWriter`, `getParameter(ServletRequest, String)` trims request parameters and returns null for whitespace-only values, `htmlFooter()` returns a standard footer, and `HTML_TAIL` is the footer constant.

`Shell` is an abstract base for running Unix-like commands with optional minimum re-execution intervals. Static helpers expose command arrays/strings for groups, permission lookup, permission/owner/group setting, user name lookup, and child-process memory limits from `JobConf`. Instance hooks configure environment and working directory, decide/run commands, expose the current `Process` and exit code, and require subclasses to implement `getExecString()` and `parseExecResult(BufferedReader)`. `Shell.ExitCodeException` adds an exit code to `IOException`. `Shell.ShellCommandExecutor` is a concrete small-output executor with constructors for command, working directory, and environment, plus `execute()` and `getOutput()`.

`StringUtils` is a broad static helper class. It stringifies exceptions, shortens hostnames, formats large integers and percentages, joins arrays, converts bytes to/from hex, converts URI and path arrays, formats elapsed times, parses comma-separated strings into arrays/collections, splits strings with escaping, escapes and unescapes separator characters, gets the hostname without throwing, and logs startup/shutdown messages. Public constants include `COMMA`, `COMMA_STR`, and `ESCAPE_CHAR`.

`Tool` extends `Configurable` and defines the standard Hadoop command-line application contract `run(String[])`. `ToolRunner` runs tools after generic Hadoop option parsing, sets the processed `Configuration` on the tool, offers an overload using `tool.getConf()`, and can print generic command usage.

`XMLUtils.transform(InputStream styleSheet, InputStream xml, Writer out)` applies an XSLT stylesheet to XML and surfaces `TransformerConfigurationException` and `TransformerException`.

## Control Flow and Behavioral Contracts

The XML does not contain method bodies, but the public contracts imply several flows. Indexed sorting callers adapt a data structure to `IndexedSortable`, then pass logical bounds to `HeapSort` or `QuickSort`. Sort implementations are constrained to mutate only through `compare` and `swap`; the progress overload can invoke `Progressable.progress()` during longer sorts.

Priority queue flow starts with subclass construction and `initialize(maxSize)`. `put` always inserts and can overflow the initialized capacity; `insert` is the safer top-N style operation because it can reject non-competitive elements when full. `top` is constant-time, while `put`, `pop`, and `adjustTop` are logarithmic. `adjustTop` is meant for mutating the top element in place and restoring heap order.

Progress flow is tree-shaped. A caller constructs a root `Progress`, adds child phases, advances with `startNextPhase()`, updates leaves with `set(float)`, and reads aggregate progress from the root with `get()`. `complete()` advances the parent to its next child, so parent/child relationships drive visible progress state.

Tool execution flow uses `ToolRunner.run`. Generic Hadoop options are parsed first through the related `GenericOptionsParser` contract, the resulting configuration is installed into the `Tool`, and then application-specific arguments are passed to `Tool.run`. The return value is the application exit code.

Shell execution flow is template-method based. A subclass provides the command vector and output parser. `run()` decides whether the minimum interval permits re-execution, starts a process with configured environment and working directory, parses stdout, records exit status, and can throw `IOException` or `ExitCodeException`. `ShellCommandExecutor` covers the simple case by collecting command output as a string.

Program and jar launch flows are reflective. `ProgramDriver` maps a short command name to a class with a `main` method and dispatches based on the first argument. `RunJar` extracts jar contents, locates the main class from the manifest or command line, and invokes it with remaining arguments.

String parsing flow centers on escaped comma-separated values. `escapeString`, `unEscapeString`, and `split` must agree on `ESCAPE_CHAR` and separator handling; callers that persist comma-separated configuration values depend on round-tripping through these helpers.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. Runtime state described by these APIs includes host include/exclude sets, job configuration flags, priority queue heap contents, progress tree nodes and status strings, command registries, shell process handles and exit codes, shell output buffers, servlet response output, and build/version metadata loaded from package or annotation resources.

Persistent or external side effects appear in several utilities. `HostsFileReader.refresh()` reads host files from disk. `NativeCodeLoader` observes native library loading and mutates `JobConf` settings for native library usage. `RunJar.unJar` writes extracted jar contents to a directory, and `RunJar.main` can execute arbitrary job code. `Shell` starts OS processes, sets process environment and working directory, may apply `ulimit` commands, and can expose platform-specific behavior through the `WINDOWS` flag. `ServletUtil.initHTML` writes HTTP response headers/body content. `XMLUtils.transform` writes transformed XML to the supplied writer. `ToolRunner.run` mutates the `Tool`'s configuration reference before calling it.

Most utility classes are stateless static helpers, but not all are thread-neutral. `Progress` marks several state-changing methods synchronized, while queue, shell executor, host reader, and program driver state are mutable and not documented as thread-safe in this XML.

## Dependencies and Integration Points

These utilities sit at integration boundaries across Hadoop common. Sorting depends on `IndexedSortable`, `Progressable`, `Comparator<IntWritable>`, and mutable caller-owned indexed data. Host loading integrates with local files and Java `Set<String>`.

Configuration and MapReduce integration appears through `Configuration`, `Configurable`, `JobConf`, `Tool`, `ToolRunner`, mapper/reducer child process memory limits, and the documented generic Hadoop command-line options.

Runtime diagnostics and system integration depend on Java reflection, `PrintWriter`, Apache Commons Logging `Log`, JVM thread information, Java `Process`, `File`, `BufferedReader`, servlet request/response APIs, jar manifests, and XSLT classes from `javax.xml.transform`.

Filesystem and command integration is platform-sensitive. `Shell` exposes Unix command constants and has explicit Windows detection; native Hadoop loading depends on `libhadoop` availability and platform-specific bundled libraries. `RunJar`, `PrintJarMainClass`, and `VersionInfo` integrate with jar/package metadata.

String and path helpers bridge Java primitives and Hadoop filesystem types: `URI[]`, `Path[]`, byte arrays, date formats, hostnames, exception stack traces, and comma-separated configuration values.

## Risks and Compatibility Notes

This chunk starts after the opening of `GenericsUtil`, so adjacent lines are needed for that class's exact start metadata. The rest of the package boundaries through `XMLUtils` are complete in this chunk.

Several APIs expose legacy raw types (`Class`, `Object`, non-generic `PriorityQueue`) because this is a Hadoop 0.18.2 API snapshot. Tightening those signatures would be source or binary incompatible for callers using the documented methods.

Sort contracts are sensitive to range interpretation. `IndexedSorter` documents `[l, r)` semantics, so off-by-one changes in implementations or callers can corrupt caller-owned structures. `QuickSort`'s fallback to `HeapSort` is part of the documented worst-case control behavior.

`GenericsUtil.toArray(List<T>)` is explicitly unsafe for empty lists. Callers that may pass empty lists should use `toArray(Class<T>, List<T>)`; changing the empty-list behavior may alter compatibility expectations.

`PriorityQueue` capacity and ordering are subclass-driven. The docs state `put` can throw an array bounds runtime exception when over capacity, while `insert` may reject elements; callers must choose the operation that matches their top-N semantics.

Shell and native utility behavior is platform and environment dependent. Command constants are Unix-oriented, memory-limit command generation may return null on non-Unix platforms or when unspecified, external commands can hang or produce large output, and `ShellCommandExecutor` explicitly expects small output.

`StringUtils` methods are often used for persisted configuration strings. Changes to escaping, splitting, hex conversion, time formatting, URI/path conversion, or hostname simplification can break configuration compatibility and user-facing logs.

`ToolRunner` is a central command-line compatibility point. Reordering generic option parsing, configuration installation, or argument forwarding can break MapReduce applications that implement `Tool`.

`RunJar` and `ProgramDriver` execute arbitrary code through reflection. Error propagation is intentionally broad (`Throwable`), so wrappers must preserve diagnostics rather than narrowing failures in ways that hide application exceptions.

## Test Signals

JDiff-level validation should confirm this XML remains well-formed through the closing `</api>`, preserves each public/protected class and interface in `org.apache.hadoop.util`, and keeps signatures, declared exceptions, field constants, synchronization flags, final/static/abstract flags, visibility, and Javadoc deprecation markers stable.

Sorting tests should adapt arrays or lists to `IndexedSortable`, verify `HeapSort` and `QuickSort` over empty, single-element, duplicate-heavy, already sorted, reverse-sorted, and subrange inputs, assert half-open range behavior, and verify progress callbacks are made by progress-aware overloads.

Host and native loader tests should cover include/exclude file parsing, `refresh()` after file changes, missing or unreadable files, returned set contents, native-library loaded/unloaded states, and `JobConf` round trips for native library usage.

Priority queue tests should cover subclass `lessThan` ordering, `initialize` capacity, `put` overflow behavior, `insert` acceptance/rejection when full, `top`, `pop`, `adjustTop` after mutating the top element, `size`, and `clear`.

Progress and progressable tests should cover tree construction, named and unnamed phases, phase advancement, completion propagation to parents, aggregate progress calculation, status formatting, synchronized access under concurrent updates, and timeout-sensitive code paths invoking `Progressable.progress()`.

Reflection and diagnostics tests should cover `Configurable` and non-`Configurable` objects in `setConf`, constructor/configuration behavior in `newInstance`, typed `getClass`, thread-info printing/logging interval suppression, and contention tracing toggles.

Launcher tests should cover `ProgramDriver.addClass` validation, dispatch to a registered main class, unknown commands, argument slicing, exception propagation, `RunJar.unJar`, manifest main-class lookup, command-line main override, and `PrintJarMainClass` output.

Shell tests should cover command vector construction, environment and working directory propagation, interval gating, stdout parsing, nonzero exit code handling through `ExitCodeException`, process and exit-code getters, `execCommand`, `ShellCommandExecutor` output capture, Windows/non-Windows command branches, and null memory-limit command cases.

String utility tests should cover exception stringification, hostname shortening, human-readable integer boundaries, percentage precision, array joining, byte/hex round trips, URI/path conversion, negative and positive time differences, formatted time-with-diff edge cases, comma-separated parsing, escaped separators, invalid escape sequences, hostname fallback, and startup/shutdown log message content.

Tool and XML tests should cover `ToolRunner.run` with null and non-null configurations, generic option parsing effects, forwarded application args, return code propagation, generic usage printing, and successful/failing XSLT transforms with checked exception propagation.
