# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.21.0.xml lines 1-5864

## Purpose and scope

This chunk is the opening portion of the generated JDiff API snapshot for `hadoop-core 0.21.0`. The file is XML produced by the JDiff Javadoc doclet, using `api.xsd`, and records public/protected Java API surface, type hierarchy, signatures, visibility, deprecation text, exceptions, fields, and Javadoc bodies. It is not executable Hadoop code; its purpose is API compatibility research and release comparison for Hadoop Common/Core.

The chunk covers the API header and these packages/classes:

- `org.apache.hadoop`: `HadoopIllegalArgumentException`.
- `org.apache.hadoop.classification`: audience and stability annotation marker types.
- `org.apache.hadoop.conf`: `Configurable`, `Configuration`, `Configuration.IntegerRanges`, `Configured`, and `ConfServlet.BadFormatException`.
- `org.apache.hadoop.fs`: starts at `AbstractFileSystem` and runs through `FileSystem`, `FileSystem.Statistics`, and the beginning of `FileUtil.copyMerge`. The chunk ends inside the `FileUtil.copyMerge` documentation block, so later `FileUtil` API is unresolved in this chunk.

## Important APIs and types

### Common and classification

`HadoopIllegalArgumentException` is a public Hadoop-specific subclass of `IllegalArgumentException`, used to distinguish invalid argument failures thrown by Hadoop implementation from JDK-originated `IllegalArgumentException`.

`InterfaceAudience` and `InterfaceStability` define annotation classes that document intended consumers and compatibility expectations. Audience values include `Public`, `LimitedPrivate`, and `Private`; stability values include `Stable`, `Evolving`, and `Unstable`. These markers are important for API consumers and for tooling such as the ExcludePrivateAnnotations JDiff doclet that generated this file.

### Configuration APIs

`Configurable` is the small contract for types that accept and expose a `Configuration` through `setConf(Configuration)` and `getConf()`. `Configured` is the base implementation holding a `Configuration`.

`Configuration` is a central mutable property container and implements `Iterable` plus Hadoop `Writable`. The API exposes:

- Construction with defaults enabled, defaults disabled, or cloned from another `Configuration`.
- Static deprecation-map management through synchronized `addDeprecation(...)`, plus synchronized `addDefaultResource(String)`.
- Resource loading from classpath names, URLs, `Path`, and `InputStream`.
- Lazy reloading via synchronized `reloadConfiguration()`, which clears resource-loaded values and final-parameter state while preserving explicitly set overlays.
- Typed getters/setters for strings, ints, longs, floats, booleans, enums, regex patterns, integer ranges, comma-delimited string collections, class names, class arrays, and instantiated implementation lists.
- Class loading and interface-constrained class validation through `getClassByName`, `getClass`, `getClasses`, `getInstances`, and `setClass`.
- Local path/file selection from configured directory lists, choosing a directory based on path hash and creating it if needed.
- Resource accessors returning `URL`, `InputStream`, or `Reader`.
- Serialization and diagnostics through `readFields`, `write`, `writeXml(OutputStream)`, synchronized `writeXml(Writer)`, static `dumpConfiguration(Configuration, Writer)`, `iterator()`, `size()`, `clear()`, `main(String[])`, and quiet-mode controls.

The `Configuration` class documentation defines the key control rules: resources are loaded in order; later resources override earlier ones unless a value was marked final; default resources are `core-default.xml` and `core-site.xml` unless disabled; values undergo variable expansion against other configuration keys and then Java system properties. Deprecated keys map to replacement keys for both read and write paths.

`Configuration.IntegerRanges` parses strings such as `2-3,5,7-` into positive integer ranges and exposes `isIncluded(int)` plus `toString()`.

### File-system abstraction layer

`AbstractFileSystem` is the lower-level protected API behind `FileContext`. It is abstract and validates URI scheme/authority/path ownership, tracks filesystem statistics, and declares filesystem operations using fully qualified `Path` values and already-applied permissions. Key contracts include `create`/`createInternal`, `mkdir`, `delete`, `open`, `setReplication`, `rename`/`renameInternal`, symlink methods, permission/owner/time mutation, checksum/status/block-location queries, filesystem status, listing, and checksum verification toggles. Many methods mirror `FileContext` but explicitly state that paths must belong to this filesystem and permissions are absolute after umask application.

`AvroFSInput` adapts Hadoop file inputs to Avro-style input semantics. It can be constructed from an `FSDataInputStream` plus length, or from `FileContext` and `Path`, and exposes `length`, byte-range `read`, `seek`, `tell`, and `close`.

`BlockLocation` is a writable metadata object for block hostnames, storage names, topology paths, offset, and length. It supports getters/setters, `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.

`ChecksumException` is an `IOException` with a position accessor, used to report checksum failures at a specific file offset.

`ChecksumFileSystem` is a `FilterFileSystem` that layers client-side checksum files over a raw filesystem. It exposes checksum filename detection and sizing, raw filesystem access, checksum byte sizing, verified `open`, append/create wrappers, checksum-aware rename/delete/listing/copy/local-output behavior, and `reportChecksumFailure(...)`. Its documentation states that it creates one checksum file per raw file and generates/verifies checksums on the client side.

`ContentSummary` is a `Writable` for directory/file aggregate metadata: length, directory count, file count, namespace quota, space consumed, and space quota. It serializes with `write/readFields` and renders quota-aware or non-quota output via `getHeader(boolean)` and `toString(boolean)`.

`CreateFlag` is an enum representing file creation semantics: create, append, overwrite, and valid combinations. The docs describe `CREATE + APPEND` as create-if-missing or append-if-present, and `OVERWRITE` combined with either create or append as overwrite behavior.

`FileAlreadyExistsException` is an `IOException` used when a target exists and overwrite is not configured.

`FileChecksum` is an abstract `Writable` describing checksum algorithm name, byte length, and checksum bytes, with equality/hash based on algorithm and value.

### FileContext APIs

`FileContext` is a final application-facing filesystem context. Static factories create contexts from default configuration, local filesystem, explicit URI, explicit `Configuration`, or an `AbstractFileSystem`. The class tracks default filesystem, working directory, and umask, and resolves three path forms: fully qualified URI, slash-relative path against the default filesystem, and working-directory-relative path. Relative paths with a scheme are documented as illegal.

The main operations include:

- Path qualification with `makeQualified`.
- File creation with `EnumSet<CreateFlag>` and `Options.CreateOpts`.
- Directory creation with permissions and `createParent`.
- Delete, open, replication, rename, permission, owner, time, checksum, status, link-target, block-location, filesystem-status, symlink, listing, delete-on-exit, and path resolution methods.
- Access to `FileContext.Util`, which provides utility operations layered on the base operations.

The FileContext documentation makes a clear state split: FileContext keeps namespace context and umask, while individual filesystem instances supply server-side defaults such as home directory, initial working directory, replication, block size, buffer size, and bytes-per-checksum.

`FileContext.FSLinkResolver<T>` is a helper for operations that may cross symlinks and filesystems. Subclasses implement `next(AbstractFileSystem, Path)`, while `resolve(FileContext, Path)` repeatedly invokes it until symlinks are resolved.

`FileContext.Util` provides non-atomic library operations over `FileContext`: existence checks, content summaries, list-status overloads with filters and path arrays, glob-status overloads with the same Hadoop glob grammar as `FileSystem`, and copy operations with delete-source/overwrite flags. Its docs explicitly warn that these library functions are not atomic and may partially complete when other threads modify the same namespace.

### File status and classic FileSystem APIs

`FileStatus` is a `Writable` and `Comparable` carrying client-side metadata: length, file/directory/symlink classification, block size, replication, modification/access time, permission, owner, group, path, and optional symlink target. It serializes via `write/readFields`. `compareTo`, `equals`, and `hashCode` are path-based. The old `isDir()` API is deprecated in favor of `isFile()`, `isDirectory()`, and `isSymlink()`.

`FileSystem` is the classic abstract, configured filesystem base class and implements `Closeable`. Its static factory and cache surface includes `get(...)`, `newInstance(...)`, `newInstanceLocal(...)`, `getLocal(...)`, `getDefaultUri`, `setDefaultUri`, `closeAll`, and deprecated `getNamed`. The scheme-to-implementation lookup is through the `fs.<scheme>.class` configuration key, and `initialize(URI, Configuration)` receives the full URI.

`FileSystem` defines extensive data-path operations:

- Qualification and path validation: `makeQualified`, protected `checkPath`.
- Block and server defaults: `getFileBlockLocations`, `getServerDefaults`, `getDefaultBlockSize`, `getDefaultReplication`.
- Stream APIs: abstract `open(Path,int)`, many `create` overloads, abstract permission-aware `create`, protected `primitiveCreate`, and append overloads.
- Directory APIs: static permission-exact `mkdirs(FileSystem, Path, FsPermission)`, abstract `mkdirs(Path, FsPermission)`, protected `primitiveMkdir` variants, and default-permission `mkdirs(Path)`.
- Mutation APIs: `rename`, protected transition `rename(Path,Path,Options.Rename...)`, `delete`, `deleteOnExit`, `processDeleteOnExit`, `setReplication`, `setPermission`, `setOwner`, `setTimes`, and `setVerifyChecksum`.
- Query APIs: `exists`, `isDirectory`, `isFile`, deprecated `getLength`/`getBlockSize`/`getReplication`, `getContentSummary`, `listStatus` overloads, `globStatus` overloads, `getHomeDirectory`, working-directory APIs, `getFileStatus`, `getFileChecksum`, `getStatus`.
- Local transfer helpers: copy/move from local, copy/move to local, start/complete local output.
- Lifecycle and accounting: `close`, `getUsed`, static statistics accessors, `clearStatistics`, and `printStatistics`.

`FileSystem.Statistics` tracks bytes read and bytes written per URI scheme. It exposes increment, readback, reset, `toString`, and `getScheme`. `FileSystem` and `AbstractFileSystem` both share statistics concepts.

`FileUtil` begins in this chunk. Covered APIs include `stat2Paths`, `fullyDelete`, `fullyDeleteContents`, deprecated filesystem recursive `fullyDelete`, `copy` overloads between `FileSystem` instances, and the signature start of `copyMerge`. The `copyMerge` documentation is cut off by the chunk boundary.

## Control flow and behavior encoded by the API

The XML has no method bodies, but the documented contracts imply control flow:

- `Configuration` loads resources lazily and in order, applies final-parameter restrictions, maps deprecated keys to replacements, expands variables on read, and overlays explicit `set*` values over resource-loaded values. `reloadConfiguration()` resets loaded resource state so subsequent access re-reads resources.
- `FileContext` resolves incoming paths against its default filesystem and working directory before dispatching operations to `AbstractFileSystem`. It applies umask before calling lower-level operations documented as receiving absolute permissions.
- `AbstractFileSystem` operations assume fully qualified, ownership-checked paths; many methods mirror `FileContext` but are protected provider-facing hooks.
- `FileSystem` uses configuration-driven implementation lookup and cached or new instances depending on `get` versus `newInstance`. It delegates core operations to abstract provider methods while convenience overloads supply defaults, convert legacy signatures, or add transition support for `FileContext`.
- Symlink-aware `FileContext` operations can route through `FSLinkResolver`, repeatedly resolving unresolved links and potentially crossing filesystem boundaries.
- Utility copy/list/glob/delete operations are layered workflows, not atomic primitives. `FileContext.Util` and `FileUtil` both carry partial-completion risk in their docs.

## State and persistence behavior

Persistent or serialized state is visible through Hadoop `Writable` contracts on `Configuration`, `BlockLocation`, `ContentSummary`, `FileChecksum`, and `FileStatus`. These APIs must remain compatible with Hadoop serialization expectations because the JDiff file is a compatibility baseline.

Runtime state includes:

- `Configuration` resource lists, final-parameter markers, deprecation mappings, explicit key/value overlays, classloader, and quiet-mode setting.
- `FileContext` default filesystem, working directory, and umask.
- `FileSystem` cached instances, delete-on-exit paths, working directory for implementations that still expose it, static default URI configuration keys, and global per-scheme/class statistics.
- `ChecksumFileSystem` checksum policy/state over a raw filesystem, including bytes-per-checksum and checksum-file naming.
- Metadata values in `FileStatus`, `BlockLocation`, and `ContentSummary`, plus `FileSystem.Statistics` counters.

The XML itself is a generated persisted artifact. Its header captures generation time, doclet, classpath, sourcepath, API name, and JDiff version. That makes it sensitive to build environment, doclet filters, annotations, classpath contents, and line ordering.

## Dependencies and integration points

The generated header shows integration with `org.apache.hadoop.classification.tools.ExcludePrivateAnnotationsJDiffDoclet`, JDiff `1.0.9`, Ant/Ivy-era dependency resolution, Hadoop Common build classes, and `api.xsd`.

The API surface integrates with:

- Java core types: `URI`, `URL`, `IOException`, `FileNotFoundException`, `URISyntaxException`, `Closeable`, `Iterable`, `Comparable`, `ClassLoader`, `Pattern`, `EnumSet`, `DataInput`, `DataOutput`, `InputStream`, `Reader`, `Writer`, `OutputStream`, and Java annotation interfaces.
- Hadoop Common: `Path`, `FileStatus`, `FileSystem`, `AbstractFileSystem`, `FileContext`, `FsServerDefaults`, `FsStatus`, `Options`, `CreateFlag`, `PathFilter`, `FSDataInputStream`, `FSDataOutputStream`, `FsPermission`, `Progressable`, `Writable`, and Hadoop security exceptions such as `AccessControlException`.
- Avro: `AvroFSInput` adapts Hadoop file streams to Avro input patterns.
- Commons Logging: `FileContext.LOG` and `FileSystem.LOG` fields are part of the public/protected API snapshot.

## Risks and compatibility concerns

- Because this is a JDiff baseline, changing any documented signature, visibility, exception declaration, field, deprecation marker, or doclet filtering rule can appear as an API compatibility change even if implementation behavior is unchanged.
- The chunk includes numerous transition APIs between `FileSystem` and `FileContext`, including protected `primitiveCreate`, `primitiveMkdir`, and protected rename with options. These are explicitly temporary/transition-oriented in documentation, which increases compatibility risk for downstream subclasses.
- Filesystem semantics have implementation-dependent edge cases: rename atomicity, symlink support, checksum support, block locations, status capacity, default server settings, and permissions may differ by filesystem provider.
- `FileContext.Util` and `FileUtil` utility operations are documented as non-atomic and partially completing on concurrent namespace mutation; tests should not assume all-or-nothing behavior.
- Several methods are deprecated but still present: `FileStatus.isDir`, `FileSystem.getName`, `getNamed`, one-argument `delete`, old replication/block-size/length getters, and `getStatistics()` returning a map. Removing or changing them would break API compatibility for 0.21 consumers.
- `Configuration` has subtle compatibility risks around deprecated key forwarding, final parameters, variable expansion, resource ordering, and synchronized static mutation after resource loading. These are core behaviors for Hadoop deployments.
- The chunk ends mid-`FileUtil.copyMerge`; any whole-file analysis must merge this with the following chunk to avoid truncating `FileUtil` coverage.

## Test signals

Useful validation signals for this chunk are mostly API and behavior compatibility tests:

- JDiff or equivalent API-diff checks comparing this XML against regenerated output for the same source tree should be stable except for intentionally changed API/doc content.
- Unit tests for `Configuration` should cover resource ordering, `final` properties, deprecated key mapping, typed getter default behavior, variable expansion, reload semantics, XML/Writable serialization, class loading, and quiet mode.
- Filesystem contract tests should exercise both `FileSystem` and `FileContext` path qualification, working-directory behavior, umask application, create flags, mkdir parent semantics, rename overwrite behavior, delete recursion, symlink resolution, status/list/glob operations, checksum toggling, and exception mapping.
- Serialization tests should round-trip `BlockLocation`, `ContentSummary`, `FileStatus`, `FileChecksum` subclasses, and `Configuration` through `Writable` APIs.
- Utility tests should check partial-completion and overwrite/delete-source semantics for `FileContext.Util.copy`, `FileUtil.copy`, and recursive delete helpers, using both local and non-local/mock filesystem implementations.
- Statistics tests should verify per-scheme/class `FileSystem.Statistics` counters, reset behavior, global clear/print paths, and byte increments from stream operations.

## Cross-chunk notes

This chunk starts the file and is complete through most of the foundational configuration and filesystem API surface, but it stops inside the `FileUtil.copyMerge` method documentation. The merge lane should combine this with the next chunk before producing the final per-file report so the remaining `FileUtil` APIs and later packages are not omitted.
