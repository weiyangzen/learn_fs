# Research: subset-b-007351

This grouped report covers the Hadoop `org.apache.hadoop.fs.viewfs` files assigned to `subset-b-007351`. Each section is bounded by the exact source markers required by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFileSystem.java

`ChRootedFileSystem` is a private `FilterFileSystem` wrapper that makes a target `FileSystem` appear rooted at a configured URI path. It is the concrete target wrapper used by `ViewFileSystem` links: view paths are resolved to a remaining path, and this class prefixes that remaining path with the mount target root before delegating to the raw filesystem.

Important state is `myUri`, `chRootPathPart`, `chRootPathPartString`, and `workingDir`. The core API is `fullPath(Path)`, which validates the incoming path with `checkPath` and maps absolute paths to `chRootPathPart + path`, while relative paths are resolved under the chrooted working directory. `stripOutRoot(Path)` is the inverse helper used by viewfs status rewriting and nfly status wrapping. `getMyFs()` exposes the raw target filesystem for operations such as cross-mount rename when the rename policy permits it.

Control flow is intentionally repetitive: create, open, delete, list, ACL, xattr, snapshot, checksum, storage-policy, and capability methods all call `fullPath()` and then delegate to `super` or the wrapped `fs`. This keeps persistence in the underlying filesystem; this wrapper stores only process-local URI and working-directory state. `createFile()` and `openFile()` also prefix paths before returning builder APIs.

Dependencies include Hadoop `FileSystem`, `FilterFileSystem`, `Path`, permission/ACL/xattr types, and `ViewFsFileStatus` for block-location path rewriting. Integration points are `ViewFileSystem.InodeTree` target initialization, `NflyFSystem.NflyNode`, and `ViewFileSystem.getChrootedPath`.

Risks are concentrated in path string concatenation, URI qualification edge cases, and inverse root stripping. Tests should cover root chroot (`/`), non-root chroot, relative working directories, `stripOutRoot` boundary paths, all delegated metadata methods, builder APIs, and rename/status interactions through `ViewFileSystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFs.java

`ChRootedFs` is the `AbstractFileSystem` counterpart to `ChRootedFileSystem`. It wraps an `AbstractFileSystem` and exposes a filesystem rooted below the raw filesystem root. It is used by the newer `ViewFs` API path rather than the older `FileSystem`-based `ViewFileSystem` path.

The key APIs mirror the `FileSystem` wrapper: `fullPath(Path)` prefixes an absolute checked path with `chRootPathPartString`; `stripOutRoot(Path)` removes the chroot prefix from a qualified target path; `getResolvedQualifiedPath(Path)` qualifies a path after chroot expansion; and `getMyFs()` exposes the raw `AbstractFileSystem`. The constructor validates the root against the raw filesystem, derives the URI path with `myFs.getUriPath(theRoot)`, and constructs a URI containing the chrooted path.

Most methods are direct delegations after path expansion: `createInternal`, `delete`, `open`, `mkdir`, `renameInternal`, file status, located listing, ACL/xattr, snapshots, checksums, storage policies, checksum settings, symlink creation, and delegation token retrieval. State is in-memory only: raw filesystem reference, URI, chroot path, and string prefix. Durable data and metadata changes happen in the wrapped filesystem.

Dependencies are Hadoop `AbstractFileSystem`, `Path`, `FileStatus`, `Token`, ACL/xattr/storage policy APIs, and `Options.ChecksumOpt`. Integration is with `ViewFs` and `InodeTree<AbstractFileSystem>` implementations.

Risks include differences from `ChRootedFileSystem`: `satisfyStoragePolicy(Path)` and `getStoragePolicy(Path)` delegate some paths without `fullPath`, so tests should verify intended behavior. Symlink semantics are also subtle because the target is chrooted but the link argument is intentionally not rewritten. Test signals should include root and non-root chroots, symlinks, rename across same chroot, ACL/xattr, snapshot paths, and storage policy path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ConfigUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ConfigUtil.java

`ConfigUtil` is a public convenience API for writing and reading viewfs mount-table configuration keys. It centralizes the key layout defined by `Constants`, so callers do not need to manually compose `fs.viewfs.mounttable.<name>.*` properties.

Important APIs include `getConfigViewFsPrefix`, `addLink`, `addLinkMergeSlash`, `addLinkFallback`, `addLinkMerge`, `addLinkNfly`, `addLinkRegex`, `setHomeDirConf`, `getHomeDirValue`, `getDefaultMountTableName`, `isNestedMountPointSupported`, and `setIsNestedMountPointSupported`. `addLinkNfly` supplies a default `minReplication=2,repairOnRead=true` settings string when settings are omitted. `addLinkRegex` embeds optional interceptor settings using `RegexMountPoint.SETTING_SRCREGEX_SEP`.

There is no persistent state in this class; all effects are writes to a supplied `Configuration`. Control flow is simple key assembly with validation for home directory values starting with `/`. Dependencies are `Configuration`, `URI`, `StringUtils`, and the viewfs constants/regex separator.

Integration points are broad: tests and applications can create mount tables programmatically, while `InodeTree` later parses these same keys. The default mount table name feeds `ViewFileSystem.initialize` when no URI authority is provided.

Risks are mostly compatibility and formatting risks: `Arrays.toString(targets)` for merge links must remain parseable by `StringUtils.getStrings`, nfly settings must match `NflyFSystem.NflyKey`, regex settings cannot accidentally collide with source regex syntax, and invalid home paths fail eagerly. Tests should assert exact generated keys for named and default mount tables, nfly defaults, regex settings serialization, home-dir validation, and nested-mount boolean round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ConfigUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/Constants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/Constants.java

`Constants` is the shared key and default-value contract for viewfs. It defines mount-table prefixes, link key names, feature flags, defaults, and the read-only internal-directory permission used by `ViewFileSystem`.

Important constants include `CONFIG_VIEWFS_PREFIX`, `CONFIG_VIEWFS_MOUNTTABLE_PATH`, `CONFIG_VIEWFS_HOMEDIR`, `CONFIG_VIEWFS_DEFAULT_MOUNT_TABLE_NAME_KEY`, `CONFIG_NESTED_MOUNT_POINT_SUPPORTED`, `CONFIG_VIEWFS_LINK`, `CONFIG_VIEWFS_LINK_FALLBACK`, `CONFIG_VIEWFS_LINK_MERGE`, `CONFIG_VIEWFS_LINK_NFLY`, `CONFIG_VIEWFS_LINK_MERGE_SLASH`, `CONFIG_VIEWFS_LINK_REGEX`, `CONFIG_VIEWFS_RENAME_STRATEGY`, `CONFIG_VIEWFS_ENABLE_INNER_CACHE`, `CONFIG_VIEWFS_MOUNT_LINKS_AS_SYMLINKS`, `CONFIG_VIEWFS_IGNORE_PORT_IN_MOUNT_TABLE_NAME`, `CONFIG_VIEWFS_MOUNTTABLE_LOADER_IMPL`, and `CONFIG_VIEWFS_TRASH_FORCE_INSIDE_MOUNT_POINT`. `PERMISSION_555` is reused when synthetic mount-table directories and symlink-like mount entries are listed.

The interface has no control flow or mutable state, but it strongly shapes runtime behavior in `ConfigUtil`, `InodeTree`, `ViewFileSystem`, `ViewFileSystemOverloadScheme`, and `HCFSMountTableConfigLoader`. The default loader is `HCFSMountTableConfigLoader.class`.

Risks are compatibility risks: changing strings breaks existing core-site.xml deployments, and changing defaults can alter mount listing, caching, trash root, or URI-authority behavior. Tests should treat these constants as wire/configuration contract, checking exact property names and defaults used by parser and helper APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/Constants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/FsGetter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/FsGetter.java

`FsGetter` is a small extension seam for obtaining Hadoop `FileSystem` instances. It exposes `getNewInstance(URI, Configuration)` and `get(URI, Configuration)`, delegating to `FileSystem.newInstance` and `FileSystem.get` respectively.

The class has no state and no persistence behavior. Its purpose is integration flexibility: `ViewFileSystem` uses it when initializing chrooted target filesystems and when deciding whether to use an inner cache; `NflyFSystem` accepts it so tests or overload-scheme code can control how child filesystems are created; `ViewFileSystemOverloadScheme.ChildFsGetter` subclasses it to avoid recursive resolution when an overloaded scheme points at a target with the same scheme.

The main risk is cache semantics. `get` may return shared cached instances while `getNewInstance` returns independent instances, and viewfs code relies on that distinction for lifecycle and loop-avoidance behavior. Tests should use a fake or subclassed `FsGetter` to verify `ViewFileSystem` inner cache behavior, nfly child creation, and overload-scheme target instantiation without coupling tests to global `FileSystem` cache state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/FsGetter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/HCFSMountTableConfigLoader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/HCFSMountTableConfigLoader.java

`HCFSMountTableConfigLoader` implements `MountTableConfigLoader` for mount-table XML files stored on a Hadoop-compatible filesystem. It lets `ViewFileSystemOverloadScheme` load mount-table resources from a configured path before building the in-memory `InodeTree`.

The main API is `load(String mountTableConfigPath, Configuration conf)`. It constructs a `Path`, chooses a child filesystem using `ViewFileSystemOverloadScheme.ChildFsGetter` to avoid overload recursion, lists files directly under the configured path, parses a version number from the penultimate dot-separated filename component, selects the highest version, opens it, loads it into a fresh `Configuration(false)`, and adds that resource into the caller's configuration. Invalid file names and missing valid versions are logged rather than thrown.

State is limited to the last `mountTable` path field during a load call. Persistence is external: versioned XML files are read from the configured filesystem; the in-memory `Configuration` is mutated by `addResource`.

Dependencies include `FileSystem`, `FSDataInputStream`, `RemoteIterator<LocatedFileStatus>`, `Path`, SLF4J, and the overload scheme child getter. Integration point is `ViewFileSystemOverloadScheme.initialize`, gated by `fs.viewfs.mounttable.path`.

Risks include ambiguous file naming, direct-file path handling versus directory listing, lack of strict failure when no file is found, version parsing from names with extra dots, and consistency during concurrent mount-table updates. Tests should cover highest-version selection, invalid names, empty directory warning behavior, configured single path expectations, resource loading, stream closing, and overload-scheme same-scheme target resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/HCFSMountTableConfigLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/InodeTree.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/InodeTree.java

`InodeTree<T>` is the in-memory mount-table engine shared by viewfs implementations. It parses configuration entries into a tree of internal directories and links, resolves input paths to a target filesystem plus remaining path, and supports simple links, fallback links, merge links, merge-slash, nfly links, regex links, and nested mount points.

Important types are `INode`, `INodeDir`, `INodeDirLink`, `INodeLink`, `MountPoint`, `LinkType`, `LinkEntry`, and `ResolveResult`. Subclasses provide `initAndGetTargetFs()`, `getTargetFileSystem(INodeDir)`, and `getTargetFileSystem(String, URI[])`, which allow the same tree logic to produce either `FileSystem` or `AbstractFileSystem` targets. `INodeLink` lazily initializes single-link target filesystems under a lock; merge and nfly targets are created eagerly through the subclass hook. `MountPoint` records source-to-target links for listing and admin APIs.

Constructor control flow scans `Configuration` for `fs.viewfs.mounttable.<table>.` keys, classifies each key by prefix, validates merge-slash exclusivity, sorts regular link entries, builds internal directories, handles nested mount points via `INodeDirLink` when enabled, stores root fallback links, and optionally creates a fallback from the initializing URI when a subclass allows empty mount tables. Regex entries are compiled into `RegexMountPoint` instances.

`resolve(String, boolean)` handles `/`, merge-slash root links, regex matches, normal tree descent, nested dir-link fallback, root fallback, and internal-directory returns. State is in-memory and immutable after construction except lazy target filesystem creation. Dependencies include `Configuration`, `Path`, `FileSystem` logging, `UserGroupInformation`, `StringUtils`, regex mount helpers, and Hadoop filesystem exceptions.

Risks include mount-key parsing, conflict detection, nested mount precedence, fallback behavior masking missing paths, regex ordering, lazy initialization error handling, and raw string path splitting. Tests should cover every `LinkType`, duplicate/conflicting paths, merge-slash exclusivity, fallback and no-fallback missing paths, nested mount enabled/disabled behavior, regex resolution with `resolveLastComponent`, mount point listing, lazy target initialization failure, and root-path edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/InodeTree.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/MountTableConfigLoader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/MountTableConfigLoader.java

`MountTableConfigLoader` is the private evolving SPI for loading viewfs mount-table configuration from an external location. It defines one method, `load(String mountTableConfigPath, Configuration conf)`, which implementations use to mutate the supplied Hadoop `Configuration` before the mount table is parsed.

There is no state, control flow, or persistence in the interface itself. The persistence contract is defined by implementations: the bundled `HCFSMountTableConfigLoader` reads XML resources from Hadoop-compatible filesystems. `Constants.DEFAULT_MOUNT_TABLE_CONFIG_LOADER_IMPL` points to that implementation, and `ViewFileSystemOverloadScheme` obtains a configurable implementation through `fs.viewfs.mounttable.config.loader.impl`.

Risks are API-contract risks. A loader may partially mutate configuration before throwing, may block initialization on slow storage, or may load keys that conflict with already-present core-site keys. Tests should verify that configured loader classes are instantiated, `load` is called before `ViewFileSystem.initialize`, IOExceptions propagate as initialization failures, and bad loader classes fail clearly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/MountTableConfigLoader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NflyFSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NflyFSystem.java

`NflyFSystem` is a private `FileSystem` implementation for `linkNfly` mount points. It presents multiple target URIs as one filesystem: writes are broadcast to all destinations and considered successful when at least `minReplication` destinations succeed; reads prefer the closest destination or the most recent replica depending on flags.

Important types include `NflyKey` (`minReplication`, `readMostRecent`, `repairOnRead`), `NflyNode`, `MRNflyNode`, `NflyOutputStream`, and `NflyStatus`. Construction wraps each target URI in a `ChRootedFileSystem`, resolves host/rack information with `DNSToSwitchMapping`, and sorts nodes by network distance from the client. `createFileSystem(URI[], Configuration, String, FsGetter)` parses settings and returns an initialized nfly filesystem.

Write control flow creates `_nfly_tmp_<name>` files on all nodes, writes/flushed/closes all still-working streams, drops failing nodes from a `BitSet`, and commits by renaming each successful tmp path to the final path if the surviving count meets `minReplication`. Failed insufficient writes delete tmp files best effort. Reads collect file statuses when `readMostRecent` or `repairOnRead` is enabled, optionally sort by mtime, copy newer replicas to stale/missing nodes through tmp paths, then open the best reachable replica. Rename, delete, mkdirs, status, and list operations fan out or choose a nearest readable node.

State is process-local node topology, flags, and statistics. Durable effects are broad: replicated writes, best-effort delete/rename across all nodes, timestamp normalization, and repair-on-read copies.

Risks include non-atomic cross-filesystem commit, leftover temp files, partial delete/rename results, `append` returning null, stale replica comparison by mtime precision, repair races, and path/status stripping through `NflyStatus`. Tests should simulate partial failures, min-replication thresholds, tmp cleanup, read-most-recent ordering, repair-on-read, all-not-found behavior, list/status path rewriting, and nfly settings validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NflyFSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NotInMountpointException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NotInMountpointException.java

`NotInMountpointException` is a public evolving exception used when an operation cannot be associated with a mounted target. It extends `UnsupportedOperationException` and stores a formatted message in a final `msg` field returned by `getMessage()`.

The constructors distinguish path-specific failures, such as `getStatus` on a path outside all mount points, from operations on an empty path such as default block-size queries without a target path. There is no mutable state beyond the stored message and no persistence behavior.

Integration points include `ViewFileSystem` default replication/block/server-default APIs, path capability lookups outside mount points, trash/enclosing-root failures, overload-scheme admin helpers, `ViewFileSystemUtil.getStatus`, and internal directory operations that cannot delegate to a target filesystem.

Risks are mostly diagnostic and type-semantic risks. Because it is unchecked, callers may not expect it from filesystem metadata queries. Tests should assert message content for both constructors and verify public APIs throw this type, not generic `IOException`, where no target mount exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/NotInMountpointException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPoint.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPoint.java

`RegexMountPoint<T>` implements regex-based mount entries for `InodeTree`. Instead of matching fixed path components, it compiles a source regex and maps captured groups into a destination URI/path string containing `$name`, `${name}`, or numeric group variables.

Important APIs and state include `initialize()`, `resolve(String, boolean)`, `getVarListInString`, `VAR_PATTERN_IN_DEST`, source/destination strings, compiled `Pattern`, destination variable map, and a list of `RegexMountPointInterceptor`s. Settings use `SETTING_SRCREGEX_SEP` between interceptor settings and source regex, `;` between interceptors, and `:` inside interceptor settings.

Resolution first chooses the source prefix to resolve, excluding the last path component when `resolveLastComponent` is false. It applies source interceptors, runs the source pattern, replaces all configured destination variables from named or indexed regex groups, computes the remaining path from the original source path, applies destination and remaining-path interceptors, and delegates to `InodeTree.buildResolveResultForRegexMountPoint` to create the target filesystem.

State is initialized once and then read during resolution. Persistence is indirect: matching produces a target filesystem URI and operations persist in that target. Dependencies include Java regex, Hadoop `Path`, `StringUtils`, SLF4J, `InodeTree`, and interceptor factory/type classes.

Risks include invalid regex syntax, missing named groups throwing from `Matcher.group`, multiple matches overwriting `resolvedPathStr`, null path-to-resolve when excluding the last component, separator collisions in settings, and target filesystem initialization failures returning null. Tests should cover named and numeric groups, `$x` and `${x}`, no-match behavior, bad regex, interceptor chains, `resolveLastComponent` true/false, remaining path construction, and invalid/missing capture groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptor.java

`RegexMountPointInterceptor` is the limited-private unstable interface for plug-in transformations around regex mount resolution. It lets a regex mount transform the source string before matching, transform the resolved destination string after group replacement, and transform the remaining `Path` before the final `ResolveResult` is built.

The interface methods are `initialize()`, `interceptSource(String)`, `interceptResolvedDestPathStr(String)`, `interceptRemainingPath(Path)`, `getType()`, and `serializeToString()`. It has no state itself; implementations own validation, compiled patterns, and serialization format.

Integration is through `RegexMountPoint.initializeInterceptors`, which creates implementations with `RegexMountPointInterceptorFactory`, initializes them, and applies them in list order during `resolve`. `RegexMountPointResolvedDstPathReplaceInterceptor` is the only built-in implementation.

Risks are SPI and ordering risks: interceptors can produce invalid source strings, invalid destination URIs, or remaining paths that no longer correspond to the resolved prefix. Since initialization can throw `IOException`, bad settings fail mount-table construction. Tests should verify interceptor ordering, initialization failure propagation, serialization round trips, and behavior when transformed destination paths cannot initialize a target filesystem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorFactory.java

`RegexMountPointInterceptorFactory` is a private factory that deserializes one interceptor settings string into a `RegexMountPointInterceptor`. The expected format is `<type>:<payload>`, with the concrete built-in replace interceptor using `replaceresolveddstpath:<regex>:<replacement>`.

Control flow finds the first internal separator `:`, lowercases the type tag, resolves it with `RegexMountPointInterceptorType.get`, and switches on the enum. The only supported type is `REPLACE_RESOLVED_DST_PATH`, which is delegated to `RegexMountPointResolvedDstPathReplaceInterceptor.deserializeFromString`. Unknown types, missing separators, or empty payloads return null; callers turn null into an `IOException` during regex mount initialization.

There is no mutable state or persistence. Dependencies are the interceptor type enum, regex mount separator constants, and the replace interceptor implementation.

Risks are format rigidity and silent nulls. Regex or replacement strings containing `:` are not supported by the replace interceptor deserializer, and bad configs surface as a generic illegal settings error. Tests should cover unknown types, missing separators, trailing separators, case-insensitive type tags, valid replace interceptors, and payloads with unsupported separators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorType.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorType.java

`RegexMountPointInterceptorType` is the enum registry for regex mount interceptors. It currently exposes one type, `REPLACE_RESOLVED_DST_PATH`, configured with the lowercase tag `replaceresolveddstpath`.

The enum stores a `configName` for each type and populates a static map from config name to enum instance. `get(String)` is the lookup API used by `RegexMountPointInterceptorFactory`; `getConfigName()` is used by interceptor serialization.

There is no persistence or mutable runtime state after static initialization. Integration is limited but important: this enum is the compatibility contract for serialized interceptor settings in configuration keys.

Risks are configuration compatibility and namespace collisions. Renaming `configName` would break existing mount tables. Adding new enum values requires factory support and tests for serialization/deserialization. Current tests should assert lookup of the known tag, null for unknown tags, and serialization by `RegexMountPointResolvedDstPathReplaceInterceptor`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointInterceptorType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointResolvedDstPathReplaceInterceptor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointResolvedDstPathReplaceInterceptor.java

`RegexMountPointResolvedDstPathReplaceInterceptor` is the built-in regex mount interceptor that applies a regex replacement to the resolved destination path string after capture-group substitution. It does not alter the source string or remaining path.

Important APIs are the constructor, `initialize()`, `interceptResolvedDestPathStr(String)`, `serializeToString()`, and `deserializeFromString(String)`. State consists of the source regex string, replacement string, and compiled `Pattern`. Initialization compiles the regex and wraps `PatternSyntaxException` as `IOException`. Interception uses `Matcher.replaceAll(replaceString)`.

The serialized format is `replaceresolveddstpath:<srcRegex>:<replaceString>`, using `RegexMountPoint.INTERCEPTOR_INTERNAL_SEP`. Deserialization splits on `:`, requires exactly three parts, and returns null for bad formats. The implementation assumes the regex and replacement do not contain `:`.

Dependencies include Java regex, Hadoop `Path`, the interceptor interface, and the interceptor type enum. Persistence is configuration serialization only; actual filesystem persistence occurs after the regex mount resolves to a target.

Risks include separator limitations, replacement syntax surprises from `Matcher.replaceAll` (`$` and backslash semantics), invalid regex initialization, and unexpected global replacement across the whole destination string. Tests should cover valid replacements, no-op unmatched replacements, invalid regex, serialization round trip, bad serialized lengths, and replacement strings with regex metacharacter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/RegexMountPointResolvedDstPathReplaceInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystem.java

`ViewFileSystem` is the public `FileSystem` implementation for `viewfs://`. It exposes a client-side mount table that maps view paths to target filesystems. It builds an `InodeTree<FileSystem>` from configuration, wraps link targets in `ChRootedFileSystem`, exposes synthetic read-only internal directories, and delegates file operations to resolved targets.

Important types and state include `InnerCache`, public `MountPoint`, `InternalDirOfViewFs`, `RenameStrategy`, `creationTime`, `ugi`, `myUri`, `workingDir`, `config`, `fsState`, `homeDir`, `enableInnerCache`, and `cache`. `initialize` chooses the mount table name from URI authority, optionally ignoring port, constructs `InodeTree`, provides target initialization hooks, sets the working directory to the viewfs home directory, and reads the configured rename strategy. The inner cache can reuse child filesystems by lowercased scheme/authority.

Most API control flow is resolve-and-delegate. `getUriPath` validates and absolutizes paths; `fsState.resolve(path, resolveLastComponent)` returns a target filesystem and remaining path. Create and mkdir resolve the parent (`false`) to protect internal mount-table paths; read/status/list/metadata operations resolve the full path (`true`). Status objects from external targets are rewritten to viewfs-qualified paths, with special handling for local files and nfly statuses. Rename resolves both sides, applies `RenameStrategy`, and for two `ChRootedFileSystem` targets can rename on raw filesystems with fully expanded paths. Internal directories are read-only except selected fallback behavior for create/mkdir/list/block locations.

Persistence lives in target filesystems. Viewfs stores only in-memory mount state, working directory, home directory cache, and optional child filesystem cache. Integration points are `ConfigUtil`/`Constants`, `InodeTree`, `ChRootedFileSystem`, `NflyFSystem`, `NotInMountpointException`, and `ViewFileSystemUtil`.

Risks include internal-dir versus fallback semantics, rename policy correctness, path/status rewriting, mount links as symlink versus target status, cache lifecycle, trash-root translation, and unsupported cross-filesystem operations such as concat. Tests should cover all operation families over internal dirs, simple links, fallback links, nfly links, regex links, merge slash, nested mount points, rename strategies, cache close behavior, trash roots, path capabilities, storage policies, and `getChildFileSystems`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystemOverloadScheme.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystemOverloadScheme.java

`ViewFileSystemOverloadScheme` extends `ViewFileSystem` so an existing scheme such as `hdfs://cluster` or `s3a://bucket` can be backed by a viewfs mount table without using the `viewfs://` URI scheme. It keeps normal viewfs mount parsing but reports the original scheme and handles same-scheme child filesystem creation specially to avoid recursive overload resolution.

Important APIs and state include `initialize`, `getScheme`, `supportAutoAddingFallbackOnNoMounts`, `setSupportAutoAddingFallbackOnNoMounts`, `fsGetter`, `getRawFileSystem`, `getMountPathInfo`, `getFallbackFileSystem`, and nested `ChildFsGetter`/`MountPathInfo`. Initialization stores the original URI, defaults mount links to non-symlink display, defaults mount-table-name parsing to ignore port, optionally loads external mount table XML through `MountTableConfigLoader`, then calls `super.initialize`.

`ChildFsGetter` checks whether a target URI uses the overloaded root scheme. If so, it instantiates the real target filesystem class from `fs.viewfs.overload.scheme.target.<scheme>.impl` and initializes it directly; otherwise it delegates to normal `FileSystem` creation/cache APIs. Admin helper APIs resolve paths and expose either raw child filesystems or path-on-target plus target filesystem, unwrapping `ChRootedFileSystem` when needed.

State is in-memory and configuration-driven. Persistent effects occur in underlying filesystems and in loaded mount table resources. Dependencies include `ViewFileSystem`, `FsGetter`, `MountTableConfigLoader`, `HCFSMountTableConfigLoader`, reflection, `FsConstants`, and `NotInMountpointException`.

Risks include infinite recursion if same-scheme targets are not configured correctly, class-instantiation failures, default behavior differences from `viewfs://`, external mount-table loading failures, and admin APIs assuming chrooted targets. Tests should cover same-scheme and different-scheme targets, missing target impl config, fallback auto-add behavior, mount table loader invocation, port-ignore default, raw filesystem unwrapping, and `MountPathInfo` for links/internal dirs/fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystemOverloadScheme.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystemUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystemUtil.java

`ViewFileSystemUtil` is a public utility class for identifying viewfs instances and collecting filesystem status per matching mount point. It is stateless and non-instantiable.

Important APIs are `isViewFileSystem(FileSystem)`, `isViewFileSystemOverloadScheme(FileSystem)`, and `getStatus(FileSystem, Path)`. The first checks for the literal `viewfs` scheme; the second checks `instanceof ViewFileSystemOverloadScheme`. `getStatus` validates that the input filesystem is either a viewfs or overload-scheme instance, casts to `ViewFileSystem`, obtains the viewfs URI path, iterates public mount points, compares path components, and returns a map of matching mount points to `FsStatus`.

Control flow distinguishes three cases: the path is over a specific mount point, the path is an internal directory leading to one or more mount points, or the path is `/` and includes all mount points. If none apply, it throws `NotInMountpointException`. For matches, it calls `viewFileSystem.getStatus(path)` and stores the result by `MountPoint`.

Dependencies are `FileSystem`, `FsConstants`, `FsStatus`, `Path`, `UnsupportedFileSystemException`, `ViewFileSystem.MountPoint`, and `InodeTree.breakIntoPathComponents`.

Risks include scheme-based detection missing overload schemes unless callers use the second helper, map overwrites if mount point equality changes, path-component edge cases at root, and `getStatus(path)` behavior for fallback/internal dirs. Tests should cover non-viewfs rejection, root status over all mounts, internal directory status aggregation, path over a single mount, unrelated paths throwing `NotInMountpointException`, and overload-scheme inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFileSystemUtil.java -->
