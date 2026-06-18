# subset-b-007371 Hadoop util research

This grouped report covers Hadoop common utility classes under `org.apache.hadoop.util`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DurationInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DurationInfo.java

## Purpose

`DurationInfo` is a small `AutoCloseable` duration logger built for try-with-resources blocks. It extends `OperationDuration`, logs a "Starting" line at construction, and logs the elapsed duration from `close()`.

## Important APIs, Types, And Functions

The public constructors accept a `Logger`, an optional `logAtInfo` flag, and `String.format` style text. `getFormattedText()` memoizes the formatted message from a `Supplier<String>`. `toString()` appends the inherited duration text, and `close()` calls `finished()` before logging at INFO or DEBUG.

## Control Flow, State, And Persistence

Construction records the start timestamp in `OperationDuration`, stores the logger, lazily formats text, and logs the start message only when the selected level is enabled. Closing updates the finish timestamp and emits the final message. State is per-instance and in-memory only; no persistent data is written beyond logging.

## Dependencies And Integration Points

It depends on SLF4J and `OperationDuration`. Callers integrate it around expensive operations such as configuration, filesystem, or service work where scoped elapsed-time logging is useful.

## Risks And Test Signals

The formatted text is cached, so mutable arguments are captured at first formatting rather than close time. `String.format` exceptions can be thrown during construction. Tests should cover INFO and DEBUG modes, lazy formatting, `toString()` duration text, and try-with-resources close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/DurationInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitCodeProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitCodeProvider.java

## Purpose

`ExitCodeProvider` is a minimal interface for exceptions or error carriers that can expose a process exit code. It lets existing exception hierarchies participate in command-line exit handling without sharing a base class.

## Important APIs, Types, And Functions

The only API is `int getExitCode()`. `ExitUtil.ExitException` and `ExitUtil.HaltException` implement it, and other Hadoop exceptions can implement it where callers need stable shell status propagation.

## Control Flow, State, And Persistence

The interface has no control flow or state. Runtime behavior depends entirely on implementing classes and consumers such as `ExitUtil` or command wrappers.

## Dependencies And Integration Points

It lives in `org.apache.hadoop.util` and has no imports. It integrates with CLI tools, service launchers, and test hooks that distinguish normal failures from generic exceptions.

## Risks And Test Signals

The main risk is inconsistent exit-code semantics across implementers. Tests should assert that wrappers prefer `getExitCode()` over fallback defaults and preserve expected nonzero codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitCodeProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitUtil.java

## Purpose

`ExitUtil` centralizes JVM termination so Hadoop code can be tested or embedded without directly invoking `System.exit()` or `Runtime.halt()`. It can disable exits or halts, convert them to exceptions, remember the first attempted termination, and still perform real process termination when enabled.

## Important APIs, Types, And Functions

Important types are `ExitException` and `HaltException`, both `RuntimeException` classes implementing `ExitCodeProvider`. Control APIs include `disableSystemExit()`, `enableSystemExit()`, `disableSystemHalt()`, `enableSystemHalt()`, `resetFirstExitException()`, `resetFirstHaltException()`, `terminate(...)`, `halt(...)`, `haltOnOutOfMemory()`, and getters for the first captured exceptions.

## Control Flow, State, And Persistence

Static volatile flags gate real exit and halt calls. `terminate(ExitException)` logs nonzero status, captures logging failures as suppressed throwables, stores the first disabled-exit exception in an `AtomicReference`, and either throws it or calls `System.exit(status)`. `halt(HaltException)` mirrors this flow for `Runtime.getRuntime().halt(status)`. `haltOnOutOfMemory()` avoids normal cleanup and directly halts after best-effort stderr output. State is JVM-global and non-persistent.

## Dependencies And Integration Points

It depends on SLF4J and is annotated limited-private for HDFS, MapReduce, and YARN. Tools such as `NativeLibraryChecker` use it for testable process exit. Service launchers and tests rely on the disable flags to assert exit behavior.

## Risks And Test Signals

Global static flags can leak between tests unless reset. Logging itself can throw `Error`, and the code intentionally prioritizes errors over exit exceptions. Tests should cover real-disabled paths, first-exception capture, status propagation, suppressed exceptions, halt-vs-exit independence, and OOM halt behavior with minimal assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ExitUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FastNumberFormat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FastNumberFormat.java

## Purpose

`FastNumberFormat` provides a compact, allocation-light helper for appending a long to a caller-supplied `StringBuilder` with optional zero padding.

## Important APIs, Types, And Functions

The only API is `format(StringBuilder sb, long value, int minimumDigits)`. It handles negative values by appending `-`, computes how many leading zeroes are needed, appends those zeroes, then appends the numeric value.

## Control Flow, State, And Persistence

The method is stateless and thread-safe as long as the caller owns the `StringBuilder`. It uses simple arithmetic rather than `NumberFormat`, so there is no locale or formatter state.

## Dependencies And Integration Points

It has no external dependencies and is suitable for hot paths that need predictable decimal formatting, such as IDs or counters.

## Risks And Test Signals

`Long.MIN_VALUE` remains negative when negated, so tests should verify the expected output for that edge case. Padding behavior should be tested for zero, negative values, minimum digits smaller/larger than actual digits, and builder reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FastNumberFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FileBasedIPList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FileBasedIPList.java

## Purpose

`FileBasedIPList` loads IP addresses, hostnames, and CIDR ranges from a local text file and answers membership queries through the `IPList` interface.

## Important APIs, Types, And Functions

The constructor takes a file name and builds a `MachineList` from unique file lines. `reload()` returns a new `FileBasedIPList` for the same file. `isIn(String ipAddress)` delegates to `MachineList.includes()`. `readLines()` opens the file as UTF-8, trims and filters comments/empty lines, and deduplicates with a `HashSet`.

## Control Flow, State, And Persistence

If the file does not exist, construction logs a warning and uses an empty `MachineList`. Otherwise it reads the full file once. Instances are immutable after construction; `reload()` does not mutate the existing list. Persistence is entirely external in the watched file.

## Dependencies And Integration Points

It depends on `MachineList`, `IPList`, Java NIO file APIs, and SLF4J. It is used where administrators provide allow/deny lists for network-facing Hadoop services.

## Risks And Test Signals

Membership reflects only the snapshot at construction time. Bad CIDR syntax propagates from `MachineList`; unknown hosts are logged and skipped there. Tests should cover missing files, comments, whitespace, duplicate entries, wildcard/list behavior through `MachineList`, and reload producing a fresh snapshot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FileBasedIPList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FindClass.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FindClass.java

## Purpose

`FindClass` is a diagnostic `Tool` for classpath and resource lookup. It can load a class, instantiate a class, locate a resource, or print a resource to stdout, returning explicit status codes for scripts.

## Important APIs, Types, And Functions

Actions are `create`, `load`, `locate`, and `print`. Exit codes include `SUCCESS`, `E_USAGE`, `E_NOT_FOUND`, `E_LOAD_FAILED`, and `E_CREATE_FAILED`. Key helpers are `getClass()`, `getResource()`, `loadResource()`, `dumpResource()`, `loadClass()`, `createClassInstance()`, `usage()`, `explainResult()`, and `setOutputStreams()` for tests.

## Control Flow, State, And Persistence

`run()` expects exactly an action and a target. Resource lookup uses the configured classloader. Class loading reports code source when available; creation uses `ReflectionUtils.newInstance()` with the active `Configuration`. Resource printing streams bytes until EOF. Static stdout/stderr streams are mutable test state; no persistent state is written.

## Dependencies And Integration Points

It integrates with `ToolRunner`, `Configured`, `Configuration`, `ReflectionUtils`, and classloader resources. It is useful in Hadoop shell diagnostics and tests that validate client classpaths or generated resources.

## Risks And Test Signals

Static stream overrides can leak between tests. Instantiation can execute arbitrary class initialization and constructors. Resource printing does not close stdout. Tests should validate every action, missing resources/classes, constructor failure, code-source reporting, usage errors, and stream override reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/FindClass.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSet.java

## Purpose

`GSet` defines a set-like collection that also supports key-based retrieval of the stored element. It fills the gap between `Set` and `Map` for objects that act as their own keys.

## Important APIs, Types, And Functions

The interface extends `Iterable<E>` and declares `size()`, `contains(K)`, `get(K)`, `put(E)`, `remove(K)`, `clear()`, and `values()`. The type parameters require stored elements `E` to be assignable to keys `K`.

## Control Flow, State, And Persistence

There is no implementation state here. Implementations decide thread-safety, hashing strategy, replacement semantics, and value-view behavior. The contract rejects null keys/elements.

## Dependencies And Integration Points

It depends on Java collections and SLF4J for a shared logger. Implementations in this set include `GSetByHashMap`, `LightWeightGSet`, and `LightWeightResizableGSet`, used by memory-sensitive Hadoop structures.

## Risks And Test Signals

The replacement semantics differ from `Set.add()`, so callers must expect `put()` to replace equal elements. Tests for implementations should verify null rejection, value-view backing behavior, iterator behavior, and equality/hash-code consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSetByHashMap.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSetByHashMap.java

## Purpose

`GSetByHashMap` is the straightforward `HashMap`-backed implementation of `GSet`, intended when standard Java collection overhead is acceptable.

## Important APIs, Types, And Functions

The constructor accepts initial capacity and load factor. `put(E)` stores the element as both key and value, replacing any equal element. `contains()`, `get()`, `remove()`, `iterator()`, `clear()`, and `values()` delegate to the backing map.

## Control Flow, State, And Persistence

The only state is a private `HashMap<K,E>`. There is no synchronization and no persistence. The values collection and iterator are live views from `HashMap`.

## Dependencies And Integration Points

It depends on `GSet`, `HashMap`, and Java collection iterators. It can be substituted for low-memory `GSet` implementations in tests or less constrained code.

## Risks And Test Signals

`put(null)` throws `UnsupportedOperationException`, while some other methods rely on `HashMap` null behavior despite the `GSet` contract. Tests should cover replacement, returned previous values, live `values()` view, iterator removal semantics inherited from `HashMap`, and null behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GSetByHashMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GcTimeMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GcTimeMonitor.java

## Purpose

`GcTimeMonitor` is a daemon monitoring thread that estimates the percentage of recent wall-clock time spent in JVM garbage collection and invokes a callback when a threshold is exceeded.

## Important APIs, Types, And Functions

`Builder` configures observation window, sleep interval, threshold, and `GcTimeAlertHandler`. The constructor validates bounds and allocates a ring buffer of `TsAndData`. `work()` runs the monitoring loop. `shutdown()` stops future iterations. `getLatestGcData()` returns a clone of mutable metrics stored in `GcData`.

## Control Flow, State, And Persistence

On start, it snapshots GC counters, sleeps, computes per-interval GC pause deltas from all `GarbageCollectorMXBean`s, advances ring-buffer indices, sums pauses inside the observation window, and updates `curData`. Alerts receive a cloned snapshot. State is in-memory thread/ring-buffer data and is lost on shutdown.

## Dependencies And Integration Points

It extends `SubjectInheritingThread`, uses Java management MXBeans, and Hadoop `Preconditions`. It integrates with services that need live back-pressure or warnings when GC time becomes excessive.

## Risks And Test Signals

The alert handler can retain large object graphs if `shutdown()` is not called. Long sleep intervals reduce accuracy; huge windows are rejected by the buffer cap. Tests should cover constructor validation, ring-buffer window math, alert threshold behavior, cloned data immutability, and clean shutdown/interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GcTimeMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GenericOptionsParser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GenericOptionsParser.java

## Purpose

`GenericOptionsParser` parses Hadoop's standard command-line options and applies them to a `Configuration`, separating framework options from application-specific remaining arguments.

## Important APIs, Types, And Functions

Constructors accept optional Commons CLI `Options`, a `Configuration`, and raw args. Public accessors are `getRemainingArgs()`, `getConfiguration()`, `getCommandLine()`, and `isParseSuccessful()`. Key helpers include `buildGeneralOptions()`, `processGeneralOptions()`, `validateFiles()`, `getLibJars()`, `getFiles()`, `getResources()`, and `printGenericCommandUsage()`.

## Control Flow, State, And Persistence

Parsing builds generic options under `Option.class` synchronization, uses `GnuParser`, stores the resulting `CommandLine`, and mutates the supplied configuration. `-fs`, `-jt`, `-conf`, `-D`, `-files`, `-archives`, `-libjars`, and `-tokenCacheFile` each set corresponding configuration keys or credentials. `-libjars` also creates new `URLClassLoader`s for the configuration and current thread. State is in-memory configuration, credentials, classloaders, and parsed CLI state.

## Dependencies And Integration Points

It depends on Commons CLI, Hadoop `Configuration`, `FileSystem`, `FileUtil`, `Path`, `Credentials`, and `UserGroupInformation`. `ToolRunner` and Hadoop command-line tools rely on it before delegating to application arguments.

## Risks And Test Signals

Option parsing mutates global-ish thread context classloader state. File validation touches local and Hadoop filesystems and can fail before application code runs. Tests should cover repeated `-conf` and `-D`, wildcard libjars, missing token cache files, remaining-arg preservation, parse failures, and configuration source metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GenericOptionsParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GenericsUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GenericsUtil.java

## Purpose

`GenericsUtil` contains reflection and generic-array helpers used to work around Java type erasure, plus a compatibility helper for SLF4J reload4j logger access.

## Important APIs, Types, And Functions

`getClass(T)` returns the runtime class with a generic cast. `toArray(Class<T>, List<T>)` and `toArray(List<T>)` allocate typed arrays. `isLog4jLogger(Class<?>)` checks logger implementation compatibility and caches classpath failure with an `AtomicBoolean`.

## Control Flow, State, And Persistence

Array creation uses `Array.newInstance()`. Logger detection first checks whether the reload4j adapter class remains available; once missing, the atomic flag prevents repeated class loading. State is only the static cache flag.

## Dependencies And Integration Points

It depends on reflection, lists, SLF4J, and Hadoop annotations. It supports utility code that needs typed arrays or log4j-specific behavior while compiled against SLF4J.

## Risks And Test Signals

Unchecked casts are intentional but can hide type mistakes until runtime. The log4j adapter cache is one-way after a missing-class result. Tests should cover empty and non-empty lists, subclass runtime classes, logger adapter positive/negative cases, and classloader behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/GenericsUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HeapSort.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HeapSort.java

## Purpose

`HeapSort` implements `IndexedSorter` using an in-place heap sort over an `IndexedSortable` index range. It is intended for MapReduce-style sort paths where data is manipulated through compare/swap callbacks.

## Important APIs, Types, And Functions

Public methods are `sort(IndexedSortable s, int p, int r)` and `sort(IndexedSortable s, int p, int r, Progressable rep)`. Internal helpers build and pop the heap using callback comparisons and swaps; the progress-aware overload periodically invokes `rep.progress()`.

## Control Flow, State, And Persistence

The algorithm builds a max heap over `[p, r)`, repeatedly swaps the root with the end, reduces heap size, and heapifies. It keeps no object state and persists nothing.

## Dependencies And Integration Points

It depends on `IndexedSorter`, `IndexedSortable`, and `Progressable`. It integrates with Hadoop sort buffers whose records are addressed indirectly rather than as Java objects.

## Risks And Test Signals

Heap sort is not stable. Bugs in range math can corrupt adjacent records because swaps are callback-driven. Tests should sort empty, singleton, already-sorted, reverse, duplicate-key, and subrange inputs, and verify progress callbacks do not change ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HeapSort.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HostsFileReader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HostsFileReader.java

## Purpose

`HostsFileReader` manages include and exclude host files for Hadoop services, exposing atomic snapshots of allowed and excluded hosts, including optional exclude timeout values.

## Important APIs, Types, And Functions

Constructors load include/exclude files from file names or streams. Public APIs include `refresh()`, `lazyRefresh()`, `finishRefresh()`, stream-based `refresh(...)`, `getHosts()`, `getExcludedHosts()`, `getHostDetails()`, `getLazyLoadedHostDetails()`, `setIncludesFile()`, `setExcludesFile()`, and `updateFileNames()`. `HostDetails` holds immutable snapshot references.

## Control Flow, State, And Persistence

The class stores current and lazy-loaded `HostDetails` in `AtomicReference`s. Refresh reads include files into an unmodifiable set and exclude files into an unmodifiable map of host to optional timeout. Lazy refresh stages a snapshot without swapping it into current until `finishRefresh()`. Persistence stays in the external files; in-process state is atomic snapshots.

## Dependencies And Integration Points

It uses Java file streams, SLF4J, and Hadoop host include/exclude semantics for NameNode/DataNode or resource-management admission controls. Consumers obtain snapshots to avoid inconsistent include/exclude views.

## Risks And Test Signals

Bad file contents, duplicate hosts, missing files, or timeout parsing can change cluster membership behavior. Tests should cover atomic snapshot replacement, lazy refresh finish, stream inputs, empty file names, exclude timeout parsing, deprecated copy-out APIs, and file-name updates without content reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HostsFileReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HttpExceptionUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HttpExceptionUtils.java

## Purpose

`HttpExceptionUtils` serializes server-side exceptions into Hadoop's `RemoteException` JSON shape and reconstructs/throws client-side exceptions from non-expected HTTP responses.

## Important APIs, Types, And Functions

Constants define JSON keys: `RemoteException`, `exception`, `javaClassName`, and `message`. Server APIs are `createServletExceptionResponse()` and `createJerseyExceptionResponse()`. Client flow is `validateResponse(HttpURLConnection, int)`, which reads error JSON, calls `createExceptionFromJson()`, and uses a generic trick to throw reconstructed exceptions.

## Control Flow, State, And Persistence

Server methods set status/content type and write pretty JSON through `JsonSerialization.writer()`. Client validation returns on expected status. Otherwise it reads the error stream, parses a map, reflectively finds a public `(String)` constructor for the remote exception class, and throws it; if parsing or reflection fails, it throws an `IOException` with response details. There is no mutable persistent state.

## Dependencies And Integration Points

It depends on servlet APIs, JAX-RS `Response`, `HttpURLConnection`, `MethodHandles`, and `JsonSerialization`. Hadoop REST services and clients use it to preserve exception class/message across HTTP boundaries.

## Risks And Test Signals

Reflective construction only works for public exception classes with a string constructor. Error messages are truncated to one line. Tests should cover servlet and Jersey JSON shape, expected-status no-op, malformed JSON fallback, unknown classes, constructor absence, and checked exception rethrow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/HttpExceptionUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IPList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IPList.java

## Purpose

`IPList` is a tiny membership interface for IP-address allow or deny lists.

## Important APIs, Types, And Functions

The only method is `boolean isIn(String ipAddress)`. `FileBasedIPList` implements it by delegating to `MachineList`.

## Control Flow, State, And Persistence

The interface has no state or persistence. Implementations define parsing, lookup, reload, and thread-safety behavior.

## Dependencies And Integration Points

There are no imports. It integrates with security and networking components that need an interchangeable IP-list source.

## Risks And Test Signals

Callers should not infer whether input is a literal IP, hostname, or CIDR; that is implementation-specific. Tests belong mainly to implementations and should validate null, unknown, wildcard, and CIDR membership behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IPList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdGenerator.java

## Purpose

`IdGenerator` is a minimal interface for objects that allocate monotonically or otherwise uniquely generated IDs.

## Important APIs, Types, And Functions

It declares `long nextValue()`. Implementations provide the allocation policy; the interface does not specify persistence, monotonicity after restart, or concurrency guarantees.

## Control Flow, State, And Persistence

There is no state in the interface. Consumers should treat ID behavior as implementation-defined unless a concrete implementation documents stronger guarantees.

## Dependencies And Integration Points

It has no external dependencies. It provides a common seam for Hadoop subsystems that need pluggable ID allocation.

## Risks And Test Signals

The missing semantic contract can lead to assumptions about uniqueness or ordering that a given implementation may not satisfy. Concrete implementation tests should cover concurrency, overflow, restart behavior, and collision guarantees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdentityHashStore.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdentityHashStore.java

## Purpose

`IdentityHashStore` is a compact identity-based key/value store. Keys are compared with `==` rather than `equals()`, making it useful for object-identity tracking.

## Important APIs, Types, And Functions

The class stores alternating key/value entries in an `Object[]`. Important APIs are the constructor, `put(K,V)`, `get(K)`, `remove(K)`, `numElements()`, `capacity()`, `isEmpty()`, `visitAll(Visitor<K,V>)`, and the `Visitor` callback interface. Internal helpers compute identity hashes, probe open-addressed slots, and reallocate on growth.

## Control Flow, State, And Persistence

Insert probes by identity hash until it finds a free slot; inserting the same key multiple times creates multiple mappings rather than replacing. Lookups scan the full probe cycle for the first identical key. Remove clears the found entry without compacting clusters, relying on full-cycle lookup rather than stopping at empty slots. State is in-memory array contents, size, and capacity; there is no synchronization or persistence.

## Dependencies And Integration Points

It depends mainly on Java arrays and `Preconditions`. It integrates with low-level Hadoop code that needs identity semantics without the overhead or behavior of ordinary maps.

## Risks And Test Signals

Open addressing is sensitive to deletion and duplicate-key behavior. Tests should cover identity-distinct equal objects, null-key rejection on put, duplicate inserts of the same key, collision clusters, removal followed by lookup of later clustered entries, expansion, and `visitAll()` traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IdentityHashStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSortable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSortable.java

## Purpose

`IndexedSortable` abstracts a collection whose items can be compared and swapped by integer index, allowing sort algorithms to operate without knowing the underlying storage layout.

## Important APIs, Types, And Functions

It declares `compare(int i, int j)` with `Comparator`-style semantics and `swap(int i, int j)`.

## Control Flow, State, And Persistence

The interface has no state. Implementations own the indexed data and must keep compare/swap consistent across the sorted range.

## Dependencies And Integration Points

It is limited-private to MapReduce and pairs with `IndexedSorter`, `HeapSort`, and other sort algorithms in Hadoop's spill/sort code.

## Risks And Test Signals

Bad compare consistency or swap implementation corrupts sorter behavior. Tests should validate sorter algorithms against implementations with duplicate keys, equal records, and side-effect-sensitive storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSortable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSorter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSorter.java

## Purpose

`IndexedSorter` is the algorithm interface for sorting an `IndexedSortable` over a half-open index range.

## Important APIs, Types, And Functions

It declares `sort(IndexedSortable s, int l, int r)` and `sort(IndexedSortable s, int l, int r, Progressable rep)`. The second form reports progress during long sorts.

## Control Flow, State, And Persistence

The interface has no state. Implementations such as `HeapSort` use only `compare()` and `swap()` to reorder the range `[l, r)`.

## Dependencies And Integration Points

It depends on `IndexedSortable` and `Progressable`, and is limited-private to MapReduce. It integrates with sort buffers where record data is not exposed as an object list.

## Risks And Test Signals

Implementations must respect range boundaries and progress callback expectations. Tests should check empty ranges, subranges, progress reporting, and no swaps outside `[l, r)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IndexedSorter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedLock.java

## Purpose

`InstrumentedLock` wraps a `Lock` to detect long wait times and long held times, logging throttled warnings with suppressed-message statistics.

## Important APIs, Types, And Functions

It implements `Lock`: `lock()`, `lockInterruptibly()`, `tryLock()`, timed `tryLock()`, `unlock()`, and `newCondition()`. Timing hooks are `startLockTiming()` and `check(acquireTime, releaseTime, isLockHeld)`. Supporting types `SuppressedStats` and `SuppressedSnapshot` track throttled warning counts and max suppressed waits.

## Control Flow, State, And Persistence

Acquisition methods record wait start, delegate to the wrapped lock, check wait duration, then store acquire time. `unlock()` delegates and checks held duration. `check()` compares duration to threshold and uses atomic timestamps to throttle logs by `minLoggingGap`; otherwise it increments suppressed stats. State is per-wrapper timing counters, atomics, wrapped lock state, and logger output only.

## Dependencies And Integration Points

It depends on `java.util.concurrent.locks`, Hadoop `Timer`, `VisibleForTesting`, and SLF4J. Services wrap hot locks with it to diagnose stalls without changing lock callers.

## Risks And Test Signals

Non-reentrant or externally shared locks can make one acquire timestamp insufficient for unusual patterns; read locks are handled by a subclass. Tests should use fake timers to cover wait warnings, hold warnings, throttling, suppressed snapshots, interruptible and timed paths, and condition delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadLock.java

## Purpose

`InstrumentedReadLock` adapts `InstrumentedLock` for `ReentrantReadWriteLock.ReadLock`, where multiple threads may hold the read lock simultaneously.

## Important APIs, Types, And Functions

The constructor wraps `readWriteLock.readLock()`. It overrides `unlock()` and `startLockTiming()`. A `ThreadLocal<Long>` records the first read-lock acquisition timestamp for each holding thread.

## Control Flow, State, And Persistence

On first read hold per thread, `startLockTiming()` stores the monotonic timestamp. `unlock()` checks whether the thread's read hold count is about to drop to zero, then unlocks, removes the thread-local, and calls `check()` for held time. State is per-thread timing plus the underlying read-write lock.

## Dependencies And Integration Points

It depends on `ReentrantReadWriteLock`, `InstrumentedLock`, `Timer`, and SLF4J. It is created by `InstrumentedReadWriteLock`.

## Risks And Test Signals

Thread-local cleanup only occurs when hold count reaches zero, so unbalanced locking leaks thread-local state until thread death. Tests should cover reentrant read locking, concurrent readers, threshold logging on final unlock only, and interruption-free delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadWriteLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadWriteLock.java

## Purpose

`InstrumentedReadWriteLock` wraps a `ReentrantReadWriteLock` and exposes instrumented read and write locks through the standard `ReadWriteLock` interface.

## Important APIs, Types, And Functions

The constructor accepts fairness, name, logger, minimum logging gap, and warning threshold. `readLock()` returns an `InstrumentedReadLock`; `writeLock()` returns an `InstrumentedWriteLock`.

## Control Flow, State, And Persistence

Construction creates one underlying `ReentrantReadWriteLock` and two wrappers around its read/write sides. Runtime state is the underlying lock plus wrapper timing counters. There is no persistence.

## Dependencies And Integration Points

It depends on Java read-write locks, `InstrumentedReadLock`, `InstrumentedWriteLock`, and SLF4J. It integrates with services that want lock diagnostics while keeping `ReadWriteLock` APIs.

## Risks And Test Signals

Fairness must match the caller's concurrency expectations. Tests should verify read/write locks share the same underlying lock, fairness propagation, long read/write held logging, and standard `ReadWriteLock` semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedReadWriteLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedWriteLock.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedWriteLock.java

## Purpose

`InstrumentedWriteLock` adapts `InstrumentedLock` for `ReentrantReadWriteLock.WriteLock`, including reentrant write-lock timing rules.

## Important APIs, Types, And Functions

The constructor wraps `readWriteLock.writeLock()`. It overrides `unlock()` and `startLockTiming()` to use `ReentrantReadWriteLock.getWriteHoldCount()`.

## Control Flow, State, And Persistence

`startLockTiming()` records timing only on first write hold by the current thread. `unlock()` checks whether the write hold count is about to reach zero, delegates unlock, and only then reports held duration. State is inherited timing plus the shared read-write lock; nothing persists.

## Dependencies And Integration Points

It depends on `InstrumentedLock`, `ReentrantReadWriteLock`, `Timer`, and SLF4J. It is the write-side wrapper returned by `InstrumentedReadWriteLock`.

## Risks And Test Signals

Reentrant write locking should not log intermediate unlocks. Tests should cover nested write locks, final unlock logging, timed acquisition wait logging, and behavior when unlock is called without ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InstrumentedWriteLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IntrusiveCollection.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IntrusiveCollection.java

## Purpose

`IntrusiveCollection` implements a memory-efficient doubly linked collection where elements store their own previous/next pointers for each list they join.

## Important APIs, Types, And Functions

Elements implement `IntrusiveCollection.Element` with `insertInternal()`, `setPrev()`, `setNext()`, `removeInternal()`, `getPrev()`, `getNext()`, and `isInList()`. Collection APIs include `add()`, `addFirst()`, `remove()`, `iterator()`, `contains()`, `retainAll()`, `removeAll()`, and `clear()`. A sentinel root element tracks first and last.

## Control Flow, State, And Persistence

Adding checks null and membership, links around root or tail, calls element insertion, and increments size. Removal unlinks neighboring elements, calls `removeInternal()`, and decrements size. Iterators allow their own `remove()` but do not protect against arbitrary concurrent modification. State is in-memory links owned by elements and the collection size.

## Dependencies And Integration Points

It depends on Java collection interfaces, Hadoop `Preconditions`, and SLF4J. It integrates with high-cardinality metadata structures that need lower per-entry allocation than `LinkedList`.

## Risks And Test Signals

Elements must correctly maintain per-list link fields; a bad implementation can corrupt multiple lists. Tests should cover add-first/add-last order, duplicate add rejection, iterator remove, retain/remove all, clear, multi-list elements, and concurrent-modification caveats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/IntrusiveCollection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InvalidChecksumSizeException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InvalidChecksumSizeException.java

## Purpose

`InvalidChecksumSizeException` is an `IOException` raised when checksum metadata has an invalid bytes-per-checksum value or invalid checksum type.

## Important APIs, Types, And Functions

The class only provides `InvalidChecksumSizeException(String s)` and a `serialVersionUID`.

## Control Flow, State, And Persistence

It carries only the inherited exception message and stack trace. No mutable state or persistence is involved.

## Dependencies And Integration Points

It depends on `java.io.IOException` and integrates with checksum/meta-file parsing code that must distinguish malformed checksum configuration from other I/O failures.

## Risks And Test Signals

The class has no cause-taking constructor, so callers lose causal chaining unless they encode it in the message. Tests should assert it is catchable as `IOException` and preserves messages for invalid checksum metadata paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/InvalidChecksumSizeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JsonSerialization.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JsonSerialization.java

## Purpose

`JsonSerialization<T>` wraps Jackson serialization/deserialization for Hadoop objects, with helpers for local files, Hadoop filesystems, resources, bytes, strings, and pretty map writing.

## Important APIs, Types, And Functions

Static helpers are `writer()` and `mapReader()`. Instance APIs include `fromJson()`, `fromJsonStream()`, `load(File)`, `save(File,T)`, `fromResource()`, `fromInstance()`, `load(FileSystem,Path,FileStatus)`, `save(FileSystem,Path,T,boolean)`, `writeJsonAsBytes()`, `toBytes()`, `fromBytes()`, `toJson()`, and robust `toString(T)`.

## Control Flow, State, And Persistence

The constructor creates an `ObjectMapper` configured for unknown-property handling and indentation. Most mapper operations are synchronized. Local loads validate existence, file-ness, and non-empty content. Hadoop FS loads use `openFile()` with whole-file read policy and optional file status, then wrap JSON processing errors in `PathIOException`. Save methods overwrite only when requested and close streams in `finally`. Persistence is JSON written to local or Hadoop filesystems.

## Dependencies And Integration Points

It depends on Jackson, Hadoop `FileSystem`, `Path`, `FutureDataInputStreamBuilder`, `PathIOException`, `FutureIO.awaitFuture`, and annotations. It is reused by registry, REST, and configuration/state persistence code.

## Risks And Test Signals

UTF-8 is hard-coded through a string charset name. Shared `ObjectMapper` access is synchronized but callers can mutate the mapper returned by `getMapper()`. Tests should cover empty input, malformed JSON, unknown fields, filesystem status optimization, stream closure, overwrite false, resource loading, byte round trips, and robust `toString()` failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JsonSerialization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JvmPauseMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JvmPauseMonitor.java

## Purpose

`JvmPauseMonitor` is an `AbstractService` that runs a daemon loop to detect JVM or host pauses by measuring sleep overshoot and logging GC activity around the pause.

## Important APIs, Types, And Functions

Configuration keys are `jvm.pause.warn-threshold.ms` and `jvm.pause.info-threshold.ms`. Service hooks are `serviceInit()`, `serviceStart()`, and `serviceStop()`. Metrics getters expose warning count, info count, and total extra sleep time. Helpers `getGcTimes()` and `formatMessage()` describe GC deltas per collector.

## Control Flow, State, And Persistence

On start, a daemon `Monitor` repeatedly records GC counters, sleeps for 500 ms, computes extra sleep time via `StopWatch`, compares thresholds, logs WARN/INFO with GC differences, and accumulates counters. Stop flips `shouldRun`, interrupts, and joins the thread. State is service lifecycle, monitor thread, counters, and logs only.

## Dependencies And Integration Points

It depends on Hadoop `AbstractService`, `Configuration`, `Daemon`, `StopWatch`, local `Lists`/`Sets`, Guava-thirdparty `Joiner`/`Maps`, and Java MXBeans. Hadoop daemons use it for operational visibility into GC or host scheduling stalls.

## Risks And Test Signals

Counters are not atomic, though normally read from service threads. The sample `main()` intentionally leaks memory for manual testing. Tests should cover thresholds from configuration, start/stop lifecycle, interruption, log-level classification, GC-delta formatting, and metric accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/JvmPauseMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/KMSUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/KMSUtil.java

## Purpose

`KMSUtil` provides utility conversions and provider lookup helpers for Hadoop Key Management Server clients and key-provider metadata.

## Important APIs, Types, And Functions

Important APIs include `getKeyProvider(Configuration, String)`, `createKeyProviderFromUri(Configuration, URI)`, metadata-to/from-map conversion, encrypted-key-version serialization/deserialization helpers, and base64 material encoding/decoding. It handles KMS REST field names from `KMSRESTConstants`.

## Control Flow, State, And Persistence

Provider lookup resolves URIs through `KeyProviderFactory` and validates that a provider exists. Conversion helpers map `KeyProvider.Metadata`, key versions, and `EncryptedKeyVersion` objects to REST-compatible `Map` structures and back, including dates, versions, cipher, bit length, description, attributes, IV, encrypted material, and encryption key/version names. State is transient conversion data; persistence occurs in external KMS/key-provider systems.

## Dependencies And Integration Points

It depends on Commons Codec `Base64`, Hadoop `Configuration`, `KeyProvider`, `KeyProviderFactory`, `KMSClientProvider`, `KMSRESTConstants`, and KMS crypto extension types. It is a bridge between Java key-provider APIs and REST payloads.

## Risks And Test Signals

Incorrect map keys or base64 conversions can make encrypted keys undecryptable or incompatible across KMS versions. Tests should cover provider URI success/failure, metadata round trips, encrypted-key round trips, null/optional attributes, date handling, and malformed REST maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/KMSUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LambdaUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LambdaUtils.java

## Purpose

`LambdaUtils` contains a small helper for evaluating a `Callable` and completing a `CompletableFuture` with either its result or the thrown failure.

## Important APIs, Types, And Functions

The public helper is `eval(CompletableFuture<T> result, Callable<T> call)`. It invokes `call.call()`, completes the supplied future normally on success, or completes it exceptionally with any caught `Throwable`.

## Control Flow, State, And Persistence

The utility is stateless. `eval()` always returns the same future instance it was passed after attempting completion.

## Dependencies And Integration Points

It depends on Java `Callable` and `CompletableFuture`. It integrates with async Hadoop code that wants a concise bridge from synchronous callable execution into future completion.

## Risks And Test Signals

The helper catches `Throwable`, so serious errors are captured into the future rather than escaping the evaluating thread. Tests should verify successful completion, checked/runtime/error exceptional completion, returned future identity, callable invocation exactly once, and behavior when the future is already completed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LambdaUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightCache.java

## Purpose

`LightWeightCache` extends `LightWeightGSet` with low-overhead expiration and optional size-limit eviction. It is designed for entries that already carry their own hash-chain links and expiration timestamp.

## Important APIs, Types, And Functions

Entries must implement `LightWeightCache.Entry`, extending `LinkedElement` with `setExpirationTime()` and `getExpirationTime()`. Public APIs override `get()`, `put()`, `remove()`, and `iterator()`. Internal helpers are `setExpirationTime()`, `isExpired()`, `evict()`, `evictExpiredEntries()`, and `evictEntries()`.

## Control Flow, State, And Persistence

Construction validates creation/access expiration periods, adjusts recommended hash length for size limits, and creates a `PriorityQueue` ordered by expiration time. `put()` evicts expired entries, replaces any equal entry, sets creation expiration, queues it, and enforces size limit. `get()` optionally refreshes access expiration by removing/reinserting in the queue. `remove()` also evicts expired entries. State is hash table plus priority queue and timer; no persistence.

## Dependencies And Integration Points

It depends on `LightWeightGSet`, Hadoop `Timer`, `Preconditions`, `HadoopIllegalArgumentException`, and Java `PriorityQueue`. It supports memory-sensitive caches in HDFS and common services.

## Risks And Test Signals

The class is explicitly not thread-safe. Queue `remove(Object)` is linear, and expired entries are evicted only opportunistically with a per-call limit. Tests should cover expiration, access refresh, replacement, size-limit enforcement, iterator remove rejection, invalid constructor args, and queue/hash consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightGSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightGSet.java

## Purpose

`LightWeightGSet` is a low-memory hash set with key-based retrieval. Elements store their own singly linked collision pointer through `LinkedElement`, avoiding wrapper node allocations.

## Important APIs, Types, And Functions

`LinkedElement` declares `setNext()` and `getNext()`. Main APIs implement `GSet`: `get()`, `contains()`, `put()`, `remove()`, `values()`, `iterator()`, `clear()`, plus diagnostics `toString()` and `printDetails()`. Static helpers include `actualArrayLength()` and `computeCapacity()`. `SetIterator` is fail-fast unless tracking is disabled.

## Control Flow, State, And Persistence

The constructor rounds the backing array size to a power of two and computes `hash_mask`. `put()` validates element/link type, removes any equal existing element, and inserts at the bucket head. `remove()` unlinks from the bucket chain and clears the element next pointer. Iteration walks buckets and chains while checking a modification counter. State is in-memory bucket array, size, modification count, and cached values view.

## Dependencies And Integration Points

It depends on `GSet`, Hadoop `HadoopIllegalArgumentException`, `StringUtils`, `Preconditions` indirectly through callers, and runtime memory sizing. HDFS metadata structures use it where entry count is high and allocation overhead matters.

## Risks And Test Signals

Elements must implement `LinkedElement` correctly and cannot belong to two `LightWeightGSet` chains using the same next field. The class is not thread-safe. Tests should cover replacement, null rejection, bad element type, collision chains, iterator fail-fast/remove, clear, capacity rounding, and memory-percentage capacity math.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightGSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightResizableGSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightResizableGSet.java

## Purpose

`LightWeightResizableGSet` adds synchronized access and table growth to `LightWeightGSet`, resizing when element count exceeds a configurable load-factor threshold.

## Important APIs, Types, And Functions

Constructors accept initial capacity and optional load factor, with defaults of 16 and 0.75. It synchronizes `put()`, `get()`, `remove()`, `size()`, `getIterator(Consumer<Iterator<E>>)` and resizing helpers `resize()` and `expandIfNecessary()`.

## Control Flow, State, And Persistence

Construction rounds capacity, initializes `hash_mask`, threshold, and buckets. `put()` delegates to the parent insertion then expands if `size > threshold` and below max capacity. `resize()` allocates a new bucket array and relinks every existing `LinkedElement` into its new bucket. State is inherited hash table plus capacity/load-factor fields; no persistence.

## Dependencies And Integration Points

It depends on `LightWeightGSet`, `HadoopIllegalArgumentException`, Java `Consumer`, and iterators. It is appropriate where the low-memory linked-element representation is desired but initial cardinality is uncertain.

## Risks And Test Signals

Returning iteration through a consumer under synchronization controls concurrent access, but callers must not retain and use the iterator after the synchronized callback if they need safety. Tests should cover constructor validation, expansion boundaries, rehash correctness, synchronized get/remove, iterator callback behavior, and max-capacity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LightWeightResizableGSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LimitInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LimitInputStream.java

## Purpose

`LimitInputStream` is Hadoop's copy of Guava's limited input stream, capping the number of bytes that can be read or skipped from an underlying stream.

## Important APIs, Types, And Functions

The constructor accepts an `InputStream` and nonnegative byte limit. It overrides `available()`, `mark()`, `read()`, `read(byte[],int,int)`, `reset()`, and `skip()` while tracking remaining bytes in `left` and marked remaining bytes in `mark`.

## Control Flow, State, And Persistence

Reads return EOF once `left` reaches zero. Bulk reads clamp length to `left` and subtract successful bytes read. `skip()` clamps similarly. `mark()` records the current remaining limit even if the underlying stream does not support reset; `reset()` validates support and mark presence before restoring `left`. State is per-stream wrapper only.

## Dependencies And Integration Points

It depends on `FilterInputStream` and Hadoop `Preconditions`. It is used where callers must expose only a bounded segment of a larger stream.

## Risks And Test Signals

The wrapper does not close early at the limit; it simply returns EOF. Tests should cover zero limit, negative limit rejection, single and bulk reads, skip, available clamping, mark/reset success and failure, and EOF behavior from the underlying stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LimitInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LineReader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LineReader.java

## Purpose

`LineReader` reads records from an `InputStream` into Hadoop `Text`, supporting default CR/LF/CRLF line endings or a custom byte delimiter.

## Important APIs, Types, And Functions

Constructors accept stream, buffer size, `Configuration`, and optional delimiter bytes. Public APIs are `readLine(Text,int,int)`, `readLine(Text,int)`, `readLine(Text)`, `close()`, and `getIOStatistics()`. Protected/test helpers expose buffer position/size and `unsetNeedAdditionalRecordAfterSplit()`. Core implementations are `readDefaultLine()` and `readCustomLine()`.

## Control Flow, State, And Persistence

The reader maintains a byte buffer, length, and position across calls. Default line reading handles LF, CR, and CRLF, including CR at buffer boundaries. Custom delimiter reading tracks partial delimiter matches and ambiguous bytes so split readers can avoid duplicate or missing records. It truncates stored `Text` to `maxLineLength` while still consuming bytes up to a record boundary or the consume hint. State is in-memory stream/buffer state; no persistence.

## Dependencies And Integration Points

It depends on `Configuration`, `Text`, filesystem `IOStatisticsSource`, and `IO_FILE_BUFFER_SIZE_KEY`. MapReduce input formats rely on it for split-aware line and custom-record reading.

## Risks And Test Signals

Delimiter boundary logic is subtle, especially at split boundaries and EOF. Tests should cover CR, LF, CRLF, unterminated final lines, very long lines with truncation, consume-limit overshoot, custom delimiters spanning buffers, ambiguous delimiter tails, IO statistics delegation, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/LineReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Lists.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Lists.java

## Purpose

`Lists` is a Hadoop-local collection utility class modeled after common Guava list helpers, creating mutable list implementations with convenient overloads.

## Important APIs, Types, And Functions

It provides `newArrayList()` overloads for empty lists, varargs elements, iterable/iterator contents, and expected sizes, plus `newLinkedList()` and capacity helper logic for array-list sizing.

## Control Flow, State, And Persistence

All methods are static and allocate new Java list instances. Iterable and iterator overloads copy elements into the new collection. There is no class state or persistence.

## Dependencies And Integration Points

It depends on Java `ArrayList`, `LinkedList`, `Iterator`, `Iterable`, and collection sizing utilities. Hadoop code uses it to avoid direct dependency on relocated or changing Guava APIs.

## Risks And Test Signals

Expected-size calculations must avoid integer overflow and excessive allocation. Tests should cover varargs null elements, iterator exhaustion, iterable copying, expected-size boundaries, and mutability of returned lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Lists.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MachineList.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MachineList.java

## Purpose

`MachineList` stores hostnames, literal IP addresses, CIDR ranges, or a wildcard and answers whether an `InetAddress` or string address is included.

## Important APIs, Types, And Functions

Constructors accept comma-separated strings or collections and an optional `InetAddressFactory` for tests. `includes(String)` resolves through the factory; `includes(InetAddress)` checks wildcard, exact addresses, then CIDR ranges. `getCollection()` exposes original entries for tests.

## Control Flow, State, And Persistence

Construction copies entries. A single `*` sets `all=true`; otherwise CIDR entries are parsed with `SubnetUtils` using inclusive host counts, and non-CIDR entries are resolved to `InetAddress`. Unknown hosts are logged and skipped. State is immutable sets/lists after construction; no persistence.

## Dependencies And Integration Points

It depends on Apache Commons Net `SubnetUtils`, Java networking, Hadoop `StringUtils`, and SLF4J. `FileBasedIPList` and admission-control code use it for host/IP membership.

## Risks And Test Signals

Hostname resolution happens at construction or string lookup time and can be DNS-dependent. Invalid CIDR syntax throws. Tests should use `InetAddressFactory` to cover wildcard, exact IP, hostname, CIDR, unknown host skipping, null input rejection, and IPv4 range boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MachineList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MergeSort.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MergeSort.java

## Purpose

`MergeSort` implements the core merge-sort algorithm for integer index arrays using a comparator over reusable `IntWritable` wrappers.

## Important APIs, Types, And Functions

The constructor accepts a `Comparator<IntWritable>`. `mergeSort(int[] src, int[] dest, int low, int high)` recursively sorts ranges. Internal `swap()` exchanges destination entries.

## Control Flow, State, And Persistence

For ranges shorter than seven, it uses insertion sort. Larger ranges recursively sort halves from destination to source, skips merging if already ordered, otherwise merges sorted halves back into destination. The instance holds the comparator and two reusable `IntWritable` objects; no persistence.

## Dependencies And Integration Points

It depends on `IntWritable`, `Comparator`, and MapReduce-limited APIs. It is used by sort code that manipulates integer pointer/index arrays rather than records directly.

## Risks And Test Signals

Reusable `IntWritable` fields make instances not thread-safe. Tests should cover stable merge behavior if expected by callers, insertion-sort threshold, already-sorted fast path, duplicate keys, reverse order, subrange sorting, and comparator side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/MergeSort.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCodeLoader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCodeLoader.java

## Purpose

`NativeCodeLoader` loads Hadoop's native library and exposes whether native code and build features are available.

## Important APIs, Types, And Functions

Static initialization attempts to load the Hadoop native library and records `nativeCodeLoaded`. Public APIs include `isNativeCodeLoaded()`, `getLibraryName()`, `buildSupportsIsal()`, and `buildSupportsOpenssl()`.

## Control Flow, State, And Persistence

Class loading performs a one-time native-library load, logs success or failure, and stores the result in static fields. Feature queries are native methods and should only be used when the library is loaded by callers that can tolerate native linkage failures. State is JVM-static native load status; persistence is outside the process in installed shared libraries.

## Dependencies And Integration Points

It depends on SLF4J and native JNI symbols packaged with Hadoop. Compression, crypto, erasure coding, native I/O, and `NativeLibraryChecker` use it to decide whether to use accelerated paths.

## Risks And Test Signals

Static initialization is one-shot per classloader, so tests need classloader isolation or careful assumptions. Missing/incorrect native libraries degrade features or fail checks. Tests should cover no-native fallback, library-name reporting when loaded, feature false paths, and logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCodeLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCrc32.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCrc32.java

## Purpose

`NativeCrc32` exposes native CRC32/CRC32C checksum calculation and verification routines used by Hadoop data paths when native code is available and the platform is supported.

## Important APIs, Types, And Functions

The class declares native methods for chunked checksum calculation and verification over byte arrays or direct buffers. Java wrappers pass buffer positions, lengths, file names, base offsets, and a verify/calculate flag through to JNI. It also exposes checksum constants copied from `DataChecksum`.

## Control Flow, State, And Persistence

`isAvailable()` returns false on SPARC and otherwise follows `NativeCodeLoader.isNativeCodeLoaded()`. Calculation and verification methods delegate directly to JNI and do not mutate buffer position, limit, or mark. Checksum mismatch is surfaced as `ChecksumException`. There is no Java mutable state or persistence.

## Dependencies And Integration Points

It depends on `DataChecksum`, `ChecksumException`, `ByteBuffer`, native Hadoop libraries loaded through `NativeCodeLoader`, and JNI symbols. It integrates with HDFS block read/write and local filesystem checksum verification.

## Risks And Test Signals

Native/Java behavior must match exactly across endian, direct-buffer, and byte-array paths. Tests should compare native results with Java checksum implementations, cover invalid checksum size/type, buffer offset/length boundaries, direct and heap buffers, and disabled-native fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCrc32.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeLibraryChecker.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeLibraryChecker.java

## Purpose

`NativeLibraryChecker` is a command-line diagnostic that prints availability of Hadoop native libraries and exits nonzero when required native support is missing.

## Important APIs, Types, And Functions

The only public entry point is `main(String[] args)`. It supports `-h` for usage and `-a` to require additional native libraries. It checks Hadoop native code, zlib, bzip2, OpenSSL, ISA-L, PMDK, and Windows `winutils.exe`.

## Control Flow, State, And Persistence

Argument validation prints usage and terminates via `ExitUtil`. The checker creates a `Configuration`, queries each subsystem's factory/loading state, prints a table, and calls `ExitUtil.terminate(1)` if required checks fail. No persistent state is changed.

## Dependencies And Integration Points

It depends on `NativeCodeLoader`, `ZlibFactory`, `Bzip2Factory`, `OpensslCipher`, `ErasureCodeNative`, `NativeIO`, `Shell`, and `ExitUtil`. It is used by administrators, build validation, and diagnostics.

## Risks And Test Signals

The `-a` failure condition requires zlib, bzip2, and ISA-L but prints OpenSSL/PMDK details without requiring them. Windows output includes `winutils` twice. Tests should disable exits, exercise `-h`, invalid args, default vs `-a`, Windows/non-Windows paths, and loaded/failure detail strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeLibraryChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/OperationDuration.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/OperationDuration.java

## Purpose

`OperationDuration` is a simple elapsed-time value object used to capture operation duration in milliseconds and format it as human-readable minutes/seconds/milliseconds.

## Important APIs, Types, And Functions

The constructor records start and initial finish time. `finished()` updates the finish timestamp. `value()` returns elapsed milliseconds. `getDurationString()`, `toString()`, and static `humanTime(long)` format values. `asDuration()` returns a `java.time.Duration`.

## Control Flow, State, And Persistence

By default, `value()` is zero until `finished()` is called because start and finish are initialized together. `time()` is protected for test overrides. State is just start and finish timestamps; no persistence.

## Dependencies And Integration Points

It depends on `java.time.Duration` and Hadoop annotations. `DurationInfo` extends it for scoped logging, and other utilities can use it for timing without logging.

## Risks And Test Signals

It uses wall-clock `System.currentTimeMillis()`, so clock adjustments can produce negative or skewed durations. Tests should override `time()` or control timestamps to cover formatting, repeated `finished()` calls, `asDuration()`, and negative/large values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/OperationDuration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Options.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Options.java

## Purpose

`Options` provides type-safe marker classes for varargs option lists and helpers to retrieve or prepend options.

## Important APIs, Types, And Functions

Nested abstract option classes carry values for `String`, `Class`, `boolean`, `int`, `long`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, and `Progressable`. `getOption(Class<T>, base[] opts)` returns the first option assignable to a class. `prependOptions(T[] oldOpts, T... newOpts)` combines arrays with new options first.

## Control Flow, State, And Persistence

Each option wrapper stores a final value and exposes it through a getter. `getOption()` scans the varargs array and casts the first matching class. `prependOptions()` uses `Arrays.copyOf()` and `System.arraycopy()`. There is no global state or persistence.

## Dependencies And Integration Points

It depends on Hadoop filesystem stream/path types and `Progressable`. Filesystem APIs use it to accept extensible typed optional arguments without long overload lists.

## Risks And Test Signals

Matching by class means subclasses and duplicate option types return the first matching instance. Tests should cover all wrapper getters, absent options, subclass matching, duplicate ordering, null arrays if allowed by callers, and prepend order/array component type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/Options.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PerformanceAdvisory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PerformanceAdvisory.java

## Purpose

`PerformanceAdvisory` is a central logger holder for non-fatal performance advisories.

## Important APIs, Types, And Functions

The class exposes a single public static `Logger LOG` named for `org.apache.hadoop.util.PerformanceAdvisory`.

## Control Flow, State, And Persistence

There is no method control flow. Runtime state is the static SLF4J logger; persistence is whatever logging backend writes.

## Dependencies And Integration Points

It depends on SLF4J. Other Hadoop code can log performance warnings to this category so operators can route or filter advisory messages separately from functional errors.

## Risks And Test Signals

Because it is just a shared logger, misuse can blur performance hints with correctness warnings. Tests rarely need this class directly; integration signals are correct logger category names and expected log emission from callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/PerformanceAdvisory.java -->
