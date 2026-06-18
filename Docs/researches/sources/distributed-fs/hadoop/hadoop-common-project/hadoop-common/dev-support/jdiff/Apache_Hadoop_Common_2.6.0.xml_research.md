# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007151`: lines 1-5866, `Docs/researches/chunks/subset-b-007151_research.md`
- `subset-b-007152`: lines 5867-11840, `Docs/researches/chunks/subset-b-007152_research.md`
- `subset-b-007153`: lines 11841-17787, `Docs/researches/chunks/subset-b-007153_research.md`
- `subset-b-007154`: lines 17788-23751, `Docs/researches/chunks/subset-b-007154_research.md`
- `subset-b-007155`: lines 23752-30010, `Docs/researches/chunks/subset-b-007155_research.md`
- `subset-b-007156`: lines 30011-36346, `Docs/researches/chunks/subset-b-007156_research.md`
- `subset-b-007157`: lines 36347-42401, `Docs/researches/chunks/subset-b-007157_research.md`
- `subset-b-007158`: lines 42402-45596, `Docs/researches/chunks/subset-b-007158_research.md`

## Chunk Research

### subset-b-007151: lines 1-5866

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 1-5866

## Scope

This chunk is the opening section of the Hadoop Common 2.6.0 JDiff XML API snapshot generated from public and protected Javadoc. It is not executable source code; it records API surface, inheritance, visibility, exceptions, deprecation metadata, and selected documentation. The covered range starts at the XML/API header and includes packages `org.apache.hadoop`, `org.apache.hadoop.conf`, `org.apache.hadoop.crypto`, `org.apache.hadoop.crypto.key`, `org.apache.hadoop.crypto.key.kms`, `org.apache.hadoop.crypto.random`, and the start of `org.apache.hadoop.fs` through part of `CommonConfigurationKeysPublic`.

The chunk stops inside `CommonConfigurationKeysPublic`, ending after `KMS_CLIENT_ENC_KEY_CACHE_LOW_WATERMARK`; later constants and later filesystem APIs are outside this mapped item.

## Purpose

The XML file is a release API baseline for Hadoop Common. JDiff consumes this form to compare public/protected API compatibility across Hadoop releases. For this chunk, the baseline describes the core exception type, the configuration system, runtime reconfiguration hooks, key-provider and KMS extension APIs, and early filesystem abstractions.

This source sits under `dev-support/jdiff`, so its primary function is compatibility governance rather than runtime behavior. It is still important because the XML encodes which classes, methods, constructors, fields, deprecations, and thrown exceptions Hadoop Common 2.6.0 exposed to downstream projects.

## Important APIs, Types, and Functions

### API metadata and base exception

- The root `<api>` names the baseline `hadoop-core 2.6.0`, generated with JDiff 1.0.9 and the `ExcludePrivateAnnotationsJDiffDoclet`.
- `org.apache.hadoop.HadoopIllegalArgumentException` extends `IllegalArgumentException` to distinguish invalid argument failures raised by Hadoop implementation code from those raised by the JDK.

### Configuration model

- `Configurable` defines the minimal `setConf(Configuration)` / `getConf()` contract.
- `Configured` is a concrete base class implementing `Configurable` for objects that carry a Hadoop `Configuration`.
- `Configuration` is the central mutable configuration container. It implements `Iterable` and Hadoop `Writable`, has constructors for default loading, explicit no-default loading, and copy construction, and exposes broad APIs for resource loading, typed access, mutation, serialization, class loading, diagnostics, and deprecation handling.
- Resource APIs include `addDefaultResource`, `addResource` overloads for classpath names, `URL`, `Path`, `InputStream`, named `InputStream`, and another `Configuration`, plus `reloadConfiguration`.
- Lookup and mutation APIs include `get`, `getTrimmed`, `getRaw`, `set`, `unset`, `setIfUnset`, and typed helpers for `int`, `long`, byte-size longs, `float`, `double`, `boolean`, enums, time durations, regex `Pattern`, ranges, string collections, password lookup, socket addresses, class names, instances, local paths, files, and resources.
- Persistence and diagnostics APIs include `writeXml(OutputStream)`, `writeXml(Writer)`, static `dumpConfiguration`, `readFields`, `write`, `iterator`, `size`, `clear`, `getFinalParameters`, `getPropertySources`, `getValByRegex`, `dumpDeprecatedKeys`, and `hasWarnedDeprecation`.
- `Configuration.DeprecationDelta` represents pending global deprecation mappings from an old key to one or more replacement keys plus an optional custom message.
- `Configuration.IntegerRanges` parses positive integer range strings such as `2-3,5,7-` and supports membership tests and iteration.

### Runtime reconfiguration

- `Reconfigurable` extends `Configurable` with `reconfigureProperty`, `isPropertyReconfigurable`, and `getReconfigurableProperties`.
- `ReconfigurableBase` supplies an abstract base for background reconfiguration tasks. Its final `reconfigureProperty` updates the `Configuration` and delegates implementation-specific state updates to `reconfigurePropertyImpl`.
- `ReconfigurationException` records the property, requested new value, and old value for failed runtime changes.
- `ReconfigurationServlet` exposes HTTP GET/POST integration for reviewing and approving node configuration changes. Its public field `CONF_SERVLET_RECONFIGURABLE_PREFIX` is the servlet-context naming prefix for reconfigurable objects.
- `ReconfigurationTaskStatus` exposes task existence, stopped/running state, start/end times, and a status map.
- `ReconfigurationUtil` and `PropertyChange` compare old/new `Configuration` objects and represent changed property triples.

### Key provider and crypto APIs

- `CachingKeyProvider` wraps a `KeyProvider` and caches key versions and metadata for short-lived bursts, invalidating relevant cache entries on delete and key roll.
- `JavaKeyStoreProvider.Factory`, `UserProvider.Factory`, and `KMSClientProvider.Factory` are `KeyProviderFactory` implementations discovered through `ServiceLoader`.
- `JavaKeyStoreProvider.KeyMetadata` adapts Hadoop key metadata to `java.security.Key`/`Serializable` so it can be stored in a Java KeyStore.
- `KeyProvider` is the abstract provider of secret key material. It defines provider configuration access, option creation, transient-provider detection, key listing, metadata lookup, version lookup, key creation, key deletion, key rolling, flush/close, generated key material, version-name helpers, provider lookup, and default cipher/bit-length constants. The Javadoc states implementations must be thread-safe.
- `KeyProvider.KeyVersion` carries a key name, version name, and material bytes.
- `KeyProvider.Metadata` carries cipher, bit length, description, attributes, creation date, and version count, with protected byte serialization/deserialization helpers.
- `KeyProvider.Options` is the fluent key-creation options holder for cipher, bit length, description, and attributes.
- `KeyProviderExtension<E>` is an abstract delegating wrapper that forwards normal `KeyProvider` operations to an underlying provider while exposing an extension object.
- `KeyProviderExtension.Extension` is a marker for extension interfaces.
- `KeyProviderCryptoExtension.CryptoExtension` adds encrypted-key generation, encrypted-key decryption, warm-up, and queue drain behavior.
- `KeyProviderCryptoExtension.EncryptedKeyVersion` carries the encryption key name, encryption key version name, encrypted-key IV, and encrypted encryption key version. Its `createForDecryption` factory permits partially populated objects for decrypt paths, and `deriveIV` avoids direct IV reuse.
- `KeyProviderDelegationTokenExtension` and nested `DelegationTokenExtension` add delegation-token acquisition into Hadoop `Credentials`.
- `KeyProviderFactory` creates providers from configured URI paths via service loading, with public `KEY_PROVIDER_PATH`.
- `KeyShell` is the CLI `Tool` for key-provider operations and exposes public `out` and `err` streams for test capture.
- KMS-specific public nested types in this chunk include `KMSClientProvider.KMSEncryptedKeyVersion`, `KMSKeyVersion`, and `KMSMetadata`, plus `ValueQueue.QueueRefiller` and `ValueQueue.SyncGenerationPolicy`.

### Filesystem APIs

- `AbstractFileSystem` is the public implementor-facing filesystem abstraction used through `FileContext`. It validates URI scheme/authority/path membership, creates filesystem instances from `fs.AbstractFileSystem.<scheme>.impl`, tracks per-filesystem statistics, qualifies paths, exposes home and initial working directories, and defines abstract or overridable filesystem operations.
- Covered `AbstractFileSystem` operations include create/open/delete/rename/mkdir, symlink support and link target lookup, permissions and ownership updates, timestamp updates, checksums, file status and link status, block locations, filesystem status, listing, corrupt block iteration, checksum verification, canonical service name, delegation tokens, ACL operations, xattr operations, and equality/hash behavior.
- `AvroFSInput` adapts `FSDataInputStream` and `FileContext`/`Path` to Avro `SeekableInput`.
- `BatchedRemoteIterator` implements batched remote pagination with `makeRequest(prevKey)`, `elementToPrevKey(element)`, and `RemoteIterator` methods. `BatchedEntries` abstracts a returned page; `BatchedListEntries` backs it with a `List`.
- `BlockLocation` models replica hostnames, cached hosts, transfer names, topology paths, file offset, length, and corrupt state.
- `ByteBufferReadable` defines stream reads directly into `ByteBuffer` and documents caller-visible position/limit semantics and possible `UnsupportedOperationException`.
- `CanSetDropBehind` and `CanSetReadahead` define optional stream tuning knobs.
- `ChecksumException` extends `IOException` and records the file position of a checksum error.
- `ChecksumFileSystem` is an abstract `FilterFileSystem` that creates and verifies client-side checksum files alongside raw files. It provides checksum file naming/length helpers, verification/write toggles, open/append/create/delete/rename/list/copy/local-output behavior, and checksum failure reporting.
- The visible portion of `CommonConfigurationKeysPublic` declares public constants for native library availability, network topology scripts and mappings, default filesystem name, disk usage/status intervals, symlink resolution, trash intervals, local block size default, automatic filesystem close, file and FTP filesystem implementation settings, MapFile/TFile/SequenceFile I/O settings, IPC client/server retry and socket settings, socket factories, hash type, group mapping caches, authentication and authorization, SSL/HTTP policy, RPC protection, SASL props, crypto codec/cipher/provider/buffer settings, impersonation provider, and KMS encrypted-key cache settings.

## Control Flow

The XML itself has no runtime control flow. Its structure is deterministic: package elements contain class/interface declarations, each declaration lists constructors, methods, fields, implemented interfaces, exceptions, and Javadoc text.

The runtime flows described by the API docs are:

- `Configuration` loads default resources (`core-default.xml`, then `core-site.xml`) unless disabled, then overlays later resources in insertion order while respecting final parameters. Getters trigger variable expansion and deprecation alias resolution. Setters update deprecated/replacement aliases as documented. Reload clears resource-derived values and final flags so resources are reread lazily on the next access while explicitly set values remain overlaid.
- Global configuration deprecations are updated by creating a new deprecation context from the old one and atomically swapping it in, retrying on races.
- Reconfiguration compares a freshly loaded configuration with the old one, presents or starts changes through the servlet/background task API, then applies accepted properties by calling the final `ReconfigurableBase.reconfigureProperty`, which updates `Configuration` and delegates internal state mutation to subclass `reconfigurePropertyImpl`.
- Key-provider flows center on `KeyProviderFactory.getProviders(conf)` and `get(uri, conf)` creating providers from configured URI schemes, then `KeyProvider` methods listing, creating, rolling, deleting, flushing, and retrieving key material. Extension wrappers delegate all base operations to the underlying provider while adding crypto or delegation-token behavior.
- Encrypted-key generation uses the current key version for a named encryption key, creates transient encrypted key material that is not stored by the provider, and later decrypts `EncryptedKeyVersion` objects using key name, key version, and IV.
- `AbstractFileSystem` factory flow maps a URI scheme to an implementation class in `Configuration`, constructs an implementation with the URI and config, and requires later path operations to pass paths that match the filesystem scheme/authority or are slash-relative. Many methods defer exact semantics to matching `FileContext` operations.
- `BatchedRemoteIterator` flow fetches a page keyed by the previous element key, yields elements from the page, and uses `hasMore` to decide whether another remote request is required.
- `ChecksumFileSystem` flow wraps raw filesystem operations, maps data paths to checksum paths, writes or verifies checksum side files depending on configuration, and can report checksum failures for retry decisions.

## State and Persistence Behavior

The JDiff XML is a persisted compatibility artifact. Changes to this file are meaningful because downstream compatibility tooling can interpret removed methods, changed signatures, changed exceptions, changed deprecation flags, or changed visibility as API drift.

The APIs represented here describe several stateful systems:

- `Configuration` owns mutable key/value state, loaded resources, final-parameter state, property source tracking, deprecation-warning state, class loader state, quiet-mode state, and serialized `Writable`/XML representations. It also participates in JVM-wide default-resource and deprecation maps.
- Configuration resources persist as XML files or streams. `writeXml` persists non-default properties, while `dumpConfiguration` emits a JSON-like diagnostic representation of all parameters and metadata except input-stream-loaded parameters.
- Password lookup intentionally prefers credential providers before cleartext configuration fallback, so secret state may live outside XML configuration in provider-backed storage.
- Reconfiguration state includes active or completed background task timestamps and per-property status results.
- Key provider implementations persist key material and metadata according to provider type. The abstract contract requires `flush()` to write changes to persistent storage; transient providers explicitly are not long-term storage. Metadata has protected byte serialization helpers for provider storage.
- `CachingKeyProvider` introduces in-memory cached copies of key versions and metadata with timeout behavior controlled by constructor arguments. Mutating operations must invalidate or refresh cache state.
- KMS client value queues cache encrypted keys and refill through `QueueRefiller`; the sync generation policy controls behavior when a queue is empty.
- `AbstractFileSystem` maintains statistics per filesystem URI scheme/authority and per-instance `statistics`. Filesystem operations mutate external persistent filesystem namespace state: files, directories, permissions, ACLs, xattrs, symlinks, replication, timestamps, and checksums.
- `ChecksumFileSystem` persists checksum side files for raw files and may copy or omit CRC files during local copy operations.
- `BlockLocation` is mutable metadata state for block placement/caching/corruption observations, not persistent storage by itself.

## Dependencies and Integration Points

- The JDiff generation command references the Hadoop annotations doclet, compiled Hadoop Common classes, Hadoop Auth, Guava, Commons CLI/Math/HTTP/IO/Net/Configuration/Logging/Lang/Collections/Compress, servlet API, Jetty, Jersey/Jackson/Jettison/JAXB, Log4j/SLF4J, Jets3t, HttpComponents, Avro, Snappy, Ant, Protobuf, Gson, Apache Directory Kerberos, Curator/ZooKeeper, JSch, FindBugs annotations, HTrace, Netty, and XZ.
- `Configuration` integrates with `Path`, local filesystem access, credential providers, `Writable`, class loading, Java regex/time/concurrency APIs, `InetSocketAddress`, `System` properties, and Hadoop default resources.
- Reconfiguration integrates with servlet APIs (`HttpServlet`, request/response, `ServletException`) and service/node classes that implement `Reconfigurable`.
- Key-provider APIs integrate with Java crypto (`Key`, `NoSuchAlgorithmException`, `GeneralSecurityException`), Java `URI`, Hadoop `Credentials`, Hadoop `Token`, service-loaded provider factories, Java KeyStore storage, user credential storage, and KMS HTTP-backed providers.
- Filesystem APIs integrate with `FileContext`, `FileSystem`, `Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `BlockLocation`, permissions/ACLs/xattrs, delegation tokens, Avro `SeekableInput`, and Hadoop security access-control exceptions.
- `CommonConfigurationKeysPublic` is the constant bridge to `core-default.xml` and therefore to user/admin configuration files.

## Risks and Edge Cases

- Because this is generated XML, manual edits risk corrupting compatibility baselines. The correct source of truth is the Java API and JDiff generation process.
- The chunk is a partial file range. Any per-file report must merge later chunks before concluding the full Hadoop Common 2.6.0 API surface.
- The root generation command embeds local absolute paths from the build machine. These are historical metadata, not portable build instructions.
- `Configuration` deprecation APIs have deprecated overloads that accept multiple replacement keys; docs say attempts to add deprecations after loading resources once can throw `UnsupportedOperationException`.
- `Configuration.addResource(InputStream)` caches stream contents and closes the stream after read, with explicit memory-use warning.
- Final configuration parameters block later resource overrides, which can surprise callers that expect last-writer-wins semantics.
- Variable expansion falls back to system properties, so values may depend on JVM environment at read time.
- Typed getters throw `NumberFormatException` for invalid numeric/time/range values except booleans and patterns, which document fallback behavior.
- `getPassword` may fall back to cleartext configuration if credential providers do not resolve the alias, preserving compatibility but weakening secret hygiene.
- Reconfiguration requires subclasses to update every internal structure derived from a property and recursively reconfigure owned `Reconfigurable` objects; partial implementations can leave live services inconsistent with their `Configuration`.
- `KeyProvider` implementations must be thread-safe and must respect `flush()` persistence semantics. Providers that cache metadata or key versions need careful invalidation on roll/delete.
- Encrypted-key APIs state generated encrypted keys are not stored by the provider; callers must persist returned encrypted key material where needed.
- `EncryptedKeyVersion.createForDecryption` returns partially populated objects, so code must avoid using them for operations other than decrypt paths.
- `AbstractFileSystem` distinguishes fully qualified paths from slash-relative paths and can throw `InvalidPathException`, `UnresolvedLinkException`, `UnsupportedFileSystemException`, `AccessControlException`, or `IOException` depending on operation and implementation.
- Several filesystem feature methods, including ACL/xattr/symlink-related operations, may be unsupported or implementation-specific despite being present in the abstract API.
- `ByteBufferReadable` explicitly allows implementations to throw `UnsupportedOperationException` and leaves buffer position/limit undefined after exceptions.
- `ChecksumFileSystem` side-file behavior means rename, delete, copy, and local-output paths must keep data files and checksum files consistent.
- `CommonConfigurationKeysPublic` includes deprecated MapReduce sort constants moved to MapReduce defaults and contains typoed documentation text such as "Defalt"; compatibility consumers should treat names and deprecation metadata as authoritative, not prose quality.

## Test Signals

- JDiff comparison tests should flag removed classes, changed method/constructor signatures, changed field visibility/static/final attributes, changed thrown exception sets, and changed deprecation metadata relative to this baseline.
- Configuration tests should cover default resource order, final parameters, resource overlays, reload behavior, variable expansion, deprecated-key aliases, source tracking, typed getter parse failures, password credential-provider fallback, XML/Writable round trips, and class loading.
- Reconfiguration tests should cover changed-property detection, successful property updates, rejected non-reconfigurable properties, exception detail fields, background task status transitions, and servlet GET/POST integration.
- Key-provider tests should cover service-loader factory selection by URI, create/delete/roll/current-version flows, metadata serialization, flush persistence, transient-provider behavior, delegation token pass-through, crypto extension encrypted-key generation/decryption, IV derivation, and cache invalidation in `CachingKeyProvider`.
- Filesystem tests should cover URI scheme/authority validation, path qualification, statistics registration/clearing, create/open/delete/rename/mkdir semantics, symlink resolution, permission/owner/time changes, status/listing/block-location APIs, delegation token retrieval, ACL and xattr operations, and unsupported-feature failures.
- Checksum filesystem tests should cover checksum file naming and length, write/verify toggles, open/create/append behavior, rename/delete consistency for checksum files, local copy CRC options, and checksum failure reporting.
- Constant compatibility tests should assert public names in `CommonConfigurationKeysPublic` remain stable, especially deprecated constants that downstream code may still compile against.

### subset-b-007152: lines 5867-11840

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 5867-11840

## Scope

This chunk covers a JDiff XML API report for part of the Hadoop Common 2.6.0 public/protected Java API. It starts at the tail of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, then covers file-system-facing types from `ContentSummary` through most of `FileUtil`. The largest API surfaces in this range are `FileContext`, `FileSystem`, `FileStatus`, `FileSystem.Statistics`, and local/file-system utility helpers.

The source is not implementation code. It records class names, method signatures, visibility, deprecation state, thrown exceptions, field declarations, implemented interfaces, and embedded Javadoc. Research therefore treats this chunk as an API contract and compatibility surface for Hadoop filesystem clients and filesystem implementations.

## Purpose

The chunk describes Hadoop Common filesystem APIs used by applications, shells, MapReduce/YARN components, HDFS clients, local filesystem adapters, token management code, and tests. It defines how callers discover filesystems, qualify paths, create/open/append files, list directories, inspect metadata, manipulate permissions/owners/timestamps, handle symlinks, manage ACLs and xattrs, obtain delegation tokens, copy data across local and distributed filesystems, and collect per-filesystem IO statistics.

It also preserves compatibility details for older API entry points. Several methods are deprecated in favor of newer path-aware or `FileContext`-oriented calls, but remain part of the Hadoop 2.6 public surface. The JDiff report is used to detect API drift across Hadoop releases, so method overloads and deprecation metadata are themselves important output.

## Important APIs, Types, and Data

The chunk begins with final public configuration constants for KMS encrypted-key cache behavior and secure-random settings in `CommonConfigurationKeysPublic`. These include cache low-watermark, refill-thread, expiry, Java secure-random algorithm, secure-random implementation, and device-file-path keys/defaults. They bind client-side crypto/token behavior to `core-default.xml` configuration names.

`ContentSummary` is a `Writable` record for directory/file aggregate state. Its constructors cover empty, basic length/file/directory counts, and quota-aware length/count/space forms. Accessors expose content length, directory count, file count, namespace quota, disk space consumed, and space quota. `write` and `readFields` make the object serializable through Hadoop IO, while `getHeader` and overloaded `toString` methods format quota-aware and human-readable command output.

`CreateFlag` is an enum contract for file creation semantics. `CREATE`, `APPEND`, `OVERWRITE`, and `SYNC_BLOCK` can be combined by callers, then validated with overloads of `validate`. The Javadoc specifies valid combinations such as create-only, append-only, overwrite-only, create-or-append, and create-or-overwrite. `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` are invalid and should throw `HadoopIllegalArgumentException`; path-aware validation also maps existence checks to `FileAlreadyExistsException` or `FileNotFoundException` behavior.

`DelegationTokenRenewer.Renewable` and `DelegationTokenRenewer.RenewAction` define the renewal hook used by filesystems that need automatic delegation-token replacement. `Renewable` supplies `getRenewToken` and `setDelegationToken`. `RenewAction` implements `Delayed` with validity, delay, ordering, equality, hash, and string methods so renewals can be scheduled in a delay queue.

`DUHelper` exposes disk-usage helper entry points: `getFolderUsage`, instance `check`, `getFileCount`, `getUsage`, and a `main` entry point. `FileAlreadyExistsException` is an `IOException` subclass used when a target already exists and overwrite was not requested. `FileChecksum` is an abstract `Writable` with algorithm name, byte length, raw checksum bytes, `Options.ChecksumOpt`, and equality/hash semantics based on algorithm and value.

`FileContext` is a higher-level namespace context around `AbstractFileSystem`. It has factory overloads for default configuration, explicit `Configuration`, explicit URI, explicit default `AbstractFileSystem`, and local filesystem contexts. It maintains path resolution state such as default filesystem, user/group identity, working directory, and umask. Its constants distinguish legacy default permissions from `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and it has a shutdown-hook priority for delete-on-exit cleanup.

`FileContext` operations cover create, mkdir, delete, open, set replication, rename, permission/owner/time changes, checksums, file status, access checks, symlink creation and target inspection, block locations, filesystem capacity/status, listing, corrupt-block listing, located listing, delete-on-exit, path resolution, filesystem statistics, delegation tokens, ACL operations, and xattr operations. The embedded symlink documentation is unusually detailed: final-component symlinks are handled differently by delete, rename, link-status, and target APIs than by APIs that follow links; targets may be fully qualified URIs, partially qualified URIs, relative paths, or absolute paths.

`FileContext.Util` is a convenience facade for common derived operations. It provides existence checks, content summaries, list-status overloads with filters and varargs, recursive file listing, globbing, and copy helpers from `Path` to `Path` or into an output stream. These utilities sit above the primitive `FileContext` operations and are important for callers that want arrays or iterators rather than lower-level filesystem calls.

`FileStatus` is a `Writable` and `Comparable` metadata record. Constructors represent empty status, basic length/directory/replication/block-size/modification-time/path state, full permission/owner/group/access-time state, symlink-aware state, and copy construction. Getters expose length, file/directory status, deprecated `isDir`, symlink state and target, block size, replication, modification/access time, permissions, encryption bit, owner, group, and path. Mutators allow setting path, permission, owner, group, and symlink before serialization. Comparison/equality/hash/string methods make statuses sortable and usable in filesystem listings and glob results.

`FileSystem` is the core abstract base class for Hadoop filesystem implementations. Static discovery APIs include `get`, `newInstance`, `getLocal`, `newInstanceLocal`, `getDefaultUri`, `setDefaultUri`, `getFileSystemClass`, and cache controls such as `closeAll` and `closeAllForUGI`. Instance identity APIs include `initialize`, scheme/URI/canonical URI/default port, canonical service name for token lookup, child filesystems, path qualification, and path validation. The class has public constants for the default filesystem key/name, logging, shutdown-hook priority, and a protected `statistics` field.

`FileSystem` file operations include many `create` overloads, `primitiveCreate`, `primitiveMkdir`, deprecated `createNonRecursive` overloads, `createNewFile`, `open`, `append`, `concat`, `rename`, `delete`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, `exists`, `isDirectory`, `isFile`, length/content summary lookup, list-status overloads, globbing, located status, recursive file listing, home/working directory management, mkdirs, local copy/move helpers, local output staging, close, used space, block/default block size, replication, status, and permission/owner/time mutation.

`FileSystem` also exposes symlink, checksum, snapshot, ACL, xattr, and statistics APIs. Snapshot calls create default or named snapshots, rename snapshots, and delete snapshots. ACL methods mirror `FileContext`: modify, remove entries, remove default ACL, remove all but base ACL, fully set, and retrieve status. XAttr methods set with optional flags, get one, get all, get named set, list names, and remove. Static statistics calls return or reset per-scheme/per-class statistics; symlink enablement is also exposed globally.

`FileSystem.Statistics` is a write-optimized counter object keyed by scheme. It has constructors, thread-local data access, increment methods for bytes read/written and read/large-read/write operations, aggregate getters, `reset`, `toString`, and `getScheme`. `StatisticsData` exposes the per-thread volatile counters and getters. The docs explain the design: writers update thread-local data to avoid contention, readers aggregate across thread-local areas, and reset offsets root data rather than mutating other threads' thread-local state.

`FileUtil` collects static local and cross-filesystem helpers. This chunk covers conversion from `FileStatus[]` to `Path[]`, recursive local deletion with explicit symlink semantics, symlink target reading, content-only deletion, deprecated filesystem recursive deletion, inter-filesystem and local/filesystem copy overloads, copy-merge, shell-path conversion, local disk usage, unzip/untar, local symlink creation, chmod/chown-style ownership and permission helpers, portable readable/writable/executable setters and access checks, `FsPermission` application, temp-file creation, file replacement, safe wrappers around `File.listFiles()` and `File.list()`, and the beginning of `createJarWithClassPath`.

## Control Flow

Most control flow is implicit in API layering. `FileContext` resolves a caller path against its default filesystem, working directory, and symlink rules, finds the relevant `AbstractFileSystem` with `getFSofPath`, and delegates filesystem operations while preserving `FileContext` state such as umask and user identity. Relative paths are not interpreted as process-current-directory paths; they are prefixed with the `FileContext` working directory.

File creation flows normalize caller intent through `CreateFlag`, permissions, umask, replication, block size, buffer size, progress callbacks, and optional checksum options. `FileSystem` exposes numerous convenience overloads that funnel toward abstract or protected primitive methods implemented by concrete filesystems. Static `FileSystem.create(fs, path, permission)` and `mkdirs(fs, path, permission)` intentionally use follow-up permission setting to avoid process-wide configuration mutation, trading an extra RPC for thread safety.

Listing flows differ by API shape. `listStatus` returns arrays in `FileSystem` and remote iterators in `FileContext`; `listLocatedStatus` includes block locations for files; `listFiles` can recurse through a subtree and emits file statuses with block locations. Glob calls expand path patterns and return sorted statuses, with a documented distinction between no-match on non-glob paths (`null`) and no-match on glob paths (empty array).

Symlink flow is explicitly split between operations that act on a final symlink and operations that resolve it. Delete, delete-on-exit, rename, link-status, and get-link-target operate on the symlink itself for the final path component. Most open, metadata, checksum, block-location, status, and listing operations follow symlinks. Intermediate symlinks are resolved transparently, and `resolve`/`resolveIntermediate` expose protected helpers for all-symlink or intermediate-only resolution.

Delegation-token flow starts from canonical service names. A filesystem with its own token returns a unique service string and can produce a token via `getDelegationToken`; callers should prefer `addDelegationTokens`, which avoids duplicating tokens already present in `Credentials` and can recurse into child filesystems for embedded filesystems. `FileContext.getDelegationTokens` asks for all filesystems accessed for a given path.

Statistics flow is low-contention by design. IO paths increment thread-local counters through `FileSystem.Statistics`; readers aggregate totals, while reset computes a negative root offset under lock instead of trying to zero thread-local counters owned by other threads.

`FileUtil` flows are utility-level. Copy helpers bridge source and destination `FileSystem` objects or local files, optionally deleting sources and overwriting destinations. Delete helpers recursively process local files/directories but avoid following symlink directories for full deletion, while content-only deletion does follow a symlink to a directory and deletes the target directory contents. Permission helpers prefer Java primitives when possible and fall back to platform commands where needed. `createJarWithClassPath` begins a flow that creates a manifest-only classpath jar to work around command-line length limits.

## State and Persistence Behavior

`ContentSummary`, `FileStatus`, and `FileChecksum` are serializable state carriers. `ContentSummary` persists aggregate counts and quotas through `Writable`; `FileStatus` persists metadata including path, permissions, ownership, times, symlink target, and encryption indicator; concrete `FileChecksum` implementations persist algorithm and bytes.

`FileContext` holds per-context state: default filesystem, working directory, umask, and UGI. This is analogous to process filesystem state but scoped to the `FileContext` object. Delete-on-exit registration persists until JVM shutdown or successful cleanup via the shutdown hook.

`FileSystem` instances are cached by URI/scheme/authority and user unless callers use `newInstance` APIs, which always create unique instances. Static cache close methods can close all cached filesystems or all cached filesystems for a specific `UserGroupInformation`. `FileSystem` also carries protected per-instance statistics and global per-scheme/per-class statistics registries.

Filesystem operations persist remote or local namespace mutations: create/append/concat/rename/delete, mkdirs, replication, permissions, owners, timestamps, symlinks, snapshots, ACLs, xattrs, and copied files. Snapshot APIs persist named point-in-time references in snapshot-capable filesystems. ACL/xattr APIs persist metadata only on filesystems that implement those features.

Delegation tokens persist in `Credentials` and in renewable filesystem state until renewed or replaced. `DelegationTokenRenewer.RenewAction` persists scheduled renewal timing in a delayed queue. Canonical service names are the stable keys used for token lookup.

`FileUtil` operations mostly mutate local filesystem state: recursive deletion, permission/ownership changes, symlink creation, archive extraction, temp-file creation, replacement, and classpath-jar creation. Some helpers bridge local state and distributed filesystems through copy and merge operations.

## Dependencies and Integration Points

This chunk depends on core Hadoop types: `Configuration`, `Path`, `PathFilter`, `RemoteIterator`, `FSDataInputStream`, `FSDataOutputStream`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `Options.ChecksumOpt`, `Options.Rename`, `CreateFlag`, `AclStatus`, `AclEntry`, `FsPermission`, `FsAction`, `UserGroupInformation`, `Credentials`, `Token`, `Progressable`, and Hadoop IO `Writable`.

`FileContext` integrates with `AbstractFileSystem` and with the newer filesystem API style that separates namespace context from concrete filesystem instances. `FileSystem` integrates with concrete implementations such as `LocalFileSystem`, HDFS `DistributedFileSystem`, embedded/composite filesystems, and service loading via `fs.<scheme>.class` configuration keys.

Security integration appears in access checks, ACLs, xattrs, delegation tokens, canonical service names, `Credentials`, `UserGroupInformation`, KMS configuration constants, and secure-random configuration constants. Access checks explicitly warn about time-of-check/time-of-use races and recommend running the actual operation as the desired user instead.

RPC integration is visible in exception documentation for remote filesystems: `RpcClientException`, `RpcServerException`, and `UnexpectedServerException` may surface from many `FileContext` operations. Block locations, replication, server defaults, checksums, snapshots, ACLs, and xattrs are especially tied to HDFS-style remote implementations.

Local platform integration is concentrated in `FileUtil`: Java `File` APIs, shell path conversion, symlink/chmod/chown behavior, Windows-specific permission and symlink limitations, archive extraction, manifest classpath jars, and wrappers that turn ambiguous `File.list*()` null returns into `IOException`.

The JDiff XML itself integrates with API compatibility tooling. Additions, removals, visibility changes, changed exceptions, or changed deprecation status in this file are signals for release compatibility review.

## Risks and Edge Cases

The biggest API risk is compatibility drift. `FileContext`, `FileSystem`, and `FileStatus` are widely consumed, and changing overloads, return types, exceptions, visibility, or deprecation state can break applications and third-party filesystem implementations even when implementation behavior remains similar.

Create flag validation is a correctness boundary. Invalid combinations such as append plus overwrite must be rejected consistently, and path-existence-aware validation must map missing/existing paths to the documented create, append, and overwrite semantics.

Symlink semantics are subtle. Full deletion of a symlink to a directory deletes only the symlink, while content-only deletion of a symlink to a directory deletes the target directory contents. FileContext final-component behavior also varies by operation. Regressions here can cause either unexpected dangling paths or destructive deletion of targets.

`FileContext.access` and `FileSystem.access` are explicitly subject to TOCTOU races. A successful access check is not a guarantee that a later operation will be allowed or will target the same object, especially on remote or concurrently modified filesystems.

`FileSystem` caching can leak resources or reuse state under the wrong user/configuration if callers choose `get` when they needed `newInstance`, or forget to close cached instances during tests. Conversely, `closeAll` and `closeAllForUGI` are dangerous if other code still relies on cached filesystems.

Permission behavior has historical traps. `FileContext.DEFAULT_PERM` used to apply to files and could give files execute bits; newer code should use `DIR_DEFAULT_PERM` or `FILE_DEFAULT_PERM`. The static `FileSystem.create` helper uses two RPCs to set exact permissions, so partial failure or race behavior differs from setting a umask globally.

Statistics reset is intentionally non-obvious. Implementations or tests that assume counters are physically zeroed per thread can misread the design; reset uses a root offset because other threads' thread-local counters cannot be safely mutated.

`FileUtil` local operations are platform-sensitive. Windows symlink creation can fail due to security policy and return a special code; Java readable/writable/executable APIs do not behave uniformly across platforms; revoking execute permission from directories differs on Windows; shell path and classpath-jar logic must account for command-line length and environment expansion.

The chunk ends before the completion of `FileUtil.createJarWithClassPath` documentation and before the `FileUtil` class close. Full analysis of that helper and subsequent nested `FileUtil.HardLink` requires the next chunk.

## Test Signals

Useful validation signals for this chunk include API compatibility checks generated from JDiff: stable class names, method overloads, parameter types, return types, thrown exceptions, field names, visibility, static/final flags, implemented interfaces, and deprecation annotations.

Filesystem behavior tests should cover `FileContext` and `FileSystem` create/open/append/rename/delete/mkdir/list/glob flows across local and HDFS-like implementations, including relative paths, slash-relative paths, fully qualified URIs, working directory changes, default filesystem resolution, and `makeQualified`.

Create semantics tests should cover every documented `CreateFlag` combination, invalid combinations, existing path, missing path, append-only, overwrite-only, create-or-append, create-or-overwrite, `SYNC_BLOCK`, non-recursive create, checksum options, replication, block size, progress callbacks, and exact permission application.

Metadata tests should cover `FileStatus` serialization/deserialization, comparison and equality, symlink targets, encrypted flags, path mutation, permission/owner/group mutation, and content summary quota and human-readable formatting.

Symlink tests should cover final symlink handling for delete, delete-on-exit, rename, get-link-target, get-file-link-status, open/status/checksum/block-location operations that follow links, dangling symlinks, fully qualified targets, partially qualified targets, relative targets, absolute targets, and intermediate symlink resolution.

Security tests should cover access checks, ACL modify/remove/default/remove-all/set/get flows, xattr set/get/list/remove flows with namespace-prefixed names, token acquisition through `addDelegationTokens`, canonical service names, child filesystem token propagation, and renewer scheduling/replacement.

Statistics tests should cover per-thread increments, aggregate reads, reset behavior under concurrent writers, scheme/class statistics lookup, `clearStatistics`, and printed statistics output.

`FileUtil` tests should cover recursive deletion of normal files, directories, symlinks to files, symlinks to directories, content-only deletion through symlink directories, copy/copyMerge local and cross-filesystem paths with delete-source and overwrite variants, archive extraction, shell-path conversion, chmod/chown/permission helpers, Windows-specific permission behavior where available, safe list wrappers converting null returns to `IOException`, temp-file creation, replace-file behavior, and classpath-jar generation on long classpaths.

## Cross-Chunk Notes

Line 5867 starts inside the final field block of `CommonConfigurationKeysPublic`; the class starts in the preceding chunk. Line 11840 stops inside the Javadoc for `FileUtil.createJarWithClassPath(String, Path, Path, Map)`, before the method documentation, `FileUtil` class, and nested `FileUtil.HardLink` entry are complete. The merge lane should combine adjacent chunks for a complete per-file report.

### subset-b-007153: lines 11841-17787

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 11841-17787

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.6.0. It starts at the tail of `org.apache.hadoop.fs.FileUtil`, covers a broad portion of the `org.apache.hadoop.fs` public API surface, then continues through filesystem crypto, FTP, permission, and viewfs packages. It ends in the middle of `org.apache.hadoop.fs.viewfs.ViewFs`, so final per-file reconciliation must merge adjacent chunks before making complete claims about that class.

The descriptor is generated API metadata, not executable code. It records public/protected constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, deprecation notes, and selected Javadocs consumed by API compatibility tooling.

Visible package areas include:

- `org.apache.hadoop.fs`: filesystem wrappers, stream wrappers, constants, shell permission commands, hard links, Hadoop Archives, local filesystem adapters, path and path exception types, read/sync/iterator contracts, trash policies, xattr helpers, checksum options, and create/rename option types.
- `org.apache.hadoop.fs.crypto`: encrypted `FSDataInputStream` and `FSDataOutputStream` wrappers.
- `org.apache.hadoop.fs.ftp`: FTP-backed `FileSystem` and its runtime exception wrapper.
- `org.apache.hadoop.fs.permission`: ACL entry/status builders, permission actions, permission serialization, and a deprecated filesystem access-control exception.
- `org.apache.hadoop.fs.viewfs`: viewfs configuration helpers/constants, mountpoint exception, `ViewFileSystem`, mountpoint marker type, and the beginning of `ViewFs`.

## Purpose

This XML chunk preserves Hadoop Common 2.6.0's filesystem-facing public API contract. The APIs here are the client-side substrate used by HDFS, local filesystems, archive filesystems, FTP integrations, viewfs mount tables, shell commands, path validation, permission and ACL processing, xattr encoding, stream positioning, sync semantics, and trash behavior.

At runtime in Hadoop, these types define how callers discover filesystem implementations, qualify and validate paths, read and write byte streams, propagate permissions and ACLs, move data to trash, resolve mount tables, and adapt special backends such as HAR, local disk, FTP, and encrypted streams. In this descriptor, their purpose is compatibility: downstream projects and tests can compare this release's public contract against other Hadoop releases.

## Important APIs, Types, and Functions

### Filesystem wrappers and constants

- `FileUtil.HardLink` is retained as a deprecated static class extending `org.apache.hadoop.fs.HardLink`; callers are directed to the top-level `HardLink` class.
- `FilterFileSystem` extends `FileSystem` and contains a protected `FileSystem fs` plus `swapScheme`. It forwards almost the full `FileSystem` surface to the wrapped filesystem: initialization, URI/canonical URI, path qualification/checking, block location lookup, `open`, `append`, `concat`, create variants, non-recursive create, replication, rename, delete, list operations, corrupt block iteration, located status iteration, working directory, status, mkdirs, local copy helpers, checksum toggles, owner/time/permission mutation, snapshots, ACLs, xattrs, symlinks, primitive create/mkdir, and child filesystem discovery.
- `FsConstants` exposes public constants for filesystem schemes and URIs: `LOCAL_FS_URI`, `FTP_SCHEME`, `MAX_PATH_LINKS`, `VIEWFS_URI`, and `VIEWFS_SCHEME`. `VIEWFS_URI` is documented as the client-side mount filesystem.

### Stream contracts

- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, and `HasEnhancedByteBufferAccess`. It wraps an `FSInputStream` and provides `seek`, `getPos`, positional `read`, `readFully`, `seekToNewSource`, `getWrappedStream`, `ByteBuffer` reads, file descriptor access, readahead/drop-behind hints, enhanced byte-buffer reads with `ByteBufferPool`, and `releaseBuffer`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable` and `CanSetDropBehind`. Its constructors accept an output stream, optional filesystem statistics, and optional start position. It exposes `getPos`, `close`, `getWrappedStream`, deprecated `sync`, `hflush`, `hsync`, and `setDropBehind`.
- `Seekable`, `PositionedReadable`, and `Syncable` are core stream interfaces. `PositionedReadable` explicitly promises positional reads that do not change the current stream offset and are thread-safe. `Syncable` distinguishes `hflush`, which makes data visible to new readers, from `hsync`, which is closer to POSIX fsync semantics.
- `ReadOption` is an enum for filesystem read options, and `ZeroCopyUnavailableException` signals failure to provide enhanced zero-copy buffer access.

### Errors, server defaults, shell helpers, and status values

- `FSError` is an `Error` for unexpected native filesystem/disk errors.
- `FSExceptionMessages` centralizes standard stream error strings such as closed stream, negative seek, and seek past EOF.
- `FsServerDefaults` implements `Writable` and carries default values reported from a filesystem service: block size, bytes per checksum, write packet size, replication, file buffer size, encrypted data transfer flag, trash interval, and checksum type.
- `FsStatus` implements `Writable` for capacity, used bytes, and remaining bytes.
- `FsShell.Help` and `FsShell.Usage` are protected shell commands for short usage and long descriptions. `FsShellPermissions.Chmod`, `Chown`, and `Chgrp` expose shell permission command parsing and per-path processing. `Chmod` holds a `ChmodParser`, while `Chown` stores parsed owner and group.

### Hard links and Hadoop Archives

- `HardLink` provides static hard-link operations for Unix/Linux, Windows through winutils, and Mac OS X. Public APIs include `createHardLink`, `createHardLinkMult`, and `getLinkCount`; protected helpers expose command argument length calculations for unit testing. The class documents a move away from the older non-thread-safe `FileUtil` nested class toward static methods that allocate fresh buffers per call.
- `HardLink.LinkStats` exposes mutable public counters for directories, single links, multi-link calls, files linked through multi-link calls, empty directories, and physical file copies. It is explicitly not thread-safe and is intended for knowledgeable clients.
- `HarFileSystem` implements the `har` filesystem over an underlying filesystem. It initializes from URIs such as `har://underlyingfsscheme-host:port/archivepath` or `har:///archivepath`, exposes archive version and hash helpers, resolves archive paths, delegates canonical URI and child filesystem information to the underlying filesystem for delegation-token behavior, and reads archive contents through `_masterindex`, `_index`, and `part-*` files.
- `HarFileSystem` is effectively read-only in this surface. Its docs mark many mutating operations as not implemented: create, non-recursive create, append, replication, delete, mkdirs, local copy into the archive, local output staging, ownership, permissions, and related mutations. `getFileChecksum` returns null because no checksum algorithm is implemented for HAR.
- `HarFs` is an `AbstractFileSystem` adapter via `DelegateToFileSystem`, exposing `getUriDefaultPort`.

### Local filesystem adapters

- `LocalFileSystem` extends `ChecksumFileSystem` for the checksumed local filesystem. It exposes scheme `file`, raw filesystem access, `pathToFile`, local copy helpers, checksum failure quarantine through `reportChecksumFailure`, and local symlink operations.
- `RawLocalFileSystem` extends `FileSystem` for direct local disk access. Its surface includes optional `stat` use, `pathToFile`, local URI/initialization, `open`, `append`, `create`, `createOutputStream`, non-recursive creates, rename, recursive delete, directory creation, primitive mkdir, working directory state, local-output staging, file status, owner/permission/time mutation through native commands or local APIs, symlink support, link status, and link target lookup.

### Paths and path-related exceptions

- `Path` is the central immutable-ish path value type implementing `Comparable`. Constructors accept strings, URIs, parent/child combinations, and scheme/authority/path components. It supports URI conversion, filesystem lookup from `Configuration`, root/absolute checks, parent/name/depth/suffix operations, equality/hash/compare behavior, path qualification, Windows absolute path detection, path merging, and scheme/authority stripping.
- Public `Path` constants include slash separator, separator char, current directory marker, and a `WINDOWS` flag.
- `PathFilter` is the one-method predicate interface for filtering `Path` values.
- `PathIOException` is the base path-aware `IOException` with path, optional target path, optional operation, and formatted message support. Subclasses map to POSIX-like conditions: `PathAccessDeniedException`, `PathExistsException`, `PathIsDirectoryException`, `PathIsNotDirectoryException`, `PathIsNotEmptyDirectoryException`, `PathNotFoundException`, `PathOperationException`, and `PathPermissionException`.
- `InvalidPathException`, `InvalidRequestException`, `ParentNotDirectoryException`, and `UnsupportedFileSystemException` cover invalid path syntax, malformed user requests, parent-not-directory failures, and unsupported filesystem schemes.

### File status, checksum, and operation options

- `LocatedFileStatus` extends `FileStatus` by adding `BlockLocation[]`. It can be constructed from an existing `FileStatus` plus block locations or from full file metadata including optional symlink path.
- `MD5MD5CRC32CastagnoliFileChecksum` and `MD5MD5CRC32GzipFileChecksum` specialize `MD5MD5CRC32FileChecksum` with distinct `DataChecksum.Type` values.
- `Options.ChecksumOpt` carries checksum type and bytes-per-checksum, supports disabled checksums, and has helper methods to merge default and user-provided checksum options while preserving backward compatibility for the older bytes-per-checksum argument.
- `Options.CreateOpts` provides varargs-style create option wrappers: block size, buffer size, replication factor, bytes per checksum, checksum parameter, permissions, create-parent flag, progress callback, and individual `getValue` accessors.
- `Options.Rename` is an enum-like rename option type with byte value conversion.

### Trash and remote iteration

- `RemoteIterator<E>` is a remote-aware iterator whose `hasNext` and `next` can throw `IOException`; it is used by filesystem listing APIs that may fetch results incrementally.
- `Trash` is a configured facade over pluggable trash policies. It can choose the appropriate trash volume for symlinks or mount points using the resolved fully qualified path, move items to trash, create checkpoints, expunge old checkpoints, and provide an emptier runnable intended for superuser execution.
- `TrashPolicy` is the abstract policy contract. Implementations initialize with `Configuration`, `FileSystem`, and home path; report enablement; move paths to trash; create/delete checkpoints; expose current trash directory; and provide an emptier. Protected fields hold the filesystem, trash path, and deletion interval. `getInstance` resolves `fs.trash.classname`.

### XAttrs and crypto streams

- `XAttrCodec` encodes and decodes extended attribute byte arrays for shell, HTTP, and display use. Decoding recognizes `0x`/`0X` hexadecimal, `0s`/`0S` base64, double-quoted text, or unquoted text. Encoding emits quoted text, hex, or base64 according to the requested codec.
- `XAttrSetFlag` validates xattr set semantics against whether an attribute already exists and the supplied `EnumSet` of flags.
- `CryptoFSDataInputStream` wraps an `FSDataInputStream` with a `CryptoCodec`, buffer size, key, and IV.
- `CryptoFSDataOutputStream` wraps an `FSDataOutputStream` with a `CryptoCodec`, buffer size, key, and IV, and exposes `getPos`.

### FTP filesystem

- `FTPException` wraps FTP-related failures in a runtime exception.
- `FTPFileSystem` extends `FileSystem` with scheme `ftp` and uses Apache Commons Net. It exposes initialization from URI/configuration, `open`, `create`, unsupported `append`, `delete`, URI/status/listing operations, mkdirs, rename, working/home directory access, and working directory mutation.
- Public FTP constants include logging, default buffer and block sizes, user/host/port/password configuration prefixes, and `E_SAME_DIRECTORY_ONLY`. The `create` method warns that the returned stream must be closed before using other APIs of the class or calls may block.

### Permission and ACL model

- `org.apache.hadoop.fs.permission.AccessControlException` is deprecated in favor of `org.apache.hadoop.security.AccessControlException`, but remains public for compatibility and remote exception unwrapping.
- `AclEntry` is an immutable ACL entry with type, optional name, permission, and scope. It supports equality/hash/string behavior and static parsing/formatting helpers: `parseAclSpec`, `parseAclEntry`, and `aclSpecToString`.
- `AclEntry.Builder` provides fluent setters for type, name, permission, scope, and `build`; absent scope defaults to access scope.
- `AclEntryScope` and `AclEntryType` are enum types for ACL scope and type.
- `AclStatus` is an immutable ACL status value containing owner, group, sticky bit, and an ordered unmodifiable list of entries. `AclStatus.Builder` sets owner/group/sticky bit and adds one or more entries before `build`.
- `FsAction` is the permission action enum. It exposes symbolic representation, implication checks, boolean-style `and`, `or`, `not`, and `getFsAction` for 3-character strings such as `rwx`.
- `FsPermission` implements `Writable` and models user/group/other actions plus sticky, ACL, and encrypted bits. It can be built from actions, a short mode, another permission, or octal/symbolic string; serialized/deserialized; converted to normal and extended shorts; masked by umask; read from and written to configuration; and produced as default directory, file, cache pool, or compatibility defaults.

### Viewfs configuration and filesystem facade

- `ConfigUtil` provides helpers for viewfs mount table configuration: deriving mount table prefixes, adding default or named mount links, setting home directory config, and reading home directory values.
- `Constants` exposes viewfs config key components: mount-table prefix, home directory key, default mount table name, full prefix for the default table, simple link key, merge link key, merge-slash key, and read-only `PERMISSION_555`.
- `NotInMountpointException` is an `UnsupportedOperationException` for operations on paths not mounted through viewfs.
- `ViewFileSystem` extends `FileSystem` and implements a client-side mount table with the same spec as `ViewFs`. It exposes scheme `viewfs`, constructor paths for `FileSystem#createFileSystem` and direct app use, initialization from URI/configuration, trash location lookup, URI/path resolution, home and working directories, and delegation of common filesystem operations to mounted targets: create, append, delete, block locations, checksum, file status, access, listing, mkdirs, open, rename, owner/permission/replication/time mutation, ACLs, xattrs, checksum toggles, server defaults, content summary, child filesystems, and mount point listing.
- `ViewFileSystem.MountPoint` is visible as a public static marker/data class in this slice, but no members are exposed here.
- The visible start of `ViewFs` extends `AbstractFileSystem`. It has a configuration constructor and begins exposing server defaults, default port, home directory, path resolution, `createInternal`, delete, block locations, checksum, status, access, link status, filesystem status, status iteration, listing, mkdir, open, and internal rename operations. The chunk ends before `ViewFs` is complete.

## Control Flow

`FilterFileSystem` control flow is pure delegation. Construction or initialization installs the wrapped filesystem; all path, stream, metadata, mutation, snapshot, ACL, xattr, checksum, and child-filesystem calls are forwarded unless subclasses override behavior. This makes it the extension point for wrappers that alter scheme handling, metrics, permissions, or other behavior while preserving the underlying filesystem contract.

Stream control flow is split between cursor-based and positional access. `FSDataInputStream.seek` changes the stream cursor, `getPos` reports it, and normal reads consume from it. Positional reads accept an explicit offset and are documented by `PositionedReadable` as not changing the current offset. Enhanced `ByteBuffer` reads use a caller-supplied `ByteBufferPool` and must be paired with `releaseBuffer`. `FSDataOutputStream` writes through its wrapped output stream, while `hflush` and `hsync` establish visibility/durability boundaries.

HAR access flow is index-driven. Initialization binds a HAR filesystem to an archive URI and underlying filesystem. Reads and listings consult `_masterindex` and `_index` to find part files, offsets, lengths, and directory entries. Opening a file returns an input stream that reads the correct segment of a `part-*` file and fakes EOF at the archived file boundary. Block locations are retrieved from the underlying filesystem and adjusted to archive-contained offsets and lengths.

Local filesystem flow differs between checksumed and raw variants. `LocalFileSystem` wraps a raw filesystem with checksum behavior and moves corrupt data/checksum files aside on checksum failures. `RawLocalFileSystem` maps `Path` to `java.io.File`, performs direct local IO, creates directories recursively when requested, and uses local ownership/permission/time and symlink operations where supported.

Trash flow is policy based. `Trash.moveToAppropriateTrash` resolves symlinks or mount points to find the filesystem volume that should own the trash location, then invokes a configured `TrashPolicy`. Policies initialize from configuration and filesystem state, decide enablement, move paths into current trash, checkpoint current trash, delete old checkpoints, and optionally expose a superuser emptier runnable.

Viewfs flow is mount-table based. `ConfigUtil` and `Constants` encode links and home directories into configuration. `ViewFileSystem` or `ViewFs` initializes a client-side mount table from that configuration, resolves an incoming viewfs path to a target filesystem/path, and forwards operations to that target. Operations on non-mounted paths may fail with `NotInMountpointException` or appropriate file/path exceptions. `getChildFileSystems` and mount point access expose the underlying filesystem set for delegation tokens and management.

Permission and ACL flow starts from strings, shorts, builders, or configuration. `FsPermission` converts between action triples and short wire forms, applies umasks, and persists through `Writable`. `AclEntry` parses shell-style ACL specs into immutable entries, builders assemble ACL entries/statuses, and filesystem methods in `FilterFileSystem` and `ViewFileSystem` pass ACL and xattr mutations through to the backing implementation.

FTP flow is remote-session oriented. Initialization configures host, port, user, and password from URI/configuration. File operations issue FTP commands via Commons Net. The `create` documentation is a critical sequencing constraint: the output stream must be closed before another FTPFileSystem API call, or later calls may block.

## State and Persistence Behavior

The XML itself persists API metadata for JDiff. Runtime persistence implied by the APIs includes stream positions, filesystem metadata, permission/xattr/ACL records, trash directories, HAR index files, server defaults, and `Writable` wire forms.

`FilterFileSystem` stores mutable wrapper state in `fs` and optional `swapScheme`. Its behavior depends on lifecycle ordering: callers construct, initialize with URI/configuration, then use delegated operations. `close` propagates cleanup to the wrapped filesystem.

`FSDataInputStream` and `FSDataOutputStream` maintain stream-local state through wrapped stream cursor/position and optional statistics. Enhanced byte buffers have pooled ownership state: callers must release buffers obtained from enhanced reads. Output stream sync calls represent persistence/visibility boundaries for data already written.

`FsServerDefaults`, `FsStatus`, and `FsPermission` implement `Writable`; their fields are intended for RPC or persisted configuration/storage exchange. `FsPermission.toExtendedShort` can encode bits outside classic permission mode, including ACL and encryption indicators, which makes the extended format sensitive for backward compatibility.

`HardLink.LinkStats` is mutable and public, but explicitly not thread-safe. Static hard-link operations themselves are documented as thread-safe after moving away from shared buffers.

`HarFileSystem` state is rooted in persistent archive metadata. `_masterindex` provides hash-range indirection into `_index`; `_index` maps logical paths to part files, offsets, lengths, and directory metadata. HAR permissions are not persisted when creating an archive, so `getFileStatus` reports permissions from archive index files rather than original file permissions.

`RawLocalFileSystem` state includes working directory, local file metadata, and filesystem status from local disk. `LocalFileSystem` adds checksum files and bad-file quarantine behavior. Symlink support depends on platform capability and local implementation support.

`TrashPolicy` stores the target `FileSystem`, trash path, and deletion interval. Trash checkpointing and expunge mutate persistent directories in the filesystem, while `Trash` itself is a configured facade.

`AclEntry` and `AclStatus` are immutable once built. `FsPermission` can be mutable through `fromShort`/`readFields`, but immutable instances are available through `createImmutable`. Umask state is persisted in `Configuration` under current and deprecated labels.

`ViewFileSystem` and `ViewFs` are configuration-backed. Mount tables and home directories live in `Configuration` keys; runtime state is the parsed mount table and working directory. Target filesystem state remains in the mounted filesystems, not in viewfs itself.

## Dependencies and Integration Points

- Core filesystem types depend on `java.io`, `java.net.URI`, Java collections, `Configuration`, Hadoop `Path`, `FileStatus`, `BlockLocation`, `ContentSummary`, `FsStatus`, `FsServerDefaults`, `RemoteIterator`, `Progressable`, `Writable`, and permission/xattr/ACL types.
- Stream APIs integrate with Hadoop stream capability interfaces (`Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `Syncable`) and `ByteBufferPool`.
- Local filesystem APIs bridge Hadoop `Path` to `java.io.File`, native platform commands/utilities for chmod/chown/stat/symlinks, and checksum quarantine behavior from `ChecksumFileSystem`.
- HAR APIs integrate with underlying filesystems for data reads, block locations, canonical URI, server defaults, and delegation-token child filesystem discovery.
- FTP APIs integrate with Apache Commons Net, Hadoop configuration keys, and the `FileSystem` contract.
- Permission APIs integrate with Hadoop shell parsing (`ChmodParser`), filesystem metadata, configuration, ACL lists, and `org.apache.hadoop.security.AccessControlException` for newer access-control failures.
- Viewfs APIs integrate with configuration naming conventions, mount target URIs, `FileSystem` and `AbstractFileSystem`, delegation-token discovery through child filesystems, trash location selection, and path resolution across mount boundaries.
- Crypto stream wrappers integrate with `org.apache.hadoop.crypto.CryptoCodec`, encryption keys, IVs, and the standard FS data stream wrappers.

## Risks and Edge Cases

- This chunk begins after the start of `FileUtil` and ends inside `ViewFs`. Merge/reconciliation must combine adjacent chunks for complete class-level conclusions.
- `FilterFileSystem` must forward new `FileSystem` methods consistently. Missing delegation for snapshots, ACLs, xattrs, symlinks, checksums, or child filesystems would break wrappers and token discovery.
- Path qualification and scheme swapping are compatibility-sensitive. `Path.isAbsolute` is documented as ambiguous because it returns true even with scheme and authority, so tests must preserve historical behavior.
- `FSDataInputStream` combines cursor reads, positional reads, and pooled byte-buffer reads. Bugs can corrupt stream position, leak buffers, or violate the thread-safety promise of positional reads.
- `FSDataOutputStream.sync` is deprecated but still public. Removing or altering it can break older callers even though `hflush` is the replacement.
- Hard-link multi-create splits command invocations to respect platform command-line limits. Windows, Mac, and Unix command length, path quoting, and link count behavior need platform-specific coverage.
- `HardLink.LinkStats` is public and mutable but not thread-safe; sharing one instance across parallel operations can produce misleading counters.
- HAR is read-only for most mutating operations and does not preserve original permissions. Callers expecting normal filesystem mutation or permission fidelity can fail unless those not-implemented paths are explicit and tested.
- HAR block location adjustment is offset-sensitive; incorrect segment arithmetic can report wrong locality or lengths for files embedded inside `part-*` files.
- Local symlink support and owner/permission mutation depend on platform and native tooling. Windows privilege failures, missing winutils, and command errors are important compatibility cases.
- FTP stream lifecycle is fragile: using other APIs before closing a create stream can block. Rename/delete/list semantics also depend on FTP server behavior and current working directory state.
- `FsPermission.toExtendedShort` can encode ACL and encryption bits beyond traditional mode bits. Consumers that assume only `00000-01777` may silently drop metadata.
- ACL parsing has two modes: with permissions for set operations and without permissions for remove operations. Accepting the wrong form can create incorrect ACL mutations.
- XAttr value decoding accepts multiple textual encodings. Prefix handling, quoted strings, invalid base64/hex, empty values, and round-trip formatting need regression tests.
- Viewfs path resolution crosses filesystem boundaries. Trash location, working directory, child filesystem enumeration, ACL/xattr delegation, and NotInMountpoint failures must all match mounted target behavior.
- `ViewFileSystem` and `ViewFs` expose parallel old and new filesystem APIs. Inconsistent behavior between them can create subtle client differences.

## Test Signals

- API compatibility tests should assert the presence, visibility, checked exceptions, deprecation text, and inheritance/implements lists for `FilterFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `Path`, `RawLocalFileSystem`, `FsPermission`, `AclEntry`, `ViewFileSystem`, and the visible `ViewFs` methods.
- Delegation wrapper tests should use a fake `FileSystem` under `FilterFileSystem` and verify calls forward arguments and return values for create/open/list/delete, ACLs, xattrs, snapshots, symlinks, checksums, server defaults, and child filesystem discovery.
- Stream tests should cover seek, get position, positioned read without cursor movement, readFully EOF behavior, byte-buffer read/release, readahead/drop-behind unsupported cases, `hflush`, `hsync`, and deprecated `sync`.
- Path tests should cover URI construction, parent/child resolution, Windows absolute path detection, scheme/authority stripping, `mergePaths`, root/parent/name/depth behavior, equality/hash/compare, and `makeQualified`.
- Local filesystem tests should cover recursive delete failure on non-empty directories when recursive is false, mkdir existence behavior, create-non-recursive parent handling, local checksum failure quarantine, symlink status versus target status, and owner/permission/time updates.
- HAR tests should validate URI initialization forms, version reading, path hash lookup, index/master-index lookup, file status for files/directories, list status, open segment EOF boundaries, block location offset/length adjustment, null checksum behavior, and explicit failures for unsupported mutations.
- Hard-link tests should cover single links, multi-link splitting at command length boundaries, link counts, missing source/target directories, platform-specific command limits, and public `LinkStats` reporting.
- Permission tests should cover octal and symbolic parsing, `Writable` round trips, immutable creation, umask current/deprecated configuration keys, `toShort` versus `toExtendedShort`, ACL and encrypted bits, action implication/and/or/not, and default directory/file/cache pool permissions.
- ACL tests should cover parsing with and without permissions, default versus access scope, named and unnamed entries, builder defaults, `aclSpecToString` round trips, ordered unmodifiable status entries, and equality/hash behavior.
- XAttr tests should cover text, quoted text, hex, base64, invalid encodings, encode/decode round trips, and `XAttrSetFlag.validate` for create-only, replace-only, and create-or-replace cases.
- FTP tests should use a controllable server or mock to verify initialization from config, open/create stream closure sequencing, list/status conversion, same-directory rename constraints, unsupported append, and working directory handling.
- Trash tests should cover disabled trash, already-in-trash paths, symlink/mountpoint trash resolution, checkpoint creation, expunge behavior, policy factory configuration, and emptier runnable creation.
- Viewfs tests should cover config key generation, adding default and named mount links, home directory config, mount resolution, operations delegated to target filesystems, non-mounted path failures, child filesystem enumeration, mount point listing, trash location, and behavior parity between `ViewFileSystem` and `ViewFs` for overlapping methods.

### subset-b-007154: lines 17788-23751

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 17788-23751

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop Common 2.6.0. It starts inside the tail of `org.apache.hadoop.fs.viewfs.ViewFs`, covers `ViewFs.MountPoint`, all visible APIs in `org.apache.hadoop.ha`, `org.apache.hadoop.ha.protocolPB`, and `org.apache.hadoop.http.lib`, then enters `org.apache.hadoop.io` and continues through the beginning of `SequenceFile.Sorter.merge(...)`.

The source is generated API metadata, not executable implementation. The research surface is therefore the compatibility contract: public/protected types, inheritance, implemented interfaces, constructors, method signatures, fields, checked exceptions, synchronization markers, deprecation markers, and embedded Javadocs.

## Purpose

The `ViewFs` portion documents the client-side mount-table filesystem. `ViewFs` composes a namespace from configured links to local, HDFS, S3, and other filesystems, and exposes regular `AbstractFileSystem` operations plus ACL, xattr, symlink, delegation-token, and mount-point APIs.

The HA portion defines client-facing high availability contracts: leader-election callbacks, health monitoring, active/standby transitions, fencing configuration and execution, admin targets, protocol state enums, and exception types used by failover controllers and service implementations.

The protocol PB portion exposes protobuf-backed RPC bridge types for HA and ZKFC protocols. The HTTP portion exposes a configurable static-user servlet filter for web UIs.

The `org.apache.hadoop.io` portion covers Hadoop's core binary serialization and file-format API: `Writable` wrappers, binary comparators, byte-buffer pools, stream utilities, secure local-file opening, `MapFile`/`ArrayFile`/`BloomMapFile`, and the start of `SequenceFile` reader/sorter APIs.

## Important APIs, Types, and Functions

### ViewFs

- `ViewFs` methods in this slice include `access`, `getFileLinkStatus`, `getFsStatus`, `listStatusIterator`, `listStatus`, `mkdir`, `open`, two `renameInternal` overloads, symlink support, owner/permission/replication/time/checksum setters, `getMountPoints`, `getDelegationTokens`, `isValidName`, ACL mutation/status APIs, and xattr get/list/set/remove APIs.
- The embedded Javadoc defines `viewfs:///` as an in-memory client-side mount table initialized from `fs.viewfs.mounttable.*` configuration entries. It documents normal links and not-yet-implemented merge mounts.
- `ViewFs.MountPoint` is a public static nested class representing mount table entries, with no methods exposed in this chunk.

### High Availability

- `ActiveStandbyElector.ActiveStandbyElectorCallback` defines election callbacks: `becomeActive`, `becomeStandby`, `enterNeutralMode`, `notifyFatalError`, and `fenceOldActive`. Javadocs say callbacks run on ZooKeeper client threads, must return quickly, and may arrive while earlier actions are still in progress.
- `ActiveStandbyElector.ActiveNotFoundException`, `FailoverFailedException`, `HealthCheckFailedException`, `ServiceFailedException`, and `BadFencingConfigurationException` carry HA failure modes for missing active leader, failover failure, failed health checks, failed service state operations, and invalid fencing configuration.
- `FenceMethod` is the operator-extensible fencing interface. It exposes `checkArgs(String)` for startup validation and `tryFence(HAServiceTarget, String)` for runtime fencing attempts.
- `HAServiceProtocol` defines RPC-visible service controls: `monitorHealth`, `transitionToActive`, `transitionToStandby`, `getServiceStatus`, and `versionID`. Nested `HAServiceState` has active/standby plus startup/shutdown states; `RequestSource` and `StateChangeRequestInfo` identify automatic vs CLI-style transition sources.
- `HAServiceProtocolHelper` wraps calls and unwraps `RemoteException` into specific exceptions.
- `HAServiceTarget` abstracts an admin target with service and ZKFC IPC addresses, fencer access, preflight fencing validation, proxy creation, fencing parameter construction, and auto-failover enablement.
- `ShellCommandFencer` and `SshFenceByTcpPort` are concrete `FenceMethod` implementations. The shell fencer runs configured commands with Hadoop configuration-derived environment variables and no built-in timeout. The SSH fencer uses `fuser`/`nc` against the target service TCP port and requires passwordless SSH key configuration.
- `HAAdmin.UsageInfo` is a protected static helper carrying command `args` and `help` strings.

### Protocol and HTTP Integration

- `HAServiceProtocolPB` and `ZKFCProtocolPB` extend generated protobuf blocking interfaces plus `VersionedProtocol`, making them Hadoop IPC protocol surfaces.
- `ZKFCProtocolClientSideTranslatorPB` implements `ZKFCProtocol`, `Closeable`, and `ProtocolTranslator`; it creates a PB client from an address, configuration, socket factory, and timeout, and exposes `cedeActive`, `gracefulFailover`, `close`, and `getUnderlyingProxyObject`.
- `StaticUserWebFilter` extends `FilterInitializer` and installs `StaticUserFilter`, a `javax.servlet.Filter` with `init`, `doFilter`, and `destroy`. Its package docs identify `hadoop.http.filter.initializers` as the configuration hook and describe the filter as mapping all web UI users to a static configured user.

### Hadoop I/O Serialization and Utilities

- `AbstractMapWritable` is the shared `Writable`/`Configurable` base for map writables. It tracks class-to-id and id-to-class maps per instance, synchronizes map updates/copying, and limits per-map dynamic class ids to 1..127.
- `ArrayFile`, `ArrayFile.Reader`, and `ArrayFile.Writer` layer dense long-indexed value access on top of `MapFile`; reader methods `seek`, `next`, `key`, and `get` are synchronized.
- `ArrayPrimitiveWritable` wraps primitive arrays without copying and serializes them with an optimized wire format. It exposes component-type inspection, declared component-type checks, `set`, `get`, `write`, and `readFields`.
- `ArrayWritable`, `EnumSetWritable`, `MapWritable`, `GenericWritable`, and `ObjectWritable` are container/polymorphic writable contracts. `GenericWritable` stores a type index from subclass-provided `getTypes()`, while `ObjectWritable` writes class names and handles `Writable`, `String`, primitive types, and arrays.
- Primitive writable classes in this chunk include `BooleanWritable`, `ByteWritable`, `DoubleWritable`, `FloatWritable`, `IntWritable`, `LongWritable`, and their optimized `WritableComparator` subclasses. They provide constructors, `set`, `get`, `readFields`, `write`, equality, hash, compare, and string conversion.
- `BinaryComparable`, `BytesWritable`, `RawComparator`, and optimized comparator subclasses define byte-level comparison paths that avoid full object deserialization.
- `ByteBufferPool` and `ElasticByteBufferPool` define direct/heap `ByteBuffer` leasing. `ElasticByteBufferPool` is synchronized and returns the smallest cached buffer with sufficient capacity, with no cache-size limit.
- `CompressedWritable` stores writable data compressed and lazily inflates via `ensureInflated`, with subclass hooks `readFieldsCompressed` and `writeCompressed`.
- `DataInputByteBuffer`, `DataOutputByteBuffer`, and `DataOutputOutputStream` bridge Hadoop serialization with `ByteBuffer`, `DataInput`, `DataOutput`, and `OutputStream` APIs.
- `DefaultStringifier` implements `Stringifier<T>` with Base64-encoded serialized objects, and provides static `store`, `load`, `storeArray`, and `loadArray` helpers for `Configuration`.
- `IOUtils` provides stream copy overloads, count-limited copies, compressed-data read wrapping, `readFully`, `skipFully`, cleanup/close helpers, socket close, and full `ByteBuffer` writes to channels.
- `MapFile` exposes filesystem operations and sorted key/value directory layout: `rename`, `delete`, `fix`, `main`, `INDEX_FILE_NAME`, and `DATA_FILE_NAME`. `MapFile.Reader` provides key/value class lookup, comparator/options, open/reset, approximate middle/final key retrieval, seek/next/get/getClosest, and close. `MapFile.Writer` provides many constructors and options for key/value class, comparator, compression, progress, index interval configuration, close, and sorted append.
- `BloomMapFile` adds Bloom-filter membership acceleration around `MapFile`, with `BLOOM_FILE_NAME`, `HASH_COUNT`, reader `probablyHasKey`, fast `get`, `getBloomFilter`, and writer append/close behavior.
- `MD5Hash` is a `WritableComparable` fixed-size digest holder with constructors from hex/bytes, digest helpers for byte arrays, input streams, strings, and legacy `UTF8`, thread-local digester access, half/quarter digest projections, hex parsing, and optimized comparator.
- `MultipleIOException` aggregates multiple `IOException` instances and exposes `createIOException` to return a single exception or wrapper.
- `NullWritable` is the singleton no-data writable and has a comparator optimized for its empty serialized form.
- `ReadaheadPool.ReadaheadRequest` represents an outstanding native readahead operation with `cancel`, offset, and length.
- `SecureIOUtils` provides secure local-file open/create helpers that check expected owner/group when security is enabled and avoid symlink traversal. It includes forced protected variants for tests and `AlreadyExistsException` for create collisions.
- `SequenceFile` APIs in this slice include default compression-type configuration, many `createWriter` overloads, `SYNC_INTERVAL`, `CompressionType`, `Metadata`, `Reader`, `Reader.Option`, and part of `Sorter`. Reader options cover file, stream, start, length, and buffer size; reader operations expose key/value classes, compression metadata, current value retrieval, typed and raw iteration, seeking, sync marks, position, and close. `Sorter` exposes constructors, merge factor/memory/progress setters, sort, sort-and-iterate, and initial merge overloads.

## Control Flow

The XML has no runtime control flow, but the APIs imply several key flows:

- ViewFs path operations resolve a caller path through the in-memory mount table to a target filesystem, then delegate file status, open, list, mkdir, rename, ACL, xattr, and token operations. Symlink and unresolved-link exceptions remain part of the visible control path.
- HA election flow is callback-driven. ZooKeeper election state causes `becomeActive`, `becomeStandby`, or `enterNeutralMode`; a failed active transition throws `ServiceFailedException` and makes the elector rejoin after a delay; fatal ZooKeeper or ACL conditions call `notifyFatalError`; failed prior actives can trigger `fenceOldActive`.
- HA admin/failover flow validates fencing configuration, builds an `HAServiceTarget`, obtains service/ZKFC proxies, monitors health, requests state transitions with `StateChangeRequestInfo`, and fences stale actives through ordered `FenceMethod` implementations.
- PB translator flow adapts client calls such as `cedeActive` and `gracefulFailover` into the generated protobuf blocking interface and exposes the underlying proxy for IPC lifecycle management.
- Servlet filter flow initializes from `hadoop.http.filter.initializers`, wraps incoming servlet requests with a static user identity, then passes control along the `FilterChain`.
- Writable serialization is caller-driven: callers reuse mutable instances, call `write(DataOutput)`, and call `readFields(DataInput)` to mutate existing storage. Container writables add class ids, class names, element types, or bounded type indexes before nested values.
- Binary comparison flow prefers `RawComparator.compare(byte[], int, int, byte[], int, int)` for serialized keys. Primitive and digest comparators provide optimized byte-slice implementations.
- MapFile/ArrayFile/BloomMapFile flow writes sorted keys to a `data` file with periodic entries in an `index` file; readers seek through the index and data. ArrayFile treats long positions as dense keys; BloomMapFile tests membership before doing slower map lookup.
- SequenceFile reader flow opens from a path or stream, reads headers/metadata/classes/compression state, iterates typed or raw records, and uses sync markers to seek from arbitrary split positions to record boundaries. Sorter flow reads SequenceFile inputs, spills/sorts/merges with a `RawComparator`, writes output, and optionally deletes inputs.

## State and Persistence Behavior

The JDiff file itself persists public API metadata for release compatibility checks. It does not execute code or store application data.

Several described APIs are persistence-sensitive. `Writable` implementations, `ObjectWritable`, `GenericWritable`, `ArrayPrimitiveWritable`, `MapWritable`, `EnumSetWritable`, `MD5Hash`, `MapFile`, `BloomMapFile`, and `SequenceFile` define durable binary formats used by RPC, MapReduce shuffle/sort, SequenceFiles, MapFiles, and configuration serialization. Changes to field order, class-name encoding, dynamic class ids, enum element types, comparator order, or compression metadata would break compatibility.

ViewFs mount state is client-local and configuration-derived. The mount table lives in memory and is initialized from `fs.viewfs.mounttable.*` keys; delegation tokens, ACLs, xattrs, and file data belong to the delegated target filesystems rather than ViewFs itself.

HA state is externally coordinated. Active/standby leadership and neutral mode derive from ZooKeeper election state, while fencing effects are outside the process: shell commands, SSH, process killing, network checks, or vendor-specific implementations. `HAServiceTarget.getFencingParameters()` produces environment-like state for scripts.

Mutable backing storage is part of the I/O contract. `ArrayPrimitiveWritable` does not copy the underlying primitive array; `BytesWritable` exposes backing bytes and has separate logical length/capacity; byte-buffer pools recycle mutable buffers; `CompressedWritable` keeps compressed state until inflation; `SequenceFile.Reader` and `MapFile.Reader` reuse caller-provided key/value instances.

Configuration persistence appears through `DefaultStringifier.store/load/storeArray/loadArray`, `SequenceFile.setDefaultCompressionType`, `MapFile.Writer.setIndexInterval(Configuration, int)`, static web filter initializer configuration, and ViewFs mount-table keys.

File persistence appears through local files opened by `SecureIOUtils`, MapFile directories with `data` and `index` files, BloomMapFile sidecar Bloom data, ArrayFile dense key/value storage, and SequenceFile binary key/value files with compression type, metadata, sync markers, and optional raw record paths.

## Dependencies and Integration Points

These APIs integrate with Java `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `File`, `RandomAccessFile`, `FileInputStream`, `FileOutputStream`, `Socket`, `ByteBuffer`, `FileChannel`, `WritableByteChannel`, collections, `MessageDigest`, `Comparator`, `Closeable`, servlet `Filter`, servlet request/response/chain/config, and `SocketFactory`.

Hadoop integration points include:

- `org.apache.hadoop.conf.Configuration`, `Configurable`, `Configured`, and `SerializationFactory` for I/O object configuration, stringification, fencer configuration, ViewFs mount tables, and web filter setup.
- `org.apache.hadoop.fs.Path`, `FileSystem`, `AbstractFileSystem`, `FSDataInputStream`, `FileStatus`, `FsStatus`, `RemoteIterator`, `FsPermission`, ACL and xattr types, symlink exceptions, and filesystem create/status semantics.
- `org.apache.hadoop.security.AccessControlException` and delegation-token flows for ViewFs and HA service calls.
- ZooKeeper-backed HA election and ZKFC protocols through `ActiveStandbyElector` callbacks and `ZKFCProtocol`.
- Hadoop IPC and protobuf through `VersionedProtocol`, generated HA/ZKFC protocol blocking interfaces, and client-side PB translators.
- `NodeFencer`, `HAServiceStatus`, `HAAdmin`, `Progressable`, `WritableComparator`, `CompressionCodec`, and `SequenceFile.Writer/Reader` option interfaces.
- Native/security dependencies in `SecureIOUtils` and `ReadaheadPool`, especially owner/group checks, symlink avoidance, and platform-specific readahead behavior.

## Risks and Edge Cases

- This chunk starts inside `ViewFs` and ends inside `SequenceFile.Sorter.merge`; adjacent chunks must be reconciled before making final file-wide claims about those classes.
- JDiff exposes signatures and Javadocs, not implementation bodies. Exact mount resolution, buffer sizing, synchronization details, exception messages, and filesystem side effects require source validation.
- ViewFs is client-side and in-memory. Stale or inconsistent configuration can produce namespace views that differ between clients, and merge mounts are documented as not implemented.
- HA callbacks run on ZooKeeper client threads and can overlap with prior action handling. Slow callbacks, blocking RPCs, or non-idempotent transition logic can cause election stalls or inconsistent active/standby behavior.
- `enterNeutralMode` exists to reduce split-brain risk during ZooKeeper disconnects; services that ignore it may keep changing shared state without confident leadership.
- Shell fencing has no built-in timeout and executes configured command strings through a shell, so hung scripts, quoting mistakes, environment leakage, and command injection risks are operationally significant.
- SSH fencing depends on passwordless SSH, correct target port detection, `fuser`, and `nc`; absent tools or multiple processes/listeners can make results indeterminate.
- `ObjectWritable`'s `allowCompactArrays` flag is documented as appropriate for RPC/internal or intra-cluster use, not durable inter-cluster/file output. Misuse can create incompatible persisted bytes.
- `AbstractMapWritable` has only 127 dynamic class ids per map instance. Large heterogenous maps can exhaust the contract.
- Mutable backing arrays and pooled buffers can leak stale bytes or be modified after publication if callers do not copy before retaining data.
- `ElasticByteBufferPool` explicitly has no maximum cache size, so workloads with large transient buffers can retain substantial memory.
- `MapFile.Writer.append` requires sorted nondecreasing keys. Violations can corrupt lookup semantics even if writes succeed.
- `SequenceFile.Reader.seek` only accepts positions returned by writer length APIs; arbitrary split positions must use `sync(long)`.
- Secure file open methods provide no additional owner/group checks when Hadoop security is disabled, unless forced protected test variants are used.

## Test Signals

Useful validation for this API surface should include:

- ViewFs tests for mount-table initialization, authority-specific mount tables, link resolution, list/status/open/mkdir/rename delegation, symlink behavior, ACL/xattr forwarding, delegation-token aggregation, and missing/unresolved target failures.
- HA tests for elector callback ordering, neutral mode on ZooKeeper disconnect, fatal-error notification, active transition retry after `ServiceFailedException`, health-check failures, service status reporting, request-source propagation, and concurrent callback handling.
- Fencing tests for `checkArgs`, runtime `BadFencingConfigurationException`, ordered fallback behavior, shell environment generation, shell timeout delegation to scripts, SSH argument parsing, missing `fuser`/`nc`, and no-listener success.
- PB translator tests for address/timeout construction, `cedeActive`, `gracefulFailover`, access-control exceptions, close semantics, and underlying proxy exposure.
- Static web filter tests for initializer registration through `hadoop.http.filter.initializers`, request user wrapping, filter-chain continuation, and secure-cluster web UI behavior.
- Writable round-trip and golden-byte tests for primitive writables, `BytesWritable`, `ArrayPrimitiveWritable`, `ArrayWritable`, `EnumSetWritable`, `MapWritable`, `GenericWritable`, `ObjectWritable`, `MD5Hash`, and `NullWritable`.
- Comparator tests comparing object-level and raw byte-level ordering for primitive writables, `BinaryComparable`, `BytesWritable`, `MD5Hash`, `NullWritable`, and custom `RawComparator` implementations.
- Buffer and state tests for `ByteBufferPool` direct/heap handling, `ElasticByteBufferPool` capacity selection and retention, `DataInputByteBuffer`/`DataOutputByteBuffer` position/length reporting, and mutation-after-return hazards.
- `IOUtils` tests for short reads/writes, EOF handling, skip loops, close/cleanup exception swallowing, socket close, compressed-data read wrapping, and full channel writes.
- `SecureIOUtils` tests for owner/group mismatch, symlink traversal attempts, security-enabled vs disabled behavior, force-secure test hooks, create collision, and expected file permissions.
- `MapFile`, `ArrayFile`, and `BloomMapFile` tests for sorted append enforcement, index interval persistence, corrupt index repair, closest-key lookup, dense array key behavior, Bloom false-positive/negative expectations, and sidecar file deletion/rename.
- `DefaultStringifier` tests for `Configuration` store/load, array round trips, empty-array `IndexOutOfBoundsException`, serializer/deserializer failures, and classloader/configuration behavior.
- `SequenceFile` tests for writer overload compatibility, compression type configuration, metadata round trips, raw and typed reader iteration, sync/seek semantics, split start/length options, current-value reuse, sorter factor/memory/progress controls, merge delete-input behavior, and sorted output ordering.

## Cross-Chunk Notes

The previous chunk owns the beginning of `ViewFs`, including methods that precede `access`. The next chunk should complete `SequenceFile.Sorter.merge(...)` and continue into the remaining `SequenceFile` nested APIs. The merge lane should combine adjacent chunks before publishing a final per-file report.

### subset-b-007155: lines 23752-30010

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 23752-30010

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.6.0. It starts inside `org.apache.hadoop.io.SequenceFile.Sorter`, covers the tail of the `org.apache.hadoop.io` package, then covers the complete visible `org.apache.hadoop.io.compress` package and the beginning of `org.apache.hadoop.io.file.tfile` through the early `Utils.Version` API. The XML is generated API metadata, not executable implementation, but it records public constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, synchronization flags, visibility, and deprecation notes consumed by compatibility tooling.

The visible package areas are:

- `org.apache.hadoop.io`: `SequenceFile` sorter/writer support, `SetFile`, primitive and collection `Writable` types, UTF-8 `Text`, writable serialization/comparison contracts, writable factories, and `WritableUtils`.
- `org.apache.hadoop.io.compress`: block/stream compression wrappers, codec contracts and discovery, compressor/decompressor pooling, direct decompression, native codec facades for bzip2/gzip/lz4/snappy/deflate, and splittable compression support.
- `org.apache.hadoop.io.file.tfile`: TFile exceptions, raw comparable byte ranges, TFile reader/scanner/writer APIs, TFile utility encoding/search helpers, and the start of version metadata.

## Purpose

The chunk preserves the public compatibility contract for Hadoop's binary I/O layer. The `org.apache.hadoop.io` portion documents the serialization primitives used by MapReduce keys and values, sequence-file storage, map/set files, byte-level comparators, and utility encodings. The compression package documents the common abstraction that lets higher layers choose codecs by file extension, configuration, or service discovery and then stream compressed or decompressed data through Hadoop filesystem and data-processing paths. The TFile portion documents a block-compressed key/value container with sorted-key, scanner, byte-range, record-number, metadata-block, and raw-byte access APIs.

Because this is a JDiff descriptor, its main runtime role is indirect: API compatibility checks compare this XML against other Hadoop releases. As a source-research artifact, it also gives a dense source-tree-aligned map of externally visible classes that downstream projects may compile against or load reflectively.

## Important APIs, Types, and Functions

### SequenceFile, SetFile, and writable contracts

- `SequenceFile.Sorter.RawKeyValueIterator` exposes raw sorted sequence-file iteration: `next()`, `getKey()` as `DataOutputBuffer`, `getValue()` as `SequenceFile.ValueBytes`, `getProgress()`, and `close()`.
- `SequenceFile.Sorter.SegmentDescriptor` describes merge-sort segments by file path, offset, and length. It supports sync checks, preservation policy, raw key/value reads, stored-key access, comparison/equality/hash behavior, and cleanup that closes and deletes intermediate files unless preservation is requested.
- `SequenceFile.ValueBytes` provides raw sequence-file value access through `writeUncompressedBytes`, `writeCompressedBytes`, and `getSize`.
- `SequenceFile.Writer` is a `Closeable` and `Syncable` writer for sequence-format files. Deprecated constructors remain visible, while the preferred option-based path exposes static `Writer.Option` factories for file, stream, buffer size, replication, block size, progress callback, key/value classes, metadata, compression type, and compression codec. It also exposes key/value class introspection, codec introspection, `sync`, deprecated `syncFs`, `hsync`, `hflush`, synchronized close/append/raw-append, current synchronized file length, and protected serializers for key and compressed/uncompressed values.
- `SetFile` extends `MapFile` as a file-backed set of keys. `SetFile.Reader` can seek, iterate, and fetch matching keys; `SetFile.Writer` appends strictly increasing `WritableComparable` keys and supports compression-aware constructors.
- `Writable` and `WritableComparable` define Hadoop's core serialization and comparable-key contracts. `Writable` requires `write(DataOutput)` and `readFields(DataInput)`; `WritableComparable` combines that contract with `Comparable` and documents the need for stable cross-JVM `hashCode` behavior.

### Primitive, text, and collection writables

- `ShortWritable`, `VIntWritable`, and `VLongWritable` are mutable `WritableComparable` wrappers around short, variable-length int, and variable-length long values. They expose constructors, `set`, `get`, `readFields`, `write`, equality/hash/compare, and string conversion.
- `ShortWritable.Comparator`, `Text.Comparator`, and `UTF8.Comparator` are byte-level `WritableComparator` optimizations for serialized key comparisons.
- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap` over `WritableComparable` keys and `Writable` values. It exposes sorted-map views, mutation/access methods, copy construction, and `Writable` serialization.
- `TwoDArrayWritable` serializes a two-dimensional matrix of a specified `Writable` class, with constructors, `set`, `get`, `toArray`, `readFields`, and `write`.
- `Text` stores UTF-8 bytes as a `BinaryComparable` and `WritableComparable`. It exposes constructors from string, another `Text`, or byte array; raw/copy byte access; byte length; byte-position `charAt`; UTF-8 substring search; setting/appending/clearing; stream serialization with optional maximum length; `skip`; `readWithKnownLength`; static string read/write helpers; UTF-8 encode/decode with replacement controls; UTF-8 validation; code-point extraction; `utf8Length`; and `DEFAULT_MAX_LEN`.
- `Stringifier<T>` is a closeable adapter for converting objects to and from string representations, with `IOException` on conversion failures.
- `VersionedWritable` writes and checks an implementation version byte around subclass fields; `VersionMismatchException` captures mismatched expected/current versions.

### Writable comparison, instantiation, and encoding utilities

- `WritableComparator` implements `RawComparator` and `Configurable`. It provides protected constructors for comparator subclasses, static comparator lookup/registration, object comparison, raw byte comparison, instance creation, configuration access, hash helpers, lexicographic byte comparison, and static parsers for primitive values and vint/vlong values from byte arrays.
- `WritableFactories` lets callers register a `WritableFactory` per class and create writable instances with or without `Configuration`; this supports non-public writable construction for `ObjectWritable`.
- `WritableFactory` is the single-method factory contract returning a new `Writable`.
- `WritableUtils` provides compressed byte-array/string/string-array read/write helpers, cloning via serialization, deprecated `cloneInto`, zero-compressed vint/vlong read/write, range-checked vint reading, first-byte sign/size decoding, encoded-size calculation, enum string serialization, full skipping, writable-array byte conversion, and length-bounded `readStringSafely`.

### Compression contracts and stream wrappers

- `CompressionCodec` is the central codec contract. Implementations create compression output streams and decompression input streams with or without caller-supplied `Compressor`/`Decompressor` instances, report compressor/decompressor classes, allocate new compressor/decompressor instances, and return default filename extensions.
- `CompressionInputStream` and `CompressionOutputStream` wrap input/output streams and define decompressed reads, compressed writes, reset-state behavior, current stream position, and finish/reset semantics. Mark/reset are explicitly unsupported for compression input streams in this API surface.
- `Compressor` and `Decompressor` define streaming state-machine contracts: set input and optional dictionaries, test input needs and dictionary needs, track byte counters, finish/end, compress/decompress into caller buffers, report remaining compressed input, reset, close/end, and for compressors `reinit(Configuration)`.
- `CompressorStream` and `DecompressorStream` adapt those state-machine contracts to Java streams and expose `setInputStream` for subclasses that need to swap the underlying stream.
- `BlockCompressorStream` and `BlockDecompressorStream` implement block-oriented framing over compressor/decompressor streams. Blocks contain an uncompressed length followed by one or more length-prefixed compressed data chunks; decompression can load compressed block data and reset state.

### Codec discovery, pooling, and concrete codecs

- `CodecPool` is a global reusable compressor/decompressor pool. It leases by codec, can reinitialize compressors with `Configuration`, returns instances to the pool, and reports leased compressor/decompressor counts.
- `CompressionCodecFactory` discovers codecs from the `io.compression.codecs` configuration value and Java `ServiceLoader`, stores codec classes back into configuration, resolves codecs by path extension, class name, codec name, or `Class`, removes suffixes, and exposes diagnostic extension-map and `main` helpers.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. It can use native bzip2 when available or a pure-Java implementation, but pure-Java mode does not implement compressor/decompressor object APIs. Split input streams force the pure-Java path and align reads at bzip2 block boundaries. Its default extension is `.bz2`.
- `DefaultCodec` implements the zlib/default codec path and `DirectDecompressionCodec`; `DeflateCodec` is an alias for discovery by deflate name.
- `GzipCodec` creates gzip compression/decompression streams. `GzipCodec.GzipOutputStream` bridges `DeflaterOutputStream` to Hadoop's `CompressionOutputStream` contract and exposes a protected `out` stream replacement hook.
- `Lz4Codec` and `SnappyCodec` implement `Configurable` and `CompressionCodec`; Snappy also implements `DirectDecompressionCodec`. Both expose native-code loaded/library-name checks, stream creation, compressor/decompressor allocation, and default extensions (`.lz4`, `.snappy`).
- `DirectDecompressionCodec` and `DirectDecompressor` cover ByteBuffer-based decompression. `DoNotPool` is a marker annotation for compressor/decompressor implementations that must not be pooled.
- `SplitCompressionInputStream`, `SplittableCompressionCodec`, and `SplittableCompressionCodec.READ_MODE` define split-aware compressed reads where requested start/end offsets may be adjusted to codec block boundaries. `READ_MODE` distinguishes continuous reads from blocked reads that signal end-of-block behavior.

### TFile container APIs

- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are `IOException` subclasses for named metadata-block creation and lookup failures.
- `RawComparable` describes a byte-array slice through `buffer()`, `offset()`, and `size()` so callers can compare keys without copying.
- `TFile` publishes compression names (`none`, `lzo`, `gz`), comparator names/prefixes (`memcmp`, `jclass:`), comparator construction through `makeComparator`, supported compression algorithm discovery, and a `main` information-dump entry point. Its documentation defines TFile as a typed-less byte key/value container with 64KB keys, block compression, named metadata blocks, sorted or unsorted keys, key/file-offset seeking, and configurable chunk/input/output buffer sizes.
- `TFile.Reader` wraps an `FSDataInputStream` plus known file length. It can close idempotently, report sorted state/comparator name/entry count, fetch first and last keys, return raw and entry comparators, open metadata-block streams, map file offsets to nearby record numbers or sample keys, and create scanners over full files, byte ranges, key ranges, or record-number ranges. Deprecated key-range scanner overloads remain visible beside `createScannerByKey`.
- `TFile.Reader.Scanner` is a closeable cursor over a reader range. It supports construction by record range or key range, exact seek, rewind, seek-to-end, lower/upper bound positioning, advance, end detection, current entry access, close, and current record-number lookup.
- `TFile.Reader.Scanner.Entry` models the current key/value entry. It exposes key/value length inspection, whole entry retrieval into `BytesWritable`, key/value copying to `BytesWritable`, `OutputStream`, or byte arrays, stream access for key/value data, known-value-length detection, key comparison against byte arrays or `RawComparable`, equality, and hash code.
- `TFile.Writer` wraps an `FSDataOutputStream` positioned at zero and writes block-compressed key/value entries. It supports direct byte-array append, offset/length append, streaming key append, streaming value append, and named metadata-block creation with explicit or default compression. Closing releases writer resources but intentionally does not close the underlying `FSDataOutputStream`.
- `org.apache.hadoop.io.file.tfile.Utils` provides TFile-specific variable-length integer/string encoding, decoding, and lower/upper-bound binary search helpers over lists with explicit or natural comparators.
- `Utils.Version` begins in this chunk with constructors from `DataInput` or explicit major/minor shorts, `write(DataOutput)`, major/minor accessors, and serialized size reporting.

## Control Flow

SequenceFile sorting and writing flow is staged around raw records. Sorter merge methods produce a `RawKeyValueIterator`; callers repeatedly call `next()`, then fetch a raw key and `ValueBytes`, and finally pass those records into `SequenceFile.Writer.writeFile` or append them with `appendRaw`. Segment descriptors supply per-segment raw reads and cleanup, including optional input preservation for merge intermediates. Writers are configured either through deprecated constructors or option builders, then append object or raw records, emit sync points, flush/sync the filesystem stream, report synchronized positions, and close.

Writable flow is serializer-driven. Callers write fields to `DataOutput` and reconstruct into existing instances with `readFields(DataInput)`. Comparators may instantiate writable objects and compare natural order, or bypass object creation by comparing serialized byte ranges. `WritableUtils`, `WritableComparator`, `Text`, and the variable-length writable classes provide the shared wire encodings that make these contracts compact and comparable in MapReduce shuffle, sequence files, map files, and RPC/storage paths.

Compression flow is codec-mediated. A caller resolves a `CompressionCodec` directly, through `CompressionCodecFactory`, or by path extension; leases or creates compressor/decompressor instances through the codec or `CodecPool`; wraps the underlying stream in a compression input/output stream; feeds data through compressor/decompressor state transitions; finishes or resets as needed; and returns reusable codec state to the pool. Block streams add a framing layer around stream compressors. Splittable codecs adjust requested compressed offsets and expose adjusted ranges so parallel readers can start at viable block boundaries.

TFile write flow starts with a zero-position `FSDataOutputStream`, minimum block size, compression name, optional comparator name, and configuration. Callers append full byte-array entries or open a key stream followed by a value stream. Once metadata blocks are created, no more key/value insertion is allowed. Closing finalizes container state and internal resources while leaving the filesystem stream open for the caller. TFile read flow opens with a known file length, loads index metadata, then creates scanners by full range, byte range, key range, or record-number range. A scanner positions with seeks/bounds, yields entries, advances, and closes. Entry methods then copy or stream the current key/value data.

## State and Persistence Behavior

This chunk is API metadata, but the described APIs imply several persistent wire formats. `Writable`, `Text`, `VIntWritable`, `VLongWritable`, `WritableUtils`, `VersionedWritable`, `SequenceFile.Writer`, `SetFile`, and TFile all define serialized forms that must remain readable across releases. The public JDiff signatures are therefore compatibility-sensitive even when implementation details are not present in the XML.

`SequenceFile.Writer` persists key/value class names, optional metadata, compression mode/codec, sync markers, and serialized records to a filesystem path or `FSDataOutputStream`. Its protected serializers show that object writes pass through Hadoop serializer implementations, while raw append preserves already serialized key/value bytes. `getLength()` returns a safe synchronized position, not necessarily the exact last appended key under block compression.

`SetFile` persists sorted keys as a `MapFile` variant and requires strictly increasing appended keys. Reader state is cursor-like and stream-backed.

Writable objects hold in-memory mutable primitive, text, array, or map state and serialize through `DataInput`/`DataOutput`. `Text.clear()` resets logical length without clearing the underlying byte array, so retained buffer capacity can persist in memory after logical clearing. `SortedMapWritable` persists class metadata inherited from `AbstractMapWritable` plus sorted key/value entries. `WritableFactories` and `WritableComparator` maintain process-global factory/comparator registries.

Compression state is mostly stream-local or pool-global. Compressors and decompressors carry mutable native or Java codec state until `reset`, `reinit`, `finish`, `end`, or `close`. `CodecPool` tracks leased and returned instances globally and must not pool implementations annotated with `DoNotPool`. `CompressionCodecFactory` stores configured codec class names in `Configuration` and uses extension maps for lookup.

TFile persists a block-compressed key/value container with data-block indexes, meta-block indexes, comparator metadata, version metadata, compression names, chunked values, and optional named metadata blocks. Reader/scanner/entry objects are stateful cursors over a shared `FSDataInputStream`; the TFile documentation notes that multiple scanners over the same reader serialize actual I/O because the implementation relies on `seek()+read()`. Writer exceptions during append can leave the TFile inconsistent; the documented only legitimate next call is `close()`.

## Dependencies and Integration Points

- The `org.apache.hadoop.io` APIs depend on `java.io` streams, `DataInput`, `DataOutput`, `Closeable`, Java collections, `java.nio.ByteBuffer`, `java.nio.charset` exceptions, Hadoop `Configuration`/`Configurable`, filesystem types (`FileSystem`, `Path`, `FSDataOutputStream`, `Syncable`), `Progressable`, and serializer classes.
- SequenceFile and SetFile integrate with Hadoop storage abstractions, compression codecs, progress reporting, raw comparators, and writable key/value types used by MapReduce and filesystem-backed data structures.
- `Text`, `WritableUtils`, and `WritableComparator` are cross-cutting dependencies for serialization, RPC, shuffle/sort, configuration string handling, token/service text fields, and compatibility-sensitive binary encodings.
- Compression APIs integrate with `Configuration`, `Path`, Java `ServiceLoader`, native compression libraries, Java deflater streams, direct `ByteBuffer` decompression, Hadoop split processing, and filesystem input/output streams.
- Concrete codecs are integration points for optional native libraries. BZip2 additionally integrates with pure-Java fallback behavior and split-aware processing; Snappy and LZ4 expose native availability checks.
- TFile integrates with `FSDataInputStream`, `FSDataOutputStream`, `Configuration`, `BytesWritable`, `RawComparator`, `WritableComparator`, `JavaSerializationComparator`, compression algorithms, byte-range scanning, record-number indexing, and named metadata blocks.

## Risks and Edge Cases

- The chunk starts in the middle of `SequenceFile.Sorter` and ends in the middle of `Utils.Version`. Merge tooling must combine adjacent chunks before making final per-file claims about complete class surfaces.
- Many APIs describe persistent binary formats. Changes to `WritableUtils` vint/vlong sign handling, byte order, size calculation, `Text` UTF-8 length encoding, `VersionedWritable` version checks, SequenceFile framing, or TFile encodings can corrupt stored data or break old clients.
- `SequenceFile.Writer` has deprecated constructors and deprecated `syncFs`, but they remain public compatibility obligations in Hadoop 2.6.0. Downstream code may still compile against them.
- Raw append and raw iterator APIs assume key/value bytes match declared classes and compression state. Incorrect lengths, offsets, or `ValueBytes` compressed/uncompressed handling can produce unreadable SequenceFiles.
- `SetFile.Writer.append` requires strictly increasing keys. Violating comparator order can create files that later readers search incorrectly.
- `Text.getBytes()` exposes an oversized backing array where only `getLength()` bytes are valid; callers that persist or compare the full array risk data leakage or incorrect comparisons. `clear()` also intentionally retains allocated memory.
- `WritableComparable.hashCode()` must be stable across JVMs for partitioning. Implementations with identity-based or randomized hashes can break MapReduce partitioning.
- Global registries in `WritableFactories`, `WritableComparator`, `CodecPool`, and codec discovery can make tests order-dependent if they do not isolate configuration and registered classes.
- Codec pooling is sensitive to lifecycle. Returning closed, unreinitialized, or `DoNotPool` compressor/decompressor instances can cause native crashes, data corruption, or subtle cross-stream contamination.
- Native-code codec availability is environmental. BZip2, LZ4, and Snappy behavior may vary between native and pure-Java/unavailable modes; split bzip2 intentionally uses pure-Java behavior regardless of the configured native preference.
- Compression input mark/reset are unsupported; callers expecting normal `InputStream` mark semantics will fail.
- Splittable compression offsets may be adjusted by the codec. Callers must use `getAdjustedStart()` and `getAdjustedEnd()` rather than assuming requested split boundaries.
- TFile keys are limited to 64KB while values are chunked and practically disk-limited. Unknown value lengths, chunk-size configuration, and stream-based append close ordering are important edge cases.
- TFile writer state becomes inconsistent after append I/O exceptions, and metadata-block creation forbids further key/value insertion. Recovery paths should close and discard rather than continue writing.
- TFile scanner I/O is not truly multi-threaded over one reader because shared `FSDataInputStream` seeking serializes concurrent access.

## Test Signals

- API compatibility tests should verify every public class, interface, constructor, method, field, checked exception, implemented interface, deprecation flag, synchronization flag, and visibility marker in this chunk against the intended Hadoop Common 2.6.0 baseline.
- Writable tests should round-trip `ShortWritable`, `VIntWritable`, `VLongWritable`, `TwoDArrayWritable`, `SortedMapWritable`, `VersionedWritable` subclasses, and `Text` through `DataInput`/`DataOutput`, including equality/hash/compare behavior.
- Encoding tests should cover positive and negative vint/vlong boundaries, byte-array and stream decoders, `readVIntInRange`, enum serialization, compressed string/byte-array helpers, `skipFully`, `readStringSafely`, and `Text` maximum-length enforcement.
- UTF-8 tests should cover valid and malformed byte sequences, replacement versus exception decode behavior, byte-position `charAt`, `find` without string conversion, code-point extraction, `utf8Length`, `copyBytes` versus `getBytes`, and `clear()` buffer retention.
- Comparator tests should compare object-level and raw byte-level ordering for writable primitives and `Text`, verify registered comparator lookup, and exercise byte parsers for int/long/float/double/vint/vlong.
- SequenceFile tests should write and read object and raw key/value records under no, record, and block compression; verify sync/hsync/hflush behavior; check `getLength()` as a seekable synchronized position; test sorter merge flows and segment cleanup/preserve behavior.
- SetFile tests should enforce sorted append order, seek existing and missing keys, iterate to EOF, and validate comparator-aware reader/writer constructors.
- Compression tests should verify codec factory lookup by extension/name/class/configuration and service-loaded codecs, suffix removal, codec class configuration, stream compression/decompression round trips, finish/reset behavior, mark/reset unsupported behavior, and `CompressionInputStream.getPos()`.
- CodecPool tests should cover lease/return counts, compressor reinitialization with configuration, decompressor reuse, null handling, and non-pooling behavior for `DoNotPool` implementations.
- Native codec tests should branch on environment for bzip2/lz4/snappy availability, library-name reporting, direct decompressor creation, and pure-Java bzip2 split reading.
- Splittable compression tests should verify adjusted split boundaries, continuous versus blocked read modes, and parallel split consumption for bzip2-like block codecs.
- TFile tests should write/read sorted and unsorted files with `none`, `lzo`, and `gz` where available; verify comparator construction (`memcmp` and `jclass:`); scan by full file, byte range, key range, and record-number range; exercise lower/upper bound and seek-to-end behavior; read keys/values through byte arrays, `BytesWritable`, and streams; and check known versus unknown value lengths.
- TFile metadata tests should create, duplicate, read, and miss named meta blocks, verify `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist`, and confirm no key/value appends are accepted after meta-block creation.
- TFile durability tests should validate close idempotence, underlying `FSDataOutputStream` ownership, file-length constructor requirements, version serialization, and behavior after append I/O exceptions.

### subset-b-007156: lines 30011-36346

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 30011-36346

## Scope

This chunk is part of the JDiff XML API snapshot for Apache Hadoop Common 2.6.0. It starts at the tail of `org.apache.hadoop.io.file.tfile.Utils.Version`, then covers public API declarations for serialization, Avro serialization adapters, protobuf IPC refresh translators, JMX JSON exposure, Log4J helpers, the legacy `org.apache.hadoop.metrics` SPI and sinks, the newer `org.apache.hadoop.metrics2` API and sinks, network topology/socket helpers, Unix domain socket watcher handlers, and the beginning of the deprecated `org.apache.hadoop.record` package.

The source is API metadata rather than executable implementation. It records class/interface names, inheritance, implemented interfaces, constructors, methods, fields, visibility, synchronization flags, deprecation text, exceptions, parameter types, and selected Javadoc. It is used to compare Hadoop public API compatibility across releases.

## Purpose

The chunk preserves the Hadoop Common 2.6.0 public contract for several cross-cutting subsystems:

- Object serialization choices used by Hadoop's `Serialization`, `Serializer`, and `Deserializer` framework.
- Refresh RPC protocols that let clients invoke administrative refresh operations through protobuf translators.
- Operational observability surfaces: JMX JSON, JSON log formatting, log event counters, legacy metrics contexts, metrics2 sources/sinks, MBeans, and external sink adapters.
- Network topology resolution and socket factory extension points used by HDFS/YARN placement, RPC, and client networking.
- Deprecated record I/O APIs retained for compatibility while pointing callers toward Avro.

Because this is a generated compatibility file, its behavioral value is in defining what downstream code could compile against in Hadoop Common 2.6.0. Missing or changed signatures here would be detected by JDiff as API drift.

## Important APIs and Types

### TFile Version Tail

The first lines complete `org.apache.hadoop.io.file.tfile.Utils.Version`. The visible methods are `toString()`, `compatibleWith(Utils.Version)`, `compareTo(Utils.Version)`, `equals(Object)`, and `hashCode()`. The Javadoc describes a major/minor version model where major-version changes indicate incompatible storage format changes and minor-version changes indicate compatible evolution. `compatibleWith` tests same-major-version compatibility.

### `org.apache.hadoop.io.serializer`

`JavaSerialization` implements `Serialization` for Java `Serializable` classes and exposes the standard `accept(Class)`, `getDeserializer(Class)`, and `getSerializer(Class)` hooks. `JavaSerializationComparator<T>` extends `DeserializerComparator` and compares deserialized objects through `Comparable`, so its constructor can throw `IOException` and its `compare(T, T)` is the public comparison path. `WritableSerialization` extends `Configured` and adapts Hadoop `Writable` objects by delegating persistence to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`.

The package documentation ties these implementations to the `io.serializations` configuration property. Integration code discovers a configured ordered list of `Serialization` implementations, asks `accept(Class)`, then obtains a serializer or deserializer for the matched class.

### `org.apache.hadoop.io.serializer.avro`

`AvroSerialization<T>` is the abstract `Configured` base class for Avro-backed Hadoop serialization. It implements `Serialization` and supplies public `getSerializer(Class)` and `getDeserializer(Class)` while requiring subclasses to provide `getSchema(T)`, `getWriter(Class)`, and `getReader(Class)`. It exposes `AVRO_SCHEMA_KEY`.

`AvroSpecificSerialization` targets Avro `SpecificRecord` classes generated by Avro's specific compiler. It implements `accept(Class)`, `getSchema(SpecificRecord)`, and class-based reader/writer factories.

`AvroReflectSerialization` targets reflected Java classes. It accepts classes either implementing the marker interface `AvroReflectSerializable` or living under packages configured by `AVRO_REFLECT_PACKAGES` / `avro.reflect.pkgs`. Its `accept(Class)` is synchronized, which is a visible concurrency signal for cached package or reflection state.

### `org.apache.hadoop.ipc.protocolPB`

The chunk includes protobuf-side translators for two administrative protocols:

- `GenericRefreshProtocolClientSideTranslatorPB` implements `ProtocolMetaInterface`, `GenericRefreshProtocol`, and `Closeable`. It wraps `GenericRefreshProtocolPB`, exposes `refresh(String, String[])`, `isMethodSupported(String)`, and `close()`, and translates checked failures as `IOException`.
- `GenericRefreshProtocolServerSideTranslatorPB` implements `GenericRefreshProtocolPB` and adapts `refresh(RpcController, GenericRefreshRequestProto)` to a server-side `GenericRefreshProtocol`, returning `GenericRefreshResponseCollectionProto` or throwing protobuf `ServiceException`.
- `RefreshCallQueueProtocolClientSideTranslatorPB` and `RefreshCallQueueProtocolServerSideTranslatorPB` provide the same client/server bridge pattern for `refreshCallQueue()`.

These classes are integration glue between Hadoop's Java protocol interfaces, protobuf RPC stubs, and protocol capability probing.

### JMX and Logging

`JMXJsonServlet` extends `HttpServlet`. It initializes an `MBeanServer`, gates access through protected `isInstrumentationAccessAllowed(HttpServletRequest, HttpServletResponse)`, and implements `doGet`. The Javadoc defines `/jmx` JSON output, optional `qry`, `get`, and `callback` parameters, HTTP 400/404 failure behavior, conversion of primitive, array, `CompositeData`, and `TabularData` attributes, and JSONP support.

`org.apache.hadoop.log.EventCounter` is a deprecated compatibility subclass of `org.apache.hadoop.log.metrics.EventCounter`. The replacement appender counts fatal, error, warn, and info events and provides static getters plus `append`, `close`, and `requiresLayout`.

`Log4Json` extends Log4J `Layout`. It exposes `format(LoggingEvent)`, JSON conversion overloads for full `LoggingEvent` and explicit fields, `parse(String)` for tests, `getContentType()`, `ignoresThrowable()`, and `activateOptions()`. Its public field names (`DATE`, `EXCEPTION_CLASS`, `LEVEL`, `MESSAGE`, `NAME`, `STACK`, `THREAD`, `TIME`, `JSON_TYPE`) are the emitted JSON keys.

`LogLevel` exposes a command-line `main(String[])` and usage text for runtime log-level adjustment.

### Legacy `org.apache.hadoop.metrics`

The legacy metrics packages define a pull/update/emit model:

- `FileContext` emits legacy metrics records to a file. It supports `init`, `startMonitoring`, `stopMonitoring`, `emitRecord`, `flush`, and exposes `FILE_NAME_PROPERTY` and `PERIOD_PROPERTY`.
- `GangliaContext` sends legacy metrics over UDP in Ganglia XDR format. It maintains a byte buffer, offset, configured metrics servers, and `DatagramSocket`; it exposes initialization, close, record/metric emission, Ganglia metadata lookups (`getUnits`, `getSlope`, `getTmax`, `getDmax`), and XDR writers. `GangliaContext31` specializes emission for Ganglia 3.1.
- `AbstractMetricsContext` is the primary SPI base. It stores context name/factory, parses attributes, starts/stops synchronized monitoring, registers `Updater` callbacks, creates records, returns buffered records, emits and flushes records, and maintains internal record state through `update(MetricsRecordImpl)` and `remove(MetricsRecordImpl)`.
- `CompositeContext` fans legacy metrics operations out to multiple subcontexts.
- `MetricsRecordImpl` is the mutable record facade with overloaded `setTag`, `removeTag`, `setMetric`, `incrMetric`, `update`, and `remove`. It delegates persistence of buffered rows back to its `AbstractMetricsContext`.
- `MetricValue` carries a `Number` plus absolute/increment mode using public `ABSOLUTE` and `INCREMENT` constants.
- `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` provide no-op or sample-only contexts for disabled metrics and JMX-style pull monitoring.
- `OutputRecord` exposes immutable-ish snapshots of tags and metrics for sink implementations.
- `Util.parse(String, int)` parses comma/space-separated server specifications.

### `org.apache.hadoop.metrics2`

The metrics2 API is a newer, source/sink oriented contract:

- `AbstractMetric` implements `MetricsInfo` and requires `value()`, `type()`, and `visit(MetricsVisitor)` while providing name, description, equality, hash, and string behavior through its metadata.
- `MetricsCollector` creates `MetricsRecordBuilder` instances by name or `MetricsInfo`.
- `MetricsRecordBuilder` provides a fluent API to tag records, add existing metrics, set context, add counters and gauges across numeric types, return the parent collector, and end a record.
- `MetricsSink`, `MetricsSource`, and `MetricsPlugin` define sink flushing, source snapshotting, and plugin initialization against `SubsetConfiguration`.
- `MetricsSystem` is the lifecycle and registry interface. It initializes by prefix, registers/unregisters sources and sinks, exposes registered sources, publishes metrics immediately on a best-effort basis, registers callbacks, and shuts down. Its nested `Callback` and `AbstractCallback` define pre/post start/stop hooks, and `MetricsSystemMXBean` exposes start/stop/MBean lifecycle and current configuration through JMX.
- `MetricsTag`, `MetricsInfo`, `MetricsVisitor`, `MetricType`, and `MetricsException` define metadata, visitor dispatch, metric typing, and error reporting.

The annotations package contains `@Metric`, `@Metrics`, and `Metric.Type` enum metadata for annotation-driven source registration. The filter package exposes `GlobFilter` and `RegexFilter`, both compiling string patterns for metrics inclusion/exclusion.

### `org.apache.hadoop.metrics2.lib`

`DefaultMetricsSystem` is a singleton-style enum with static `initialize`, `instance`, `shutdown`, `setInstance`, mini-cluster mode, MBean naming, and duplicate-safe source naming helpers.

`Interns` creates interned `MetricsInfo` and `MetricsTag` instances. `MetricsRegistry` owns a record/group identity, a synchronized metric/tag map, factory methods for counters, gauges, quantiles, stats, and rates, tag/context mutation, `add(String, long)`, and `snapshot(MetricsRecordBuilder, boolean)`.

Mutable metric classes model stateful source-side metrics:

- `MutableMetric` tracks changed state and controls snapshot behavior.
- `MutableCounter`, `MutableCounterInt`, and `MutableCounterLong` expose monotonic increment and value snapshots.
- `MutableGauge`, `MutableGaugeInt`, and `MutableGaugeLong` expose increment, decrement, set, value, and snapshot behavior.
- `MutableStat` tracks sampled statistics, optional extended stats, min/max reset, and snapshot output.
- `MutableRate` specializes `MutableStat` for throughput/rate measurement.
- `MutableRates` initializes a set of method-rate metrics from a protocol class, accepts named rate samples, and snapshots the group.
- `MutableQuantiles` keeps online quantile estimates over a rolling interval and exposes `quantiles`, `previousSnapshot`, `add(long)`, `snapshot`, and `getInterval()`.

### Metrics2 Sinks and Utilities

`FileSink` and `GraphiteSink` implement configured sink lifecycle with `init`, `putMetrics`, `flush`, and `close`. `GraphiteSink` integrates with a Graphite server, while `FileSink` writes records to a configured file-like target.

`AbstractGangliaSink` is the metrics2 base for Ganglia sinks. It carries defaults for units, `tmax`, `dmax`, slope, default port, server property names, sparse-metrics support, a buffer size, and a `GangliaMetricVisitor`. It initializes from `SubsetConfiguration`, looks up `GangliaConf`, encodes XDR strings/ints, emits to configured hosts, and exposes sparse-metric support. `GangliaSink30` builds Ganglia 3.0 records and `GangliaSink31` overrides emission for Ganglia 3.1. The Javadoc explicitly notes that the sink implementation assumes the metrics system handles thread safety.

`MBeans` registers and unregisters JMX beans using Hadoop's `hadoop:service=<serviceName>,name=<nameName>` convention. `MetricsCache` stores full records for sinks that cannot consume sparse updates; its nested `Record` exposes tag and metric lookup plus entry sets, with `metrics()` deprecated in favor of `metricsEntrySet()`. `SampleStat.MinMax` tracks running minimum and maximum. `Servers.parse(String, int)` parses server specifications.

### Network and Unix Socket APIs

`DNSToSwitchMapping` is the pluggable host/IP to rack path resolver. Implementations must preserve one-to-one input/output ordering and expose cache reload for all or selected nodes. `AbstractDNSToSwitchMapping` stores configuration, exposes topology diagnostics (`getSwitchMap`, `dumpTopology`), and provides single-switch policy predicates used by block placement and other topology-sensitive code.

`CachedDNSToSwitchMapping` wraps a raw mapping, caches resolved host-to-rack results, exposes cache snapshots, delegates single-switch decisions, and supports cache reload. `ScriptBasedMapping` is the configured cached wrapper for script-based topology resolution, while protected nested `RawScriptBasedMapping` reads configuration, executes the mapping script, resolves batches, and exposes no-op cache reload methods.

`TableMapping` is another cached mapping implementation based on a table file. `ConnectTimeoutException` is the `SocketTimeoutException` subtype thrown by `NetUtils.connect` on connect timeout. `SocksSocketFactory` and `StandardSocketFactory` implement `SocketFactory` variants with standard Java socket overloads; the SOCKS version is also `Configurable` and can be constructed with a `Proxy`.

`DomainSocketWatcher.Handler` is a Unix-domain-socket callback interface whose `handle(DomainSocket)` returns whether the watcher should continue tracking the socket after readability/closure events.

### Deprecated `org.apache.hadoop.record`

The final part of the chunk begins the old Hadoop record I/O package, marked deprecated in favor of Avro:

- `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput` and `RecordOutput` over `InputStream`/`DataInput` and `OutputStream`/`DataOutput`. They provide thread-local `get(...)` helpers, primitive/string/buffer read and write methods, and record/vector/map boundaries.
- `Buffer` is a mutable byte sequence with backing-array management (`set`, `copy`, `get`, `getCount`, `getCapacity`, `setCapacity`, `reset`, `truncate`, `append`), comparison/equality/hash, charset conversion, and cloning.
- `CsvRecordInput` and `CsvRecordOutput` implement the same record I/O contract in CSV form.
- `Index` is the iterator-like helper returned while deserializing vectors and maps.
- The range ends just after the start of abstract `Record`, which implements `WritableComparable` and `Cloneable`; the rest of its API continues in the next chunk.

## Control Flow

The XML has no runtime control flow. It describes runtime control flow shapes visible through public APIs:

- Serialization dispatch is configuration-driven: configured `Serialization` classes are tested with `accept(Class)`, then serializer/deserializer objects perform actual I/O.
- Avro serialization funnels concrete subclasses through `AvroSerialization` serializer/deserializer factories, then delegates schema, reader, and writer creation to specific or reflected implementations.
- IPC refresh calls flow from Java client translator methods to protobuf protocol stubs, across RPC, through server-side translators, and finally into implementation interfaces.
- Legacy metrics flow from mutable `MetricsRecordImpl` objects into an `AbstractMetricsContext` buffer through `update()`/`remove()`, then periodic monitoring invokes updaters, emits `OutputRecord`s to concrete contexts, and flushes.
- Metrics2 flows from registered `MetricsSource` snapshots into `MetricsCollector`/`MetricsRecordBuilder`, then into configured `MetricsSink.putMetrics()` and `flush()`.
- Network topology resolution flows through cached wrappers before reaching raw script or table resolvers; reload methods invalidate cached state.
- Record I/O readers and writers advance through explicit start/end calls for records, vectors, and maps, using `Index` to loop through collection elements.

## State and Persistence Behavior

The JDiff document itself is static generated metadata, but the represented APIs expose several kinds of state:

- Serialization classes are mostly stateless factories, except for `Configured` state and Avro reflect package/configuration caches.
- IPC translators hold protobuf proxy references and must be closed on the client side.
- `JMXJsonServlet` keeps a transient `MBeanServer` reference and exposes live process/JVM/Hadoop service state as JSON.
- Log counters accumulate in-process event counts by level; `Log4Json` formats transient log events.
- Legacy metrics contexts buffer records, tags, metrics, updaters, context configuration, monitoring-period state, output files, UDP sockets, and Ganglia encoding buffers.
- Metrics2 registries and mutable metrics retain counters, gauges, statistical accumulators, quantile snapshots, changed flags, tags, and singleton metrics-system state.
- Metrics sinks may persist or transmit records to files, Graphite, Ganglia UDP endpoints, and JMX MBeans.
- Network topology mappers cache host-to-rack mappings and read configuration-driven script/table state.
- `Buffer` persists mutable byte contents and capacity/count separately; record input/output classes persist stream position and collection traversal state.

## Dependencies and Integration Points

The covered APIs depend on Java serialization, Hadoop `Writable`, Avro reflect/specific APIs, protobuf RPC, servlet APIs, JMX, Log4J, Jackson, Apache Commons Logging and Configuration, Java networking, and Hadoop configuration/RPC/metrics abstractions.

Important integration points in the Hadoop source tree include:

- `io.serializations` and Avro-related configuration in jobs and daemons.
- NameNode/DataNode/ResourceManager administrative refresh commands using `GenericRefreshProtocol` and `RefreshCallQueueProtocol`.
- Hadoop HTTP servers that mount `JMXJsonServlet` under `/jmx`.
- Log4J configurations that select `Log4Json` or event counters.
- Legacy metrics configurations using file or Ganglia contexts, plus metrics2 configurations that register file, Graphite, Ganglia, JMX, and custom sinks.
- HDFS block placement, YARN locality, and diagnostics relying on `DNSToSwitchMapping` and cached/script/table mappers.
- RPC and client code using `StandardSocketFactory`, `SocksSocketFactory`, and `ConnectTimeoutException`.
- Short-circuit local I/O and native domain socket watchers using `DomainSocketWatcher.Handler`.
- Compatibility paths for older generated record classes still implementing `org.apache.hadoop.record.Record`.

## Risks

- This is a compatibility artifact. Removing, renaming, changing visibility, changing checked exceptions, or changing inheritance/interfaces in these entries can break downstream applications even when implementation behavior is unchanged.
- The serialization APIs are class-dispatch sensitive. An overly broad `accept(Class)` can select the wrong serialization framework; an overly narrow one can fail jobs at runtime.
- Java serialization is experimental and has object-compatibility and security risks; callers should prefer Hadoop Writable or Avro where possible.
- Avro reflect acceptance through configured package names can accidentally serialize classes not intended for wire/storage compatibility.
- IPC translators must preserve protobuf/Java exception mapping and protocol method support checks; drift can break administrative refresh commands during rolling upgrades.
- JMX JSON and JSONP expose operational state. Access checks in `isInstrumentationAccessAllowed` are security-relevant, and JSON field formatting is consumed by monitoring tools.
- Legacy metrics and metrics2 coexist. Misconfiguration can silently select no-op contexts, omit metrics, duplicate MBean/source names, or generate sparse updates unsupported by a sink.
- Metrics mutable classes use changed flags and synchronization selectively. Consumers must snapshot correctly or they can miss updates, double-publish, or expose inconsistent values.
- Ganglia sinks use low-level UDP/XDR encoding and assume thread-safety is handled externally. Bad buffer handling or concurrent calls can corrupt emitted metrics.
- Network topology mapping affects rack-aware placement and scheduling. Cache invalidation, script failures, table reloads, and incorrect single-switch detection can reduce fault tolerance or locality.
- Script-based mapping executes configured commands; argument limits, working directory, failure handling, and configuration hygiene are operational risks.
- Deprecated record APIs remain public for compatibility but should not be expanded for new storage formats; their stream and buffer semantics can produce interoperability bugs if mixed with Avro expectations.
- The chunk starts and ends mid-family, so `Utils.Version` and `Record` are incomplete here and must be reconciled with adjacent chunks for whole-class reporting.

## Test and Validation Signals

Useful validation for this API slice includes:

- JDiff or equivalent API-compatibility checks against adjacent Hadoop Common releases, especially for public signatures, exceptions, deprecation markers, and inheritance.
- Unit tests for `SerializationFactory` selection over Writable, Java Serializable, Avro specific, and Avro reflect classes with configured `io.serializations` and reflect package lists.
- IPC translator tests that verify protobuf request/response conversion, `isMethodSupported`, checked exception translation, and close behavior.
- HTTP tests for `/jmx` covering `qry`, `get`, invalid parameter handling, missing bean/attribute handling, JSONP callback, and instrumentation access denial.
- Log formatter tests that parse `Log4Json` output, including throwable stack arrays, escaped messages, timestamps, and public key names.
- Legacy metrics tests for context start/stop, updater registration, record update/remove semantics, file flushing, Ganglia server parsing, and no-op contexts.
- Metrics2 tests for source/sink registration, duplicate names, lifecycle callbacks, immediate publish, mutable counter/gauge/stat/rate/quantile snapshots, changed-flag behavior, metrics cache sparse/full update behavior, and MBean registration.
- Sink integration tests for file, Graphite, and Ganglia 3.0/3.1 output formatting and flush/close behavior.
- Network topology tests for one-to-one resolution, default rack fallback, cache hits, targeted/all reload, script/table configuration reload, dump diagnostics, and single-switch predicates.
- Socket factory tests for proxy configuration, equality/hash behavior, and all `createSocket` overloads.
- Deprecated record I/O round-trip tests for binary and CSV primitive/string/buffer data, vector/map iteration through `Index`, `Buffer` capacity/count mutations, charset conversion, comparison, and clone behavior.

### subset-b-007157: lines 36347-42401

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 36347-42401

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.6.0. It is generated XML metadata, not implementation source, but it records the externally visible Java API surface: packages, classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, visibility, synchronization/finality flags, and Javadoc-derived contracts. The range starts inside the deprecated `org.apache.hadoop.record.Record` declaration and ends after `org.apache.hadoop.service.LifecycleEvent`, so adjacent chunks are needed for whole-file reconciliation.

The visible source areas are:

- `org.apache.hadoop.record`: the tail of `Record`, plus `RecordComparator`, `RecordInput`, `RecordOutput`, `Utils`, `XmlRecordInput`, `XmlRecordOutput`, and a long package-level description of the deprecated Hadoop Record I/O DDL, generated code, and binary/CSV/XML encodings.
- `org.apache.hadoop.record.compiler`, `.ant`, `.generated`, and `.meta`: deprecated record compiler model types, Ant task integration, JavaCC parser infrastructure, and runtime schema metadata.
- `org.apache.hadoop.security`: annotation-derived protocol security metadata, HTTP auth filter initialization, group/id mapping contracts, JNI fallback group mappers, provider URI helpers, SASL helpers, shell id mapping, UGI authentication-method enum metadata, and whitelist-based SASL property resolution.
- `org.apache.hadoop.security.alias`: credential-provider abstraction, nested credential entry, factory, command-line shell, password reader, and provider factories.
- `org.apache.hadoop.security.protocolPB`: protobuf client/server translators for refresh authorization-policy and user/group mapping protocols.
- `org.apache.hadoop.security.ssl`: hostname verifier helpers and a Jetty SSL connector subclass that disables SSLv3.
- `org.apache.hadoop.security.token.delegation.web`: delegation-token-aware HTTP authenticated URL classes and authenticators.
- `org.apache.hadoop.service`: the beginning of Hadoop's service lifecycle framework through `LifecycleEvent`.

## Purpose

The XML preserves Hadoop Common 2.6.0's public API contract for compatibility comparison. The record packages document a deprecated serialization and record compiler stack retained after replacement by Avro. The security packages expose contracts used by RPC, HTTP, SASL, credential storage, identity/group resolution, delegation-token web clients, and admin refresh protocols. The service package exposes a reusable lifecycle state machine used by Hadoop daemons and subsystems.

Because this is a JDiff dump, the research value is the API and behavior promised by signatures and documentation rather than executable method bodies. Compatibility tooling should treat the signatures, checked exceptions, deprecation markers, and documented side effects as the stable surface.

## Important APIs, Types, and Functions

### Deprecated Record I/O Runtime

- `org.apache.hadoop.record.Record` is an abstract base for generated record classes. It implements `WritableComparable` and `Cloneable`, requires tagged `serialize(RecordOutput, String)`, tagged `deserialize(RecordInput, String)`, and `compareTo(Object)`, and also exposes untagged `serialize(RecordOutput)`, `deserialize(RecordInput)`, `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.
- `RecordComparator` extends `WritableComparator` for raw record comparison. It has a protected constructor taking a record `Class`, an abstract byte-array `compare(...)`, and a synchronized static `define(Class, RecordComparator)` registration hook.
- `RecordInput` defines deserializer operations for primitive values, strings, `Buffer`, record boundaries, vector boundaries, and map boundaries. Composite starts return `Index` so callers can iterate serialized vector/map elements.
- `RecordOutput` defines the matching serializer operations: primitive writes, `writeString`, `writeBuffer`, record start/end, vector start/end over `ArrayList`, and map start/end over `TreeMap`.
- `org.apache.hadoop.record.Utils` exposes low-level serialization helpers: byte-array and `DataInput` variants of `readVLong`/`readVInt`, `readFloat`, `readDouble`, `getVIntSize`, `writeVLong`, `writeVInt`, `compareBytes`, and a public `hexchars` table.
- `XmlRecordInput` implements `RecordInput` over an `InputStream`; `XmlRecordOutput` implements `RecordOutput` over an `OutputStream`. Both mirror the full primitive and composite record I/O contract for XML serialization.
- The package documentation describes record DDL includes, modules, classes, target-language generation for C++ and Java, field accessor generation, primitive/composite type mappings, and binary/CSV/XML data encodings. It states that the whole package is deprecated in favor of Avro.

### Deprecated Record Compiler

- `CodeBuffer` wraps a string buffer with indentation-aware `toString()`.
- `Consts` publishes compiler constants such as `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract base for Hadoop record compiler type descriptors. Visible subclasses cover primitive and composite DDL types: `JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JBuffer`, `JString`, `JVector`, `JMap`, and `JRecord`.
- `JField` wraps a record field name and type. `JFile` represents a parsed record-definition file with included files and record declarations, and exposes `genCode(language, destDir, options)`.
- `RccTask` extends Ant `Task` and invokes the record compiler from builds. It accepts language, file, fail-on-error, destination directory, and nested filesets before `execute()`.
- `ParseException`, `Rcc`, `RccConstants`, `RccTokenManager`, `SimpleCharStream`, `Token`, and `TokenMgrError` are JavaCC-generated parser components for record DDL. `Rcc` exposes parser entry points for includes, modules, records, fields, maps, vectors, token access, parser reinitialization, tracing, and command-line driver/main flow.

### Record Metadata

- `FieldTypeInfo` pairs a field id with a `TypeID` and defines equality/hash behavior.
- `TypeID` models primitive record type ids and publishes shared constants for bool, buffer, byte, double, float, int, long, and string types; nested `TypeID.RIOType` defines byte constants for primitive and composite kinds.
- `MapTypeID`, `VectorTypeID`, and `StructTypeID` extend `TypeID` to represent map key/value types, vector element types, and struct field metadata.
- `RecordTypeInfo` extends `Record` and serializes/deserializes schema metadata. It tracks a record name, supports adding fields, exposes field type info collections, can return one-level nested struct metadata, and has a comparison method documented as not intended for meaningful ordering.
- `org.apache.hadoop.record.meta.Utils.skip(RecordInput, String, TypeID)` skips encoded data based on runtime type metadata.

### Security and Identity

- `AnnotatedSecurityInfo` extends `SecurityInfo` and reads `KerberosInfo` and `TokenInfo` annotations from protocol interfaces.
- `AuthenticationFilterInitializer` extends `FilterInitializer` and propagates `hadoop.http.authentication.*` configuration into the hadoop-auth `AuthenticationFilter`, enabling Kerberos/SPNEGO HTTP authentication.
- `GroupMappingServiceProvider` defines user-to-group lookup plus group cache refresh/add operations and exposes `GROUP_MAPPING_CONFIG_PREFIX`.
- `IdMappingConstant` publishes user/group id mapping configuration keys, defaults, minimum update interval, unknown user/group labels, and static mapping file configuration.
- `IdMappingServiceProvider` maps user and group names to numeric ids and back, including variants that allow unknown users/groups.
- `JniBasedUnixGroupsMappingWithFallback` and `JniBasedUnixGroupsNetgroupMappingWithFallback` implement group mapping through native Unix/JNI paths with fallback behavior.
- `ProviderUtils.unnestUri(URI)` translates nested credential-provider URIs into Hadoop `Path` values for provider implementations.
- `SaslPlainServer.SaslPlainServerFactory` creates SASL/PLAIN servers and advertises mechanism names; `SaslPlainServer.SecurityProvider` registers the SASL provider.
- `SaslPropertiesResolver` is configurable and returns default, server, and client SASL property maps. It also has a static `getInstance(Configuration)` factory.
- `SaslRpcServer.AuthMethod` and `SaslRpcServer.QualityOfProtection` are enum-like nested types for RPC SASL mechanisms and QOP settings. `AuthMethod` can read/write itself to `DataInput`/`DataOutput`.
- `SaslRpcServer.SaslDigestCallbackHandler` and `SaslRpcServer.SaslGssCallbackHandler` expose JAAS callback handling for token/digest and Kerberos/GSS flows.
- `SecurityUtil.QualifiedHostResolver` resolves host names to qualified `InetAddress` values.
- `ShellBasedIdMapping` maps ids and names by shelling out to platform commands, supports static mappings, periodically updates maps, and exposes synchronized lookup/update methods.
- `UserGroupInformation.AuthenticationMethod` exposes conversion between UGI auth methods and `SaslRpcServer.AuthMethod`.
- `WhitelistBasedResolver` extends `SaslPropertiesResolver` and changes server SASL properties based on whether a client address is in fixed, variable, or constant IP allowlists. It exposes configuration keys for whitelist files, cache intervals, enablement, and non-whitelist RPC protection.

### Credential Providers

- `CredentialProvider` abstracts credential/password storage. It exposes transient-provider detection, `flush()`, alias lookup/listing, credential creation/deletion, and `CLEAR_TEXT_FALLBACK`.
- `CredentialProvider.CredentialEntry` stores an alias and `char[]` credential and exposes alias, credential, and string rendering methods.
- `CredentialProviderFactory` creates providers from configured URI paths, exposes `CREDENTIAL_PROVIDER_PATH`, and discovers implementations through provider factories.
- `CredentialShell` is a `Configured` `Tool` for `hadoop credential` operations. It parses create/list/delete commands, prompts for credentials, allows stdout/stderr capture, uses an injectable `PasswordReader`, and provides a `main` entry point.
- `CredentialShell.PasswordReader` reads passwords and formats prompts/messages.
- `JavaKeyStoreProvider.Factory` and `UserProvider.Factory` implement provider creation for Java keystore-backed and user-backed credential stores.

### Protobuf Refresh Protocol Translators

- `RefreshAuthorizationPolicyProtocolClientSideTranslatorPB` implements `ProtocolMetaInterface`, `RefreshAuthorizationPolicyProtocol`, and `Closeable`; it forwards `refreshServiceAcl()`, supports `isMethodSupported`, and closes its PB proxy.
- `RefreshAuthorizationPolicyProtocolServerSideTranslatorPB` implements `RefreshAuthorizationPolicyProtocolPB` and maps protobuf `refreshServiceAcl` requests to the server-side `RefreshAuthorizationPolicyProtocol`.
- `RefreshUserMappingsProtocolClientSideTranslatorPB` implements `ProtocolMetaInterface`, `RefreshUserMappingsProtocol`, and `Closeable`; it forwards user-to-group and superuser-groups refresh calls and supports `isMethodSupported`.
- `RefreshUserMappingsProtocolServerSideTranslatorPB` implements `RefreshUserMappingsProtocolPB` and translates protobuf refresh requests into the server-side `RefreshUserMappingsProtocol`.

### SSL and Delegation-Token Web Auth

- `SSLHostnameVerifier.AbstractVerifier` implements Hadoop's hostname verifier contract. It provides `verify(host, SSLSession)` plus overloaded `check(...)` methods for sockets, certificates, CN arrays, subjectAlt arrays, and multiple hostnames, and helper methods for IPv4 detection, country wildcard acceptability, localhost detection, and dot counting.
- `SSLHostnameVerifier.Certificates` extracts common names and DNS SubjectAlt names from `X509Certificate` instances.
- `SslSocketConnectorSecure` extends Jetty `SslSocketConnector` and overrides `newServerSocket` to reject SSLv3 while allowing TLS 1.x, explicitly addressing CVE-2014-3566/POODLE.
- `DelegationTokenAuthenticatedURL` extends `AuthenticatedURL` with Hadoop delegation-token support. It has constructors for default authenticator, supplied `DelegationTokenAuthenticator`, `ConnectionConfigurator`, or both. It manages a static default authenticator class, controls header versus query-string token transmission, opens authenticated HTTP(S) connections with optional `doAs`, fetches tokens, renews tokens, and cancels tokens.
- `DelegationTokenAuthenticatedURL.Token` extends `AuthenticatedURL.Token` and stores a Hadoop `Token`, with getter and setter.
- `DelegationTokenAuthenticator` wraps another `Authenticator` and adds delegation-token operations. It supports connection configurators, authentication, token fetch, token renewal, and token cancellation, with optional `doAsUser` variants. Public constants describe operation/query/header/json parameter names.
- `KerberosDelegationTokenAuthenticator` uses Kerberos SPNEGO for HTTP authentication and falls back to `PseudoDelegationTokenAuthenticator` when the endpoint does not trigger SPNEGO.
- `PseudoDelegationTokenAuthenticator` uses Hadoop pseudo authentication by passing the current user as a query parameter while still supporting delegation-token operations.

### Service Lifecycle

- `AbstractService` implements `Service` and provides the base lifecycle state machine. The visible API includes construction by name, state/failure/config/start-time/history accessors, `init(Configuration)`, `start()`, `stop()`, `close()`, failure recording, wait-for-stop, protected extension hooks `serviceInit`, `serviceStart`, and `serviceStop`, local and global listener registration, state checks, string rendering, and blocker map management.
- `CompositeService` extends `AbstractService` to manage child services. It exposes a cloned child service list, protected `addService`, `addIfService`, `removeService`, and lifecycle overrides that initialize/start/stop children. The `STOP_ONLY_STARTED_SERVICES` policy controls whether shutdown stops only started children or all children.
- `CompositeService.CompositeServiceShutdownHook` is a `Runnable` that stops a composite service during JVM shutdown.
- `LifecycleEvent` is a serializable state-transition record with public `time` and `state` fields.

## Control Flow

Record I/O control flow is stream-oriented and callback based. Generated `Record` subclasses call `RecordOutput.startRecord`, serialize each field through typed primitive/composite methods, then call `endRecord`; readers mirror that through `RecordInput.startRecord`, typed `read*` calls, `Index` iteration for vectors/maps, and `endRecord`. Untagged `Record.write`/`readFields` adapt this generated-record flow to Hadoop `Writable` APIs. `Utils` supplies the variable-length integer and byte-comparison primitives that binary encoders and comparators rely on.

Record compiler flow is: JavaCC scanner/parser classes read DDL text, recognize includes/modules/records/fields/types, build compiler model objects (`JFile`, `JRecord`, `JField`, `JType` subclasses), and `JFile.genCode()` emits target-language source. `Rcc.main`/`driver` and `RccTask.execute` are the command-line and Ant entry points into the same compiler path.

Security control flow is mostly configuration and protocol driven. HTTP containers call `AuthenticationFilterInitializer.initFilter`, which copies prefixed Hadoop config into a servlet filter. RPC setup uses `AnnotatedSecurityInfo` and token/Kerberos annotations, then SASL handlers and property resolvers decide authentication mechanism and protection level. Group and id mapping calls flow through provider interfaces to JNI, shell, or configured implementations; `WhitelistBasedResolver` applies allowlist checks before returning SASL properties.

Credential control flow starts with `CredentialProviderFactory.getProviders(Configuration)`, which resolves configured provider URIs, delegates URI handling to provider factories, then exposes provider instances to callers. Callers create/read/delete entries, and durable providers persist buffered changes at `flush()`. `CredentialShell` wraps the same provider operations behind a command-line `Tool`.

Refresh-protocol control flow crosses the protobuf boundary. Client-side translators implement old Java protocol interfaces and call PB proxies; server-side translators receive protobuf request/response calls and delegate to non-PB protocol implementations, translating thrown exceptions into `ServiceException` as declared.

Delegation-token web control flow starts with normal `AuthenticatedURL` authentication unless a delegation token is already present in the nested token object. Token fetch/renew operations authenticate with the configured authenticator, optionally use `doAsUser`, and exchange JSON/HTTP parameters with the service endpoint. Cancellation is documented as not requiring authentication by the configured authenticator. Connection opening can transmit the delegation token through an HTTP header by default or query string for compatibility.

Service lifecycle control flow is state-transition based. `AbstractService.init` calls `serviceInit`, `start` calls `serviceStart`, and `stop` calls `serviceStop`; failures are recorded and can trigger stop behavior. Listeners observe state changes locally or globally. `CompositeService` sequences those transitions across child services and its shutdown hook delegates JVM shutdown to `stop()`.

## State and Persistence Behavior

The JDiff XML itself is persistent generated metadata. Within the APIs it describes, record I/O state is stream-local for `XmlRecordInput`/`XmlRecordOutput`, while generated records persist data through `Writable` and the record serialization formats. `RecordTypeInfo`, `TypeID`, and related metadata objects persist schema descriptions through `RecordInput`/`RecordOutput`; equality and hash behavior provide schema comparison signals.

The record parser classes are mutable. `Rcc` holds token source and current/next tokens, `RccTokenManager` holds lexical state and current characters, `SimpleCharStream` holds buffer positions and line/column arrays, and `ParseException` holds current token, expected token sequences, token images, and constructor mode. Reinitialization methods reset this parser state for reused parser instances.

Security state is distributed across process configuration, caches, and external systems. Group mapping providers have refreshable caches. Shell id mapping stores user/group maps and periodically refreshes them from system commands and static mapping files. SASL property resolvers hold `Configuration` and may cache whitelist contents. UGI authentication-method metadata ties public enum values to RPC SASL method codes.

Credential providers distinguish transient and durable stores. The `CredentialProvider` API makes `flush()` the persistence boundary, while the nested `CredentialEntry` keeps credential material in a `char[]`. Java keystore providers persist to keystore-backed storage; user providers are intended for transient job/user credential use.

Delegation-token APIs mutate authentication state carried by `DelegationTokenAuthenticatedURL.Token`: fetched tokens are stored there, renew operations return new expiration times, and cancellation invalidates server-side token state. Header versus query-string token transmission is per-URL object behavior controlled by `setUseQueryStringForDelegationToken`.

Service state is explicit and queryable. `AbstractService` stores current state, failure cause/state, configuration, start time, lifecycle event history, listeners, and blockers. `LifecycleEvent` persists transition time and state as a serializable object. `CompositeService` holds child-service state indirectly by maintaining its service list.

## Dependencies and Integration Points

- Record I/O depends on Hadoop `WritableComparable`, `WritableComparator`, `Buffer`, `Index`, `RecordInput`, `RecordOutput`, Java I/O streams, `DataInput`, `DataOutput`, and collection types such as `ArrayList` and `TreeMap`.
- The record compiler integrates with JavaCC-generated parser classes and Ant (`Task`, `BuildException`, `FileSet`).
- Record metadata integrates with the deprecated record runtime, especially `Record`, `RecordInput`, `RecordOutput`, and `TypeID`.
- Security APIs integrate with `Configuration`, `FilterInitializer`, `FilterContainer`, hadoop-auth `Authenticator` and `AuthenticatedURL`, JAAS callbacks, SASL server factories, `SecretManager`, IPC server connections, `InetAddress`, `BiMap`, and Hadoop `Path`.
- Credential providers integrate with `Configuration`, provider URI paths, Java service loading, `Tool`, `Configured`, console/password readers, and keystore/user-backed provider factories.
- ProtocolPB translators integrate old Java admin refresh interfaces with protobuf service interfaces and `com.google.protobuf.RpcController`/`ServiceException`.
- SSL classes integrate Java `SSLSession`, `SSLSocket`, `SSLException`, `X509Certificate`, and Jetty's `SslSocketConnector`.
- Delegation-token web auth integrates HTTP(S) URLs, `HttpURLConnection`, Hadoop security tokens, `ConnectionConfigurator`, Kerberos SPNEGO, pseudo auth, and service-side delegation-token operation parameters.
- Service lifecycle integrates `Configuration`, `Closeable`, `IOException`, listener interfaces, JVM shutdown hooks, and child `Service` implementations.

## Risks and Edge Cases

- This chunk starts inside `Record` and ends before later service classes, so merge/reconciliation must combine adjacent chunks before drawing whole-file conclusions.
- The record APIs are deprecated but still public. Generated legacy code may still depend on exact method names, checked exceptions, comparator registration, and wire encodings.
- Variable-length integer encoding and XML/CSV escaping are compatibility-sensitive. Any behavioral mismatch in sign handling, byte count, percent escaping, UTF-8 normalization, or buffer hex encoding can corrupt persisted records.
- JavaCC-generated parser classes expose mutable public/protected fields and many reinitialization overloads. Generated-code regeneration can accidentally change token ids, token images, lexical states, or parse error text.
- `RecordTypeInfo.compareTo` is documented as not providing meaningful ordering despite satisfying the abstract `Record` contract; callers relying on sorted behavior would be fragile.
- Group/id mapping depends on native libraries, shell command output, static mapping files, update intervals, and unknown-user fallbacks. Platform differences can cause subtle authorization or NFS identity errors.
- SASL whitelist resolution changes protection settings based on client address. Bad subnet parsing, stale variable-list caches, or hostname/address normalization issues can weaken RPC protection or block legitimate clients.
- Credential APIs handle secret material. `toString()`, shell output, merge behavior, and provider fallback to cleartext need careful testing to avoid leakage or unexpected downgrade.
- PB translators are thin adapters; exception translation and `isMethodSupported` behavior must remain compatible across mixed-version clients and servers.
- Hostname verification and SSL protocol filtering are security-critical. Wildcard matching, subjectAlt extraction, localhost shortcuts, IPv4 handling, and SSLv3 disabling need regression coverage.
- Delegation tokens sent in query strings are more likely to appear in logs than header-carried tokens. The compatibility switch is useful but carries exposure risk.
- `AuthenticatedURL` instances are documented as not thread-safe. Sharing `DelegationTokenAuthenticatedURL` or its mutable token object across threads can cause race-sensitive authentication behavior.
- Service lifecycle hooks are intended to run once per service instance and are not required to be synchronized by subclasses. Incorrect state transition handling, listener callbacks, or composite stop ordering can leave services partially initialized or not fully stopped.

## Test Signals

- API compatibility tests should verify all visible classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, visibility flags, and deprecation markers in this range.
- Record I/O tests should round-trip generated records through tagged and untagged serializers, including primitives, strings, buffers, nested records, vectors, maps, XML, CSV, binary encodings, and positive/negative variable-length integers.
- Record compiler tests should parse DDL includes, modules, primitive/composite fields, comments, invalid syntax, and recursive includes; they should exercise both `Rcc` command-line/driver flow and Ant `RccTask`.
- Metadata tests should serialize/deserialize `RecordTypeInfo`, compare `TypeID`/`FieldTypeInfo`/map/vector/struct metadata, and verify `meta.Utils.skip()` for every supported type.
- Security tests should cover annotation-derived `SecurityInfo`, auth filter parameter propagation, JNI fallback group mapping, shell id mapping refresh/static mappings, unknown id handling, SASL auth-method read/write, callback handlers, and whitelist-based QOP selection.
- Credential tests should cover provider discovery from configured paths, JKS and user provider factory selection, alias listing, create/delete/read, duplicate aliases, `flush()`, transient provider behavior, password prompting, and shell stdout/stderr capture without leaking credential values.
- PB translator tests should run client/server translator pairs for refresh-service-ACL, user-group mapping refresh, superuser-group refresh, close behavior, unsupported methods, and exception propagation as `IOException` or `ServiceException`.
- SSL tests should verify CN and DNS SubjectAlt extraction, wildcard matching rules, IPv4 and localhost handling, hostname mismatch failures, and that `SslSocketConnectorSecure` refuses SSLv3 while allowing TLS.
- Delegation-token web tests should cover default authenticator selection, custom authenticator/configurator constructors, header versus query-string token transport, `doAs` handling, get/renew/cancel operations, unauthenticated cancellation path, Kerberos fallback to pseudo auth, and non-thread-safe token mutation assumptions.
- Service tests should cover legal and illegal state transitions, null configuration rejection, hook call ordering, failure recording, listener/global-listener notification, wait-for-stop behavior, blocker map updates, composite child ordering, shutdown hook behavior, and lifecycle event serialization.

### subset-b-007158: lines 42402-45596

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 42402-45596

## Scope

This chunk is a JDiff API description for part of the Hadoop Common 2.6.0 public surface. It starts in `org.apache.hadoop.service`, then covers protocol-buffer translators for user/group mapping, tracing administration protocol types, many `org.apache.hadoop.util` helper APIs, and the beginning of `org.apache.hadoop.util.bloom`. The file records signatures, inheritance, visibility, exceptions, and Javadoc rather than method bodies, so implementation behavior below is inferred from the documented API contract and matching Java sources in the same Hadoop Common tree where available.

## Purpose

The covered APIs provide reusable infrastructure used across Hadoop daemons, command-line tools, RPC protocols, and filesystem utilities:

- Service lifecycle management: state model, transition validation, listeners, logging, and cleanup helpers.
- Protocol adapters: PB client/server translators for `GetUserMappingsProtocol` and tracing administration protocol interfaces.
- Utility foundations: application class loading, IP allow lists, reference counting, version comparison, checksums, disk/exit exceptions, bounded input streams, option wrappers, progress callbacks, protobuf IPC helpers, reflection, shell execution, shutdown hooks, string interning, binary prefix parsing, command runner support, and waitable values.
- Bloom filter data structures: standard, counting, dynamic, and retouched Bloom filters plus hash and removal-scheme helpers.

Because this is an API-diff artifact, its main value is compatibility research: identifying externally visible contracts that downstream code may compile against or depend on at runtime.

## Important APIs, Types, and Functions

### Service lifecycle APIs

- `LoggingStateChangeListener` implements `ServiceStateChangeListener` and logs state-change events at INFO level. It can log to a provided Commons Logging `Log` or to its class log.
- `Service` is the core lifecycle interface. It extends `Closeable` and defines `init(Configuration)`, `start()`, `stop()`, `close()`, listener registration, `getName()`, `getConfig()`, state/failure accessors, `waitForServiceToStop(long)`, lifecycle history snapshots, and blocker maps for remote dependencies preventing liveness.
- `Service.STATE` is a stable-valued enum with `NOTINITED`, `INITED`, `STARTED`, and `STOPPED`; `getValue()` exposes explicit numeric values for array lookup and management interfaces, and `toString()` returns the state name.
- `ServiceOperations` provides static lifecycle helpers. `stop(Service)` invokes `stop()` when non-null; `stopQuietly(Service)` and `stopQuietly(Log, Service)` catch and return `Exception`s for cleanup paths.
- `ServiceOperations.ServiceListeners` manages `ServiceStateChangeListener` registrations. `add`, `remove`, and `reset` are synchronized; `notifyListeners(Service)` snapshots the listener array before callback dispatch so registrations can change while notifications are in progress.
- `ServiceStateChangeListener.stateChanged(Service)` is called after the service state already changed, on the initiating thread and while the service is in a synchronized section. Javadoc explicitly warns that slow callbacks delay state transitions and re-entrant service calls can deadlock.
- `ServiceStateException` is a `RuntimeException` for invalid lifecycle operations and includes `convert(Throwable)` overloads to wrap checked exceptions.
- `ServiceStateModel` owns transition validation. It holds a volatile current `Service.STATE`, supports `ensureCurrentState`, synchronized `enterState`, static `checkStateTransition`, and static `isValidStateTransition`. The valid transition matrix permits `NOTINITED -> INITED|STOPPED`, `INITED -> INITED|STARTED|STOPPED`, `STARTED -> STARTED|STOPPED`, and only `STOPPED -> STOPPED`.

### Protocol and tracing APIs

- `GetUserMappingsProtocolClientSideTranslatorPB` adapts the PB interface to `GetUserMappingsProtocol` and `ProtocolMetaInterface`. It builds `GetGroupsForUserRequestProto`, calls `GetUserMappingsProtocolPB.getGroupsForUser`, converts response groups to `String[]`, supports method capability checks through `RpcClientUtil`, and closes by stopping the RPC proxy.
- `GetUserMappingsProtocolServerSideTranslatorPB` adapts a server-side `GetUserMappingsProtocol` implementation to the PB blocking interface, translating `IOException` into protobuf `ServiceException` and copying group strings into `GetGroupsForUserResponseProto`.
- `SpanReceiverInfo` exposes span receiver id and implementation class name. `SpanReceiverInfoBuilder` constructs it from a class name and configuration pairs.
- `TraceAdminProtocol` exposes `listSpanReceivers()`, `addSpanReceiver(SpanReceiverInfo)`, and `removeSpanReceiver(long)`, all throwing `IOException`; it also publishes `versionID`.
- `TraceAdminProtocolPB` is the protobuf protocol marker/extension point for the tracing administration service.

### General utility APIs

- `ApplicationClassLoader` is a child-first `URLClassLoader` for application isolation. It accepts URL arrays or a classpath string, expands wildcard jar directories, and treats configured system-class patterns as parent-first. `isSystemClass(String, List<String>)` supports positive and negative package/class patterns.
- `IPList` defines `isIn(String)`. `FileBasedIPList` loads IPs and CIDR ranges from a UTF-8 file into a `MachineList`; `CacheableIPList` wraps it with volatile cache expiry and explicit refresh; `CombinedIPWhiteList` checks fixed and optional reloadable allow lists and always allows `127.0.0.1`; `MachineList` accepts hostnames, IPs, CIDRs, and wildcard `*`, resolving hosts through an injectable `InetAddressFactory`.
- `CloseableReferenceCount` is an atomic open/closed plus reference-count guard. `reference()` fails with `ClosedChannelException` after closure, `unreference()` reports when closed with zero references, `unreferenceCheckClosed()` detects asynchronous close, and `setClosed()` atomically marks the object closed.
- `ComparableVersion` is a Maven-derived version comparator. It parses mixed dot/dash/digit/string components, normalizes known qualifiers such as alpha, beta, milestone, rc, snapshot, release/final/ga, and sp, and implements `compareTo`, `equals`, `hashCode`, and `toString`.
- `DataChecksum.Type` exposes checksum enum lookup and fields `id` and `size`, letting callers map wire ids to checksum kinds.
- `DiskChecker.DiskErrorException`, `DiskChecker.DiskOutOfSpaceException`, `ExitUtil.ExitException`, and `ExitUtil.HaltException` expose structured exception types with status codes where applicable.
- `IdentityHashStore.Visitor`, `IntrusiveCollection.IntrusiveIterator`, `LightWeightCache.Entry`, `LightWeightGSet.LinkedElement`, and `LightWeightGSet.SetIterator` are collection support APIs for identity-key visitation, intrusive iteration/removal, cache expiration timestamps, linked hash-set elements, and modification tracking.
- `LimitInputStream` wraps an `InputStream` and enforces a remaining byte limit across `read`, bulk `read`, `skip`, `available`, `mark`, and `reset`.
- `Options` is a typed varargs option framework with wrapper subclasses for boolean, integer, long, class, string, `Path`, `FSDataInputStream`, `FSDataOutputStream`, and `Progressable`. `getOption` returns the first exact-class match; `prependOptions` prefixes new options ahead of old ones.
- `PerformanceAdvisory.LOG` exposes a dedicated SLF4J logger for performance warnings. `Progressable.progress()` is the callback used by Hadoop APIs to report forward progress.
- `ProtoUtil` provides protobuf IPC helpers: raw varint32 reading, IPC connection context creation from protocol/UGI/auth method, UGI reconstruction from protobuf user info, RPC kind conversion, and request header creation including call id, retry count, client id, tracing context, caller context, authorization header, and optional alignment context.
- `PureJavaCrc32` and `PureJavaCrc32C` implement Java `Checksum`-style CRC32 and CRC32C operations with `getValue`, `reset`, and byte-array/single-byte `update`.
- `ReflectionUtils` handles configuration injection, reflective construction with constructor caching, thread dump printing/logging with rate limiting, typed class lookup, Writable copy/clone via Hadoop serialization buffers, and inherited field/method discovery.
- `Shell.CommandExecutor`, `Shell.ExitCodeException`, `Shell.OSType`, and `Shell.ShellCommandExecutor` expose the command execution API. The executor supports command arrays, working directory, environment, timeout, output retrieval, exit code retrieval, and close.
- `ShutdownHookManager` is a singleton priority-ordered shutdown hook registry with add/remove/has/isShutdownInProgress methods. `ShutdownThreadsHelper` interrupts threads or shuts down `ExecutorService`s with default or caller-specified timeouts.
- `StringInterner` exposes strong and weak string interning. `StringUtils.TraditionalBinaryPrefix` maps binary prefixes to bit shifts/masks, parses strings to long values, and formats long values with binary units.
- `ThreadUtil.sleepAtLeastIgnoreInterrupts(long)` preserves minimum sleep duration while ignoring interrupts. `Tool` plus `ToolRunner` define the standard Hadoop command entry point, generic options parsing, usage printing, and interactive confirmation prompt.
- `Waitable<T>` wraps a `Condition`-backed value with `await`, `provide`, `hasVal`, and `getVal`.

### Bloom filter APIs

- `BloomFilter` extends `Filter` and implements a bit-vector Bloom filter. It supports default construction for `readFields`, parameterized construction with vector size, hash count, and hash type, plus `add`, `membershipTest`, bitwise `and`, `or`, `xor`, `not`, `toString`, `getVectorSize`, and Writable serialization.
- `CountingBloomFilter` extends `Filter` with 4-bit counters instead of bits. It supports `add`, `delete`, `membershipTest`, approximate key counts, `and`, `or`, `toString`, and Writable serialization. `not` and `xor` are declared but unsupported in implementation.
- `DynamicBloomFilter` extends `Filter` with a matrix of standard Bloom filters. It creates new rows when the active row reaches threshold `nr`, and it supports membership across rows plus row-wise logical operations and serialization.
- `HashFunction` wraps `org.apache.hadoop.util.hash.Hash` to generate `nbHash` positions under a `maxValue`; `clear()` is a no-op and `hash(Key)` rejects null/empty key bytes.
- `RemoveScheme` defines retouched Bloom filter clearing modes: `RANDOM`, `MINIMUM_FN`, `MAXIMUM_FP`, and `RATIO`.
- `RetouchedBloomFilter` extends `BloomFilter` and implements `RemoveScheme`. It tracks known keys and false-positive keys per bit, supports adding false-positive evidence in single/collection/list/array forms, and `selectiveClearing(Key, short)` chooses a bit to clear according to the requested scheme.

## Control Flow

Service control flow is a state-machine contract. Callers construct a `Service`, call `init(Configuration)`, then `start()`, and eventually `stop()` or `close()`. Implementations are required to transition through the documented states or stop on failure. `ServiceStateModel.enterState` performs the transition check atomically and returns the previous state. State listeners are notified after transitions; `ServiceOperations.ServiceListeners` snapshots the callbacks and invokes them synchronously on the caller's thread.

PB translator flow is adapter-based. On the client side, Java interface calls are converted to request protos, sent through a PB proxy, and converted back to Java arrays or booleans. On the server side, PB requests call the underlying Java implementation, then copy Java values into response protos. Checked `IOException`s cross the PB boundary as protobuf `ServiceException`s.

Utility control flow is mostly synchronous and local. `ApplicationClassLoader` tries child URLs first for non-system classes/resources, then delegates to the parent. IP-list checks flow from `CombinedIPWhiteList` through fixed and cached lists into `MachineList` hostname/CIDR matching. `LimitInputStream` decrements a remaining-byte counter on every successful read or skip. `ToolRunner.run` parses Hadoop generic CLI options into a `Configuration`, sets the tool configuration, and invokes `Tool.run` with remaining arguments.

RPC header construction in `ProtoUtil` layers optional context into a required header: RPC kind, operation, call id, retry count, client id, current tracing span, current caller context, current authorization header, and optional alignment state. UGI serialization differs by auth method: Kerberos sends effective user only, token sends no user info, and simple auth sends effective plus optional real user.

Shell and shutdown flows manage external processes and JVM termination. `Shell.ShellCommandExecutor.execute()` runs a configured command and captures output/exit status. `ShutdownHookManager` registers one JVM hook, sorts registered hooks by priority, executes each through a single-thread executor with timeout enforcement, and then shuts the executor down. `ShutdownThreadsHelper` interrupts threads or shuts down executors and waits before escalating to `shutdownNow()`.

Bloom filter flow is hash-then-mutate or hash-then-test. `HashFunction.hash` derives multiple positions using repeated seeded hash invocations. `BloomFilter.add` sets those positions and `membershipTest` requires all positions to be set. `CountingBloomFilter.add` increments bounded 4-bit counters and `delete` decrements only if the key appears present. `DynamicBloomFilter.add` inserts into the active row or appends a row when full. `RetouchedBloomFilter.selectiveClearing` hashes a known false positive, chooses one candidate bit by the configured removal scheme, and clears it, trading false positives for possible false negatives.

## State and Persistence Behavior

The service APIs define in-memory lifecycle state, not durable persistence. `ServiceStateModel.state` is volatile and transition updates are synchronized. `Service.getLifecycleHistory()` and `getBlockers()` return snapshots, while failure cause/state expose first failure metadata maintained by implementations such as `AbstractService`.

The PB translators are mostly stateless wrappers around an RPC proxy or implementation reference. Their external state is the remote RPC connection, closed through `RPC.stopProxy`.

Several utility classes keep process-local mutable state:

- `ApplicationClassLoader` stores parent loader and system-class pattern lists and relies on URLClassLoader's loaded-class cache.
- `CacheableIPList` stores a volatile `FileBasedIPList` and volatile expiry timestamp; refresh forces reload on the next lookup.
- `CloseableReferenceCount` packs open/closed status and reference count into an `AtomicInteger` bit field.
- `ReflectionUtils` caches constructors in a static concurrent map and uses thread-local serialization buffers for object copying.
- `ShutdownHookManager` stores hook entries in a synchronized set and a shutdown-in-progress atomic flag.
- `StringInterner.strongIntern` intentionally retains strong references; `weakIntern` delegates to JVM string interning behavior in this API generation.

Bloom filters persist through Hadoop `Writable` serialization. `Filter.write` records a version marker, number of hashes, hash type, and vector size; `readFields` also handles an older unversioned format by treating the first positive int as `nbHash` and defaulting to Jenkins hash. Concrete filters append their bit vector, counter array, dynamic matrix rows, or retouched vectors. This persistence is binary and parameter-sensitive: readers must reconstruct hash functions and internal arrays from the serialized metadata before using the filter.

## Dependencies and Integration Points

- Service APIs integrate with `org.apache.hadoop.conf.Configuration`, `AbstractService`, `CompositeService`, lifecycle event history, Commons Logging/SLF4J logging, and daemon shutdown code.
- User mapping translators integrate with Hadoop IPC (`RPC`, `RpcClientUtil`, `ProtocolMetaInterface`), shaded protobuf controller/service exceptions, and generated `GetUserMappingsProtocolProtos`.
- Tracing APIs integrate with Hadoop tracing span receiver management and protobuf tracing admin service definitions.
- Utility classes depend on Hadoop FS types (`Path`, `FSDataInputStream`, `FSDataOutputStream`, `FileUtil`), Hadoop IPC protobufs, `UserGroupInformation`, auth methods, `CallerContext`, `AuthorizationContext`, Hadoop serialization, `Writable`, Java management beans, Java concurrency primitives, Apache Commons Net `SubnetUtils`, and logging APIs.
- Shell utilities integrate with OS-specific Hadoop support such as `winutils.exe`, process execution, environment handling, and platform detection.
- `Tool` and `ToolRunner` integrate with `Configurable`, `Configuration`, `GenericOptionsParser`, command audit context, and CLI callers.
- Bloom filters depend on `org.apache.hadoop.util.hash.Hash`, `Key`, `Writable`, and Java collections/bitsets. They are marked public/stable in this API slice and can be used by HDFS, MapReduce, and downstream applications.

## Risks and Edge Cases

- The service listener contract is synchronous and potentially inside service locks. Slow callbacks or callbacks that re-enter the same service can stall lifecycle transitions or deadlock.
- `ServiceOperations.stop` in implementation simply calls `stop()` for non-null services; the XML Javadoc says it checks whether the service needs stopping. Callers should not rely on pre-check semantics without verifying the target version.
- `ServiceStateModel` allows idempotent transitions such as `INITED -> INITED`, `STARTED -> STARTED`, and `STOPPED -> STOPPED`. Code that treats repeated lifecycle calls as errors may diverge from this model.
- `Service.close()` declares `IOException` but the contract says implementations relay directly to `stop()` and never throw `IOException`; callers still need to handle runtime failures.
- PB translators depend on exact protobuf field mapping. Empty or null group arrays, method support checks, and `ServiceException` wrapping are important compatibility points for clients.
- `ApplicationClassLoader` is child-first only for non-system classes. Misconfigured negative/positive system class patterns can load incompatible Hadoop or dependency classes into an isolated application.
- IP allow-list behavior differs for nulls: `FileBasedIPList.isIn(null)` returns false, while `CombinedIPWhiteList.isIn(null)` and `MachineList.includes(null)` throw `IllegalArgumentException`. Callers should normalize inputs before choosing the wrapper.
- `CacheableIPList` uses wall-clock time and double-checked locking with volatile fields. Clock changes or very small cache timeouts can cause unexpected reload frequency.
- `CloseableReferenceCount` reserves bit 30 for closed state; extreme reference counts would collide with status bits, and unbalanced `unreference()` calls fail by precondition.
- `Options.getOption` uses exact class equality, not `isAssignableFrom`, so subclasses of the requested option wrapper are not returned.
- `ProtoUtil.readRawVarint32` must reject malformed or truncated encodings; fuzz tests should cover EOF after each byte and overlong varints.
- `ReflectionUtils` constructor caching pins classes and can matter in classloader-isolated environments. Serialization copy uses a static `SerializationFactory` initialized from the first configuration.
- `ToolRunner.confirmPrompt` reads raw `System.in` and loops until recognized input; tests need controlled streams to avoid hanging.
- `Shell.ShellCommandExecutor` and shutdown helpers depend on OS process behavior and interrupt handling. Timeout cancellation does not guarantee immediate process or hook termination if code ignores interrupts.
- `StringInterner.strongIntern` can grow without release. Use it only for bounded vocabularies.
- `CountingBloomFilter` counters saturate at 15; repeated inserts of the same key increase error rates, and deletion after collisions can introduce false negatives. `not` and `xor` are visible in the API but unsupported.
- `DynamicBloomFilter.membershipTest(null)` returns true in the matching implementation, unlike other Bloom filters that reject null keys. This surprising edge case can mask caller bugs.
- `RetouchedBloomFilter.selectiveClearing` deliberately introduces false negatives. The removal scheme constants are public shorts, so invalid values reach an assertion path rather than a checked exception.

## Test Signals

- Service lifecycle tests should cover every valid and invalid transition in `ServiceStateModel`, listener add/remove/reset behavior during notification, idempotent stop/close, failure cause/state capture, `waitForServiceToStop(0)` semantics, and blocker/lifecycle history snapshot immutability.
- Listener tests should include slow callbacks and re-entrant service calls to document deadlock/stall risks.
- PB translator tests should verify client request construction, server response construction, `IOException` to `ServiceException` wrapping, close behavior, and `isMethodSupported` against a mock proxy.
- Tracing protocol tests should validate span receiver list/add/remove behavior and builder preservation of class name and configuration pairs.
- Classloader tests should cover wildcard classpath expansion, missing classpath entries, child-first loading for application classes, parent-first system classes, and negative system-class overrides.
- IP-list tests should cover missing files, null inputs, wildcard entries, CIDR inclusive host counts, invalid CIDR syntax, unresolved hostnames, cache refresh, cache expiry, localhost whitelist behavior, and injected `InetAddressFactory`.
- Reference-count tests should cover concurrent reference/close races, unbalanced unreference detection, and `AsynchronousCloseException` from `unreferenceCheckClosed`.
- Utility tests should cover version ordering qualifiers, checksum type lookup, `LimitInputStream` mark/reset/skip/EOF behavior, exact-class option lookup, varint malformed input, UGI construction for Kerberos/token/simple auth, RPC header optional context fields, reflection constructor caching/config injection, Writable copy/clone behavior, shell executor timeout/output, shutdown hook priority/timeouts, binary prefix parse/format, and `Waitable` condition wakeups.
- Tool tests should assert generic options are stripped before `Tool.run`, configuration is injected, caller/audit context is set, usage text is emitted, and prompt parsing accepts only yes/no variants.
- Bloom filter tests should round-trip every concrete filter through `write/readFields`, verify membership false-positive/no-false-negative expectations for standard filters, reject incompatible logical operations, exercise counting saturation and delete behavior, force dynamic row expansion at `nr`, validate retouched clearing schemes, and test null/empty key handling for each filter type.
