# subset-b-007345 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileUtil.java

Purpose: `FileUtil` is Hadoop common's broad file utility surface for local and Hadoop `FileSystem` operations. It covers status-to-path conversion, recursive local deletion, recursive copy between `FileSystem` instances and local files, archive extraction, symlink and permission helpers, classpath-jar construction, filesystem URI comparison, simple write helpers, protected rename access, eventually consistent listing handling, and erasure-coding capability checks.

Important APIs: `stat2Paths`, `fullyDelete`, `fullyDeleteContents`, `copy` overloads, `checkDest`, `getDU`, `unZip`, `unTar`, `symLink`, `chmod`, `setOwner`, `setPermission`, `createJarWithClassPath`, `getJarsInDirectory`, `compareFs`, `write` overloads, `maybeIgnoreMissingDirectory`, and `checkFSSupportsEC`. The deprecated nested `HardLink` class preserves compatibility with callers that formerly used `FileUtil.HardLink`.

Control flow and state: recursive delete first tries direct deletion so symlinks and empty directories are removed without traversing targets, then recursively deletes contents for real non-empty directories. Recursive copy checks destination dependencies, creates directories, streams file data using `openFile` hints and `IOUtils.copyBytes`, and optionally deletes sources after each copied subtree. Archive extraction validates canonical output paths in Java ZIP/TAR paths, converts UNIX ZIP modes to POSIX permissions, and delegates non-Windows TAR extraction to shell `tar`. The class itself stores no durable state beyond constants and logger, but it mutates local filesystem permissions, timestamps, links, classpath temp jars, and destination files.

Dependencies and integration: integrates with `FileSystem`, `FileContext`, `Path`, `FileStatus`, `FSDataOutputStream`, `Options.OpenFileOptions`, `FsPermission`, `NativeIO`, `Shell`, Commons Compress, Commons IO, and Java NIO. It is widely used by shell, local staging, archive handling, tests, and filesystem implementations needing common copy/delete/write behavior.

Risks: many methods are partial-failure-prone: recursive copy with `deleteSource` may delete already copied subtrees before later failures; delete may return false with partial deletion. Shell delegation must quote paths correctly; `makeSecureShellPath` is Unix-only. Java archive extraction protects against traversal, but the non-Windows `tar` path relies on platform tar behavior. Permission logic differs by platform and native availability. `copy(FileSystem, FileStatus, ...)` does not use the return value of recursive child copies, so callers rely on exceptions for child failures.

Test signals: cover symlink deletion semantics, recursive copy/delete partial failures, `checkDest` overwrite and directory cases, archive traversal rejection, UNIX mode restoration, Windows permission and symlink branches, classpath wildcard expansion, URI host canonicalization in `compareFs`, `maybeIgnoreMissingDirectory` with `DIRECTORY_LISTING_INCONSISTENT`, and EC capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFileSystem.java

Purpose: `FilterFileSystem` is the stable public wrapper base class for decorating an old-style `FileSystem`. By default it delegates nearly every operation to a contained `FileSystem`, allowing subclasses to intercept behavior selectively without reimplementing the full API.

Important APIs: constructors, `getRawFileSystem`, `initialize`, `makeQualified`, `checkPath`, open/create/append/rename/delete/list methods, working directory and status methods, checksum, symlink, ACL, xattr, snapshot, storage policy, trash, builder, async open, and capability APIs.

Control flow and state: the wrapper stores `protected FileSystem fs` and optional `swapScheme`. `initialize` initializes the wrapped filesystem if needed and records a scheme replacement when wrapper and wrapped schemes differ. `makeQualified` delegates then rewrites the scheme when `swapScheme` is set. Most methods forward directly; `close` closes both super and wrapped fs. `hasPathCapability` explicitly masks multipart uploader and experimental batch listing even if the wrapped filesystem reports support.

Dependencies and integration: sits between clients and wrapped `FileSystem` implementations. It preserves shared statistics by copying `fs.statistics`, exposes the child through `getChildFileSystems`, and participates in newer builder APIs via `createFile`, `appendFile`, `openFile`, and `openFileWithOptions`.

Risks: subclasses depend on comprehensive delegation; missing overrides can bypass wrapper behavior. Scheme swapping notes authority handling is imperfect. Capability masking can surprise wrappers that genuinely support multipart or batch listing through subclass logic unless overridden. Closing the wrapper closes the child and can affect shared wrapped instances.

Test signals: verify delegation coverage, initialization of unconfigured children, scheme rewrite behavior, path capability masking, child filesystem reporting, close propagation, and subclass overrides around create/open/delete paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFs.java

Purpose: `FilterFs` is the `AbstractFileSystem` equivalent of `FilterFileSystem`: a private/evolving base for wrapping another `AbstractFileSystem` and forwarding operations so subclasses can transform selected behavior.

Important APIs: constructor over an `AbstractFileSystem`, `getMyFs`, statistics and URI methods, create/delete/status/list/open/mkdir/rename/setters, symlink support, delegation tokens, ACL/xattr/snapshot/storage-policy APIs, async open options, multipart uploader, capabilities, and enclosing-root lookup.

Control flow and state: it stores final `myFs` and initializes its superclass from the wrapped URI/scheme/default port. Most path-affecting methods call `checkPath` before delegation; some methods such as `getFsStatus(Path)`, `resolvePath`, `renameInternal(src,dst,overwrite)`, `createSymlink`, and ACL/xattr methods delegate directly and rely on wrapped implementation validation. No persistent state is introduced beyond the wrapped reference.

Dependencies and integration: used by `DelegateToFileSystem`/`FileContext` paths where `AbstractFileSystem` is the API boundary. It integrates with `Options.ChecksumOpt`, `OpenFileParameters`, ACLs, xattrs, snapshots, storage policies, tokens, and multipart upload builders.

Risks: inconsistent explicit `checkPath` coverage means subclasses relying on wrapper-level path validation may need to override more methods. It preserves wrapped statistics and capabilities exactly, so wrapper-added behavior must be reflected by overrides. Constructor errors propagate as `URISyntaxException`.

Test signals: exercise path validation on create/delete/open/rename, direct delegation methods, capability pass-through, token pass-through, and subclass overrides that enforce transformed URI or authorization semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FilterFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsConstants.java

Purpose: `FsConstants` centralizes stable filesystem constants such as local filesystem URI, FTP scheme, viewfs URI/scheme/type, viewfs overload config-key pattern, and maximum symlink traversal depth.

Important APIs: constants `LOCAL_FS_URI`, `FTP_SCHEME`, package-visible `MAX_PATH_LINKS`, `VIEWFS_URI`, `VIEWFS_SCHEME`, `FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, and `VIEWFS_TYPE`.

Control flow and state: this is an interface constant holder with no runtime behavior, no mutable state, and no persistence. Values are initialized at class loading.

Dependencies and integration: consumed by filesystem resolution, symlink resolution, local FS defaults, FTP integration, and viewfs mount/overload code. Values must remain compatible with URI parsing and config naming across Hadoop modules.

Risks: changing URI or scheme constants breaks configuration and path resolution compatibility. `MAX_PATH_LINKS` bounds recursive symlink resolution; increasing or decreasing it affects loop protection and legitimate deep chains.

Test signals: verify constants used by URI creation, viewfs configuration lookup, and symlink loop handling remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsServerDefaults.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsServerDefaults.java

Purpose: `FsServerDefaults` is a writable value object carrying server-side filesystem defaults to clients: block size, checksum settings, packet size, replication, buffer size, transfer encryption, trash interval, checksum type, key provider URI, storage policy ID, and snapshot trash-root flag.

Important APIs: overloaded constructors, getters for every field, static `WritableFactories` registration, and `Writable.write/readFields`.

Control flow and state: instances hold simple fields. Serialization writes only block size, checksum bytes, write packet size, replication, file buffer size, checksum type, and storage policy ID. It does not serialize `encryptDataTransfer`, `trashInterval`, `keyProviderUri`, or `snapshotTrashRootEnabled` in this implementation, so those values are constructor/runtime only unless carried by other protocol layers.

Dependencies and integration: used by `FileSystem.getServerDefaults`, clients creating files, HDFS protocol adapters, `DataChecksum.Type`, and Hadoop `Writable` factories.

Risks: writable compatibility is delicate because omitted fields may appear default after round-trip. Constructors chain defaults, so additions must preserve old behavior. Null/empty key provider URI has semantic meaning for encryption-zone support.

Test signals: round-trip writable tests, constructor default tests, checksum enum serialization, key provider semantics, storage policy ID propagation, and compatibility with older clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsServerDefaults.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsShell.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsShell.java

Purpose: `FsShell` is the command-line entry point for `hadoop fs`. It initializes command registration, routes commands, prints usage/help, manages a default `FileSystem` and `Trash`, and wraps command execution in HTrace spans.

Important APIs: constructors, `getFS`, `getTrash`, `getHelp`, `init`, `registerCommands`, `getCurrentTrashDir`, inner `Usage` and `Help`, `run`, `close`, `main`, `newShellInstance`, and `UnknownCommandException`.

Control flow and state: `init` sets quiet mode, configures `UserGroupInformation`, creates a `CommandFactory`, registers `-help`, `-usage`, and normal `FsCommand` classes. `run` validates argv, looks up the command, starts a tracer scope, truncates traced args to 2048 characters, invokes `Command.run`, handles illegal arguments with usage output, handles unexpected exceptions as fatal internal errors, closes the tracer, and returns the command exit code. `fs`, `trash`, `help`, and `commandFactory` are lazy instance state.

Dependencies and integration: integrates with Hadoop `ToolRunner`, `Configured`, `CommandFactory`, `FsCommand`, `TableListing`, `Trash`, `UserGroupInformation`, `Tracer`, `TraceUtils`, and generic command option printing.

Risks: command registration changes affect all CLI behavior. Error display assumes non-empty command strings. `run` catches broad exceptions after command-level IO handling, so fatal paths print stack traces to stderr. `close` closes the cached filesystem, which may affect shared caches depending on underlying FS behavior.

Test signals: no-arg usage, unknown command hints with missing dash, help/usage formatting and wrapping, command registration in subclasses, tracer arg truncation, exit codes for success/argument/fatal paths, and cleanup via `close`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsShellPermissions.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsShellPermissions.java

Purpose: `FsShellPermissions` hosts `-chmod`, `-chown`, and `-chgrp` shell commands separate from the main shell class.

Important APIs: `registerCommands`, nested `Chmod`, `Chown`, and `Chgrp`, `processOptions`, `processPath`, and owner/group parsing helpers. `Chmod` uses `ChmodParser`; `Chown` and `Chgrp` use regex validation with platform-specific allowed characters.

Control flow and state: each command parses `-R`, validates the first non-option argument, then walks path arguments through `FsCommand` mechanics. `Chmod.processPath` computes a new permission and calls `setPermission` only when it changes. `Chown.processPath` sends null for unchanged owner/group so filesystem implementations mutate only needed fields. Command instances keep parsed owner/group/parser state for the run.

Dependencies and integration: integrates with `CommandFactory`, `CommandFormat`, `PathData`, `FsPermission`, `ChmodParser`, `Shell.WINDOWS`, and the active filesystem behind each `PathData`.

Risks: regex differences between Windows and Unix affect accepted names. The chmod error message intentionally retains legacy prefixing. Local filesystems using shell `chown` can interpret dotted usernames unexpectedly, as documented. Recursive behavior is delegated to `FsCommand`.

Test signals: mode parser acceptance/rejection, octal sticky-bit forms, recursive option handling, unchanged-permission no-ops, owner/group parsing including empty owner or group, Windows spaces in names, and error message compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsShellPermissions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsStatus.java

Purpose: `FsStatus` is a stable writable value object representing filesystem capacity, used bytes, and remaining bytes.

Important APIs: constructor, `getCapacity`, `getUsed`, `getRemaining`, `write`, and `readFields`.

Control flow and state: it stores three longs and serializes them in fixed order. `readFields` mutates an existing object from a `DataInput`; there is no validation on negative or inconsistent values.

Dependencies and integration: returned by `FileSystem.getStatus`/`AbstractFileSystem.getFsStatus` and serialized through Hadoop `Writable` pathways.

Risks: callers must interpret values from the filesystem correctly; this class does not enforce `capacity == used + remaining` or non-negative numbers. Writable field order is a compatibility contract.

Test signals: writable round-trip, large long values, zero/negative edge inputs if upstream permits them, and integration with `df`/status shell commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsTracer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsTracer.java

Purpose: `FsTracer` provides the singleton HTrace `Tracer` used by filesystem client operations.

Important APIs: synchronized static `get(Configuration)` and private constructor.

Control flow and state: the first `get` call builds a `Tracer` named `FSClient` from `CommonConfigurationKeys.FS_CLIENT_HTRACE_PREFIX`; subsequent calls return the same static instance regardless of later configurations. There is no explicit close or reset method here.

Dependencies and integration: used by `Globber` and filesystem APIs needing tracing, with configuration wrapped through `TraceUtils`.

Risks: singleton configuration is first-writer-wins, which can surprise tests or applications with multiple configurations. Global lifecycle is intentionally a workaround for `FileContext`/DFSClient creation patterns.

Test signals: singleton reuse, trace prefix configuration on first call, concurrency around first initialization, and no accidental tracer recreation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsTracer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlConnection.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlConnection.java

Purpose: `FsUrlConnection` adapts Java `URLConnection` to Hadoop `FileSystem` reads so registered URL protocols can return Hadoop-backed input streams.

Important APIs: constructor, `connect`, and `getInputStream`.

Control flow and state: it stores `Configuration` and a single `InputStream`. `connect` rejects double connects, converts the `URL` to a `URI`, resolves the `FileSystem`, and opens a `Path`. Opaque relative `file:` URIs use the scheme-specific part because `URI#getPath` is null for those forms. `getInputStream` lazily connects.

Dependencies and integration: created by `FsUrlStreamHandler`, uses `FileSystem.get(uri, conf)`, `Path`, and precondition checks.

Risks: the connection owns an input stream but does not override close; callers must close the returned stream. Double `connect` is illegal. URI syntax errors become `IOException`.

Test signals: normal HDFS/file URL open, opaque relative file URL handling, lazy connection, double-connect failure, null argument preconditions, and unknown filesystem scheme behavior via the factory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlConnection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandler.java

Purpose: `FsUrlStreamHandler` is the package-private `URLStreamHandler` that creates Hadoop filesystem URL connections.

Important APIs: constructors with default or supplied `Configuration`, and `openConnection(URL)`.

Control flow and state: it stores one configuration reference and creates a new `FsUrlConnection` for each URL. There is no caching or protocol dispatch here; protocol support is decided by the factory.

Dependencies and integration: used by `FsUrlStreamHandlerFactory` and Java URL handling.

Risks: a default constructor creates a fresh `Configuration`, which may not match an application's configured filesystem mappings. Configuration is shared by all connections from the handler.

Test signals: handler opens connections with supplied configuration, default configuration behavior, and compatibility with factory-cached singleton handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandlerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandlerFactory.java

Purpose: `FsUrlStreamHandlerFactory` exposes Hadoop filesystem schemes as Java URL protocols while deliberately avoiding standard JVM protocols.

Important APIs: `UNEXPORTED_PROTOCOLS`, constructors, and `createURLStreamHandler`.

Control flow and state: the constructor copies the configuration, forces FileSystem initialization by resolving `file`, creates one handler, and seeds `http`/`https` as unsupported. `createURLStreamHandler` caches whether each protocol has a `FileSystem` implementation in a `ConcurrentHashMap`; known protocols return the shared handler and unknown protocols return null to delegate to the JVM.

Dependencies and integration: integrates Java `URLStreamHandlerFactory`, `FileSystem.getFileSystemClass`, and `FsUrlStreamHandler`.

Risks: protocol support is cached, so runtime config changes after first lookup are not reflected. Returning a shared handler means one configuration is used for all supported protocols. Exporting `http`/`https` would break JVM behavior, so the denylist must remain.

Test signals: known Hadoop schemes return a handler, unknown schemes return null, http/https stay unexported, FileSystem initialization failure becomes runtime exception, and concurrent protocol lookups are stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsUrlStreamHandlerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FutureDataInputStreamBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FutureDataInputStreamBuilder.java

Purpose: `FutureDataInputStreamBuilder` defines the asynchronous open builder contract for `FSDataInputStream`.

Important APIs: inherited `FSBuilder` option methods, `build()` returning `CompletableFuture<FSDataInputStream>`, and default `withFileStatus(@Nullable FileStatus)`.

Control flow and state: this is an interface; implementations own option state. The default `withFileStatus` is a no-op so implementations opt in to using caller-provided status hints.

Dependencies and integration: used by `FileSystem.openFile`, `FileContext` opens, and utility copy methods that provide file length/status hints for object stores and async implementations.

Risks: `must` options are expected to throw for unsupported/unknown options, while `opt` options may be ignored; implementations must preserve that distinction. A provided `FileStatus` can become stale, so implementations must decide whether to trust it.

Test signals: async build success/failure paths, option validation semantics, no-op default `withFileStatus`, stale status handling in implementations, and cancellation/exception propagation through `CompletableFuture`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FutureDataInputStreamBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GetSpaceUsed.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GetSpaceUsed.java

Purpose: `GetSpaceUsed` is a pluggable interface for reporting local directory space usage, with a builder that chooses DU or Windows implementation by platform/configuration.

Important APIs: `getUsed`, nested `Builder`, configuration/path/class/interval/jitter/initialUsed/constructor setters and getters, and `build`.

Control flow and state: `Builder` resolves defaults from `CommonConfigurationKeys`, selects `WindowsGetSpaceUsed` on Windows or `DU` elsewhere unless overridden, reflectively constructs a class with a `Builder` constructor, falls back to platform default on reflection failure, and calls `init` when the result is `CachingGetSpaceUsed`.

Dependencies and integration: used by disk usage monitors and local storage accounting. It depends on `Configuration`, `Shell`, `DU`, `WindowsGetSpaceUsed`, and `CachingGetSpaceUsed`.

Risks: reflection errors are logged and silently fall back, which can mask misconfiguration. `path` is not validated in the builder itself. Constructor caching through `cons` can interact badly if callers mutate `klass` afterward.

Test signals: default class selection per platform, configured class override, fallback on bad constructor, interval/jitter config defaults, initial used sentinel `-1`, and `CachingGetSpaceUsed.init` invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobExpander.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobExpander.java

Purpose: `GlobExpander` rewrites path glob patterns so brace groups containing slashes are expanded into multiple path patterns before per-component glob matching.

Important APIs: public static `expand(String)`, internal `StringWithOffset`, `expandLeftmost`, and `leftmostOuterCurlyContainingSlash`.

Control flow and state: `expand` maintains a queue of patterns, repeatedly expanding the leftmost outer brace group that contains `/`, and emits fully expanded patterns when no such group remains. Escaped characters are consumed and validated; malformed trailing escapes throw `IOException`. No persistent state exists.

Dependencies and integration: called by `Globber.doGlob` before splitting paths into components, enabling brace alternatives that cross directory boundaries.

Risks: expansion can grow combinatorially with nested brace alternatives. Only brace groups containing slash are expanded here; other brace semantics are handled later by `GlobPattern`. Escaped-character handling must remain aligned with glob matching.

Test signals: examples with nested braces, slash-containing alternatives, escaped slash/characters, malformed trailing backslash, groups without slash, and ordering of expanded patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobExpander.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobFilter.java

Purpose: `GlobFilter` is a `PathFilter` that applies a POSIX-like glob pattern to a path's final name and optionally chains a caller-provided filter.

Important APIs: constructors, `init`, `hasPattern`, and `accept`.

Control flow and state: initialization compiles a `GlobPattern` and stores the user filter. RE2/J `PatternSyntaxException` is wrapped as an `IOException` with the legacy `Illegal file pattern` prefix. `accept` matches only `path.getName()` and then invokes the user filter on the full path.

Dependencies and integration: used by `Globber` for component matching and by callers needing reusable glob-based filtering.

Risks: matching only the final component is intentional; callers expecting full-path matching must use `Globber`. Null user filters are not guarded here. Pattern syntax compatibility depends on `GlobPattern` and RE2/J.

Test signals: wildcard detection, name-only matching, user filter chaining, illegal pattern wrapping, brace/character class behavior, and null-filter expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobPattern.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobPattern.java

Purpose: `GlobPattern` translates POSIX-style glob syntax into an RE2/J regular expression and exposes match/wildcard state.

Important APIs: constructor, `compiled`, static `compile`, `matches`, `set`, `hasWildcard`, and internal `error`.

Control flow and state: `set` scans the glob, appending regex text while tracking open character classes and brace groups. `*` becomes `.` followed by `*` through fallthrough, `?` becomes `.`, braces become non-capturing groups, commas inside braces become alternation, `[!` becomes `[^`, and regex metacharacters not intended as glob syntax are escaped. Unclosed classes/groups and missing escaped chars throw `PatternSyntaxException`.

Dependencies and integration: used by `GlobFilter` and indirectly `Globber`; relies on `com.google.re2j.Pattern` with `DOTALL`.

Risks: subtle fallthrough behavior implements `*` as `.*`; changing it can break glob semantics. Character-class edge cases are partly deferred to the regex compiler. `hasWildcard` drives `Globber` lookup strategy and null-vs-empty semantics.

Test signals: `*`, `?`, braces, commas outside braces, character classes, negated classes, escaped chars, regex metachar escaping, unclosed groups/classes, and `hasWildcard` correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobPattern.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobalStorageStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobalStorageStatistics.java

Purpose: `GlobalStorageStatistics` is a singleton registry of named `StorageStatistics` instances.

Important APIs: enum singleton `INSTANCE`, provider interface `StorageStatisticsProvider`, synchronized `get`, `put`, `reset`, and `iterator`.

Control flow and state: a `TreeMap` stores statistics by name. `put` returns an existing instance or calls the provider, rejecting null providers/results and name mismatches. `reset` calls reset on every registered statistic. Iteration snapshots the current first value then advances by `higherEntry` under synchronization, so it observes map order while tolerating concurrent synchronized modifications.

Dependencies and integration: used by filesystem implementations to publish global counters and by diagnostics/tools that enumerate or reset statistics.

Risks: provider errors are runtime failures. Iterator does not support remove. Because iteration advances by names, concurrent additions/removals may affect what is observed, though map access is synchronized.

Test signals: get null behavior, put idempotence, provider null/wrong-name failures, reset propagation, sorted iteration, no remove support, and synchronized concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/GlobalStorageStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Globber.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Globber.java

Purpose: `Globber` implements `FileSystem.globStatus(Path, PathFilter)` and `FileContext` globbing, including brace expansion, component-wise filesystem traversal, optional symlink disambiguation, tracing, and deterministic result sorting.

Important APIs: constructors for `FileSystem`/`FileContext`, `glob`, `doGlob`, helper status/list/fixRelative/scheme/authority methods, `createGlobber`, and nested `GlobBuilder` with path pattern, path filter, and symlink resolution controls.

Control flow and state: `glob` opens a trace scope and delegates to `doGlob`. `doGlob` resolves scheme/authority, expands slash-containing brace groups, turns each flattened pattern into absolute components, seeds traversal at root, and iteratively builds candidate `FileStatus` lists. Non-terminal literal components are optimistically appended until a later stat/list is needed. Glob components list candidate directories, disambiguate one-entry listings when symlink resolution is enabled, filter children by `GlobFilter`, and avoid recursing into files. Final user filtering is applied only to complete paths. No matches for a plain non-wildcard single pattern returns null; other misses return an empty sorted array.

Dependencies and integration: integrates with `FileSystem`, `FileContext`, `GlobExpander`, `GlobFilter`, `FsTracer`, `TraceScope`, and `DurationInfo`. It is central to shell and API glob semantics.

Risks: object stores with inconsistent listings can surface warnings/misses. Symlink resolution adds extra status calls; disabling it changes one-entry listing semantics. The builder method name `withPathFiltern` appears misspelled but is the exposed API here. Null `filter` would fail at final accept unless callers supply a default upstream.

Test signals: wildcard and non-wildcard misses, root and Windows drive patterns, hidden HDFS directories like `.snapshot`, symlink one-entry disambiguation, object-store deleted directory behavior, result sorting, brace expansion ordering, and builder symlink toggle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/Globber.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFileSystem.java

Purpose: `HarFileSystem` implements the read-only Hadoop Archive (`har`) filesystem. It maps logical paths inside a `.har` archive to byte ranges inside underlying `part-*` files using `_masterindex` and `_index` metadata.

Important APIs: `initialize`, `getScheme`, `getHarVersion`, URI/path helpers, `makeQualified`, `getFileBlockLocations`, `getFileStatus`, `open`, `listStatus`, read-only mutator overrides, `hasPathCapability`, `HarFSDataInputStream`, `HarMetaData`, and metadata cache configuration constants.

Control flow and state: initialization decodes `har://underlying-scheme-host/path` into an underlying filesystem URI, finds the archive path ending in `.har`, validates `_masterindex` and `_index`, and loads or refreshes static LRU metadata keyed by archive URI based on index modification timestamps. Metadata parsing reads hash ranges from `_masterindex`, seeks ranges in `_index`, builds a map of internal paths to `HarStatus`, and caches part-file statuses. `getFileStatus` and `listStatus` synthesize statuses from index entries plus underlying part/index file metadata. `open` wraps the underlying part file stream in a bounded stream that fakes EOF at the archived file's byte range and adjusts positioned reads/seeks. Mutations throw `IOException`; path-handle opens are unsupported.

Dependencies and integration: depends on underlying `FileSystem`, `LineReader`, `Text`, `FileStatus`, `BlockLocation`, `FSDataInputStream`, `FsPermission`, path capability validation, and `FileUtil.copy` for local extraction.

Risks: metadata cache is static and synchronized only around map creation; individual metadata objects can be shared. Index parsing assumes well-formed space-separated lines and uses decoded fields. Permissions/owner/group from HAR v3 metadata are parsed but not applied; synthesized statuses use underlying file metadata. `createFile` and `appendFile` delegate to underlying fs despite the connector being read-only, a surprising inherited-builder surface. `checkPath` delegates to the underlying filesystem and may not fully validate `har` URI semantics.

Test signals: valid/invalid HAR URI decoding, missing index files, metadata cache invalidation on index timestamp change, v1/v2/v3 filename decoding and modification times, file vs directory status/listing, bounded sequential and positioned reads including EOF, block location offset fixing, read-only mutator failures, and `FS_READ_ONLY_CONNECTOR` capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFs.java

Purpose: `HarFs` is the `AbstractFileSystem`/`FileContext` adapter for the `har` scheme.

Important APIs: package-private constructor and `getUriDefaultPort`.

Control flow and state: construction delegates to `DelegateToFileSystem` with a new `HarFileSystem`, scheme `har`, and authority-required flag false. It reports default port `-1`.

Dependencies and integration: bridges `FileContext` users to `HarFileSystem`; used through Hadoop filesystem service loading/configuration rather than direct public construction.

Risks: behavior is almost entirely inherited from `DelegateToFileSystem` and `HarFileSystem`, so adapter tests should catch initialization and URI translation regressions. Constructor visibility limits external direct use.

Test signals: `FileContext` resolution of `har` URIs, default port behavior, delegation to read-only HAR operations, and authority-less archive URI handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HarFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HardLink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HardLink.java

Purpose: `HardLink` provides static hard-link creation and link-count utilities with platform-specific fallback commands, plus per-instance counters for clients that track copy/link work.

Important APIs: constructor and `linkStats`, `createHardLink`, `createHardLinkMult`, `supportsHardLink`, `getLinkCount`, `LinkStats.clear`, and `LinkStats.report`.

Control flow and state: static initialization chooses a `HardLinkCommandGetter` based on platform and customizes the link-count command for macOS/FreeBSD/Solaris. Link creation uses Java NIO `Files.createLink`. Link-count retrieval first checks whether the file store supports the UNIX attribute view and reads `unix:nlink`; if not, it executes the platform command and parses output. `LinkStats` is mutable instance state and explicitly not thread-safe.

Dependencies and integration: used by local filesystem utilities and archive extraction hard-link handling. It depends on `Shell`, `ShellCommandExecutor`, Java NIO file attributes, `FileUtil.makeShellPath`, and `IOUtils`.

Risks: `supportsHardLink` only checks UNIX attribute view, so fallback commands handle other platforms but may depend on winutils or shell utilities. Solaris parses `ls -l` output differently. Static command selection is platform-global. Multi-link creation loops one NIO link per file rather than batching through a shell command.

Test signals: null/missing argument failures, single and multi-link creation, link count via NIO and command fallback, platform-specific command templates, winutils lookup on Windows, Solaris parsing, and `LinkStats` report formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HardLink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasEnhancedByteBufferAccess.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasEnhancedByteBufferAccess.java

Purpose: `HasEnhancedByteBufferAccess` marks input streams that can return direct/enhanced `ByteBuffer` reads, often mmap-backed, with explicit release semantics.

Important APIs: `read(ByteBufferPool, int, EnumSet<ReadOption>)` and `releaseBuffer(ByteBuffer)`.

Control flow and state: as an interface it defines the contract only. Implementations may allocate buffers from the stream itself or use a provided pool. `maxLength == 0` must return an empty buffer; positive reads return null at EOF; returned buffers must be released by callers.

Dependencies and integration: implemented by `FSDataInputStream` internals and filesystem-specific streams that support zero-copy or pooled reads. Uses `ByteBufferPool` and `ReadOption`.

Risks: buffer lifecycle is critical: callers must not use buffers after release, and streams may warn/leak if buffers remain unreleased at close. Passing a null factory can force `UnsupportedOperationException` when fallback allocation is needed.

Test signals: zero-length read, EOF null, pooled fallback, null-factory unsupported path, release idempotence/validation in implementations, close-with-unreleased-buffer behavior, and option handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasEnhancedByteBufferAccess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasFileDescriptor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasFileDescriptor.java

Purpose: `HasFileDescriptor` marks streams or wrappers that can expose an underlying Java `FileDescriptor`.

Important APIs: `getFileDescriptor`.

Control flow and state: interface-only contract; implementations decide whether the descriptor is live, duplicate, or tied to stream lifetime.

Dependencies and integration: used by local/native IO paths and consumers needing descriptor-level operations.

Risks: exposing descriptors can bypass stream abstractions and interacts with close semantics. Implementations must throw `IOException` when unavailable rather than returning invalid descriptors.

Test signals: descriptor availability before/after close, unsupported stream behavior, native/local stream integration, and caller handling of `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasFileDescriptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InternalOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InternalOperations.java

Purpose: `InternalOperations` exposes package-scoped `FileSystem` operations to implementation packages such as `org.apache.hadoop.fs.impl` without making them public API.

Important APIs: `rename(FileSystem, Path, Path, Options.Rename...)`.

Control flow and state: it simply calls the protected/deprecated `FileSystem.rename(src,dst,options)` method. It holds no state.

Dependencies and integration: used by Hadoop filesystem implementation code that needs access to rename-with-options behavior while preserving API boundaries.

Risks: this is intentionally not for applications; broader use would couple external code to internal compatibility shims. It suppresses deprecation because Hadoop still needs the protected API for selected flows.

Test signals: rename option propagation, overwrite behavior, exception propagation, and visibility/use from implementation packages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InternalOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathException.java

Purpose: `InvalidPathException` reports invalid Hadoop path strings or filesystem-specific path validation failures.

Important APIs: constructors accepting `path` and optional `reason`.

Control flow and state: extends `HadoopIllegalArgumentException`, formats a stable message, and carries only exception state. Null reason is omitted from the formatted message.

Dependencies and integration: thrown by path parsing/validation code and public filesystem APIs where invalid input is a caller argument error.

Risks: message text can be asserted by tests or users. It is unchecked via Hadoop's illegal argument type, so callers may not catch it as `IOException`.

Test signals: message formatting with and without reason, invalid characters, scheme-specific path validation, and compatibility with public API error expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathHandleException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathHandleException.java

Purpose: `InvalidPathHandleException` reports that constraints encoded in a `PathHandle` no longer hold when opening or resolving a handle.

Important APIs: constructors with message and message/cause.

Control flow and state: extends `IOException` with a fixed serial version. It carries only normal exception state.

Dependencies and integration: used by `FileSystem.open(PathHandle)` and implementations honoring `Options.HandleOpt` constraints such as path identity or content identity.

Risks: callers must distinguish invalid handles from missing files and other IO failures. Implementations need to preserve causes for diagnostics.

Test signals: stale/mismatched path handles, cause propagation, open-by-handle failure modes, and compatibility with handle option semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidPathHandleException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidRequestException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidRequestException.java

Purpose: `InvalidRequestException` reports malformed user requests, such as missing required parameters or invalid parameter values, using checked IO exception semantics.

Important APIs: constructors with message and message/cause.

Control flow and state: simple `IOException` subclass with serial version `0L`; no additional fields or behavior.

Dependencies and integration: used by filesystem APIs that validate request objects/options and want callers to handle the failure as an IO-level request error.

Risks: broad checked type may be caught with generic IO failures, so messages and causes are important for diagnostics. No Hadoop classification annotations are present in this file.

Test signals: malformed builder/request validation, cause propagation, message stability, and caller differentiation from unsupported options or illegal arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/InvalidRequestException.java -->
