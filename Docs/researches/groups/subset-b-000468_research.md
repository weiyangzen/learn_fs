# subset-b-000468 Research

Grouped research report for the requested Alluxio UFS common classes, UFS tests, and core server common utilities. Each section preserves the original source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ObjectUnderFileSystem.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ObjectUnderFileSystem.java

### Purpose
`ObjectUnderFileSystem` is the shared abstract implementation for object-store-backed UFS adapters. It translates Alluxio filesystem operations into object operations, synthesizes directory semantics from zero-byte directory marker objects plus common-prefix listings, implements retry behavior for eventual consistency, and provides batched concurrent delete/rename support for stores where rename is copy plus delete.

### Important APIs, Types, And Functions
The class extends `BaseUnderFileSystem`, so it inherits fingerprint, async listing, recursive listing fallback, ACL defaults, and rate limiting. Key nested types are `ObjectStatus` for object metadata, `ObjectListingChunk` for paginated listings, `ObjectPermissions` for bucket-level owner/group/mode, and the generic `OperationBuffer<T>` used by `DeleteBuffer` and `RenameBuffer`.

Subclass extension points are `createEmptyObject`, `createObject`, `copyObject`, `deleteObject`, `getPermissions`, `getObjectStatus`, `getFolderSuffix`, `getObjectListingChunk`, `getRootKey`, `openObject`, and `getUnderFSType`. Public UFS overrides cover create, delete, status, listing, mkdirs, open, rename, object-storage detection, unsupported file locations, and unsupported flush.

### Control Flow
Create optionally creates the parent path unless parent creation is skipped by configuration, then calls `createObject` on the stripped key. File status calls `getObjectStatus`; directory status uses `isDirectory`; general status checks root, then file metadata, then directory status. Directory existence is inferred from root, explicit marker object, or a listing whose first chunk has objects or common prefixes. `getObjectListingChunkForPath` may create a breadcrumb marker for discovered pseudo-directories when breadcrumbs are enabled and the mount is writable.

Listing obtains a first chunk, handles explicit empty-directory markers, normalizes the key prefix, then repeatedly calls `populateUfsStatus`. That method converts marker objects to `UfsDirectoryStatus`, ordinary objects to `UfsFileStatus`, and common prefixes or inferred recursive prefixes to directory statuses. `UfsStatusIterator` lazily fetches chunks and uses a sorted `TreeMap`, trimming entries already returned from a prior chunk by `mLastKey`.

Recursive delete lists descendants recursively, sorts them in reverse name order, batches file and marker deletes, then validates that all entries were deleted. Directory rename first copies the source marker, recursively copies children, queues deletes after successful copies, and fails if any batch has missing successes. File rename validates source file and destination absence, then copies and deletes. `retryOnException` retries only transient IO classes such as EOF, DNS, connection timeout, and socket errors; `retryOnFalse` retries false returns.

### State And Persistence
In-memory state includes the object-service executor, memoized root key supplier, breadcrumbs flag, and operation buffers. Persistent state is entirely in the object store: uploaded file objects, zero-byte directory marker objects using `getFolderSuffix`, copied destination objects, and deleted source keys. CRC64 metadata from `ObjectStatus` is propagated into `UfsFileStatus` xattrs under `Constants.CRC64_KEY`.

### Dependencies And Integration Points
This class depends on Alluxio configuration keys for object-store threads, breadcrumbs, listing length, block size, parent creation skipping, and eventual-consistency retry tuning. It integrates with `BaseUnderFileSystem` for async metadata sync and with provider implementations for S3, OSS, GCS, and similar stores. It uses `PathUtils`, `CommonUtils`, `RetryPolicy`, and executor factories.

### Risks
Object-store directory semantics are inherently inferred; marker-object and common-prefix handling must stay consistent or Alluxio metadata sync can miss or duplicate directories. Rename is non-atomic and can leave copied-but-not-deleted objects after partial failures. `OperationBuffer` suppresses per-batch IO exceptions into empty success lists, so callers must compare success counts. Breadcrumb creation during read/list paths mutates storage unless read-only. `handleRetriablException` appears misspelled but functional; expanding retry classes can hide permanent errors.

### Test Signals
`ObjectUnderFileSystemTest` verifies transient `SocketException` retry and non-retry for `FileNotFoundException`, plus object-store async listing behavior for `DescendantType.NONE`. `MockObjectUnderFileSystem` supplies a minimal subclass for these tests. Broader correctness depends on concrete object-store modules and metadata-sync tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/ObjectUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/SeekableUnderFileInputStream.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/SeekableUnderFileInputStream.java

### Purpose
This abstract class marks an under-file input stream as seekable. It wraps a regular `InputStream` with `FilterInputStream` while requiring subclasses to implement the `alluxio.Seekable` contract.

### Important APIs, Types, And Functions
The only constructor accepts the wrapped `InputStream` and passes it to `FilterInputStream`. The API surface is inherited: stream reads/delegation from `FilterInputStream` and seek/position methods from `Seekable`.

### Control Flow
There is no local read or seek implementation. Subclasses must reposition the wrapped stream when `seek(long)` is invoked.

### State And Persistence
State is the protected `FilterInputStream.in` delegate. No data is persisted.

### Dependencies And Integration Points
`UnderFileSystem.isSeekable()` documents that UFS implementations returning true should return streams extending this class from `open(String, OpenOptions)`.

### Risks
The class itself is simple; the risk is contractual. Returning true from `isSeekable` without returning this type, or implementing seek without synchronizing stream position, breaks positioned reads in upper layers.

### Test Signals
No direct test is in this subset. Coverage is expected in concrete UFS implementations with seekable stream support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/SeekableUnderFileInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsClient.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsClient.java

### Purpose
`UfsClient` defines the asynchronous metadata-listing client contract used by Alluxio metadata sync and exposes the per-UFS rate limiter.

### Important APIs, Types, And Functions
`performListingAsync` accepts a path, continuation token, start-after marker, `DescendantType`, `checkStatus`, completion callback, and error callback. Returned `UfsStatus` names are expected to be full paths from the UFS root, excluding object-store bucket names. `getRateLimiter` returns the UFS rate limiter.

### Control Flow
The interface does not implement behavior. `BaseUnderFileSystem` provides a default executor-backed implementation, while `UnderFileSystemWithLogging` wraps and forwards calls.

### State And Persistence
No state is declared here. Implementations may hold async executors, pagination tokens, and limiter state.

### Dependencies And Integration Points
The method uses `UfsLoadResult`, `UfsStatus`, `DescendantType`, `RateLimiter`, and Java `Consumer` callbacks. It is integrated into metadata sync v2 and listing pipelines that need async, bounded UFS work.

### Risks
Callback contracts are important: implementations must call exactly one completion or error path, produce full child names, and correctly use continuation/start-after semantics. Misreporting `firstIsFile`, truncation, or last item can break incremental sync.

### Test Signals
`UnderFileSystemTestUtil.performListingAsyncAndGetResult` converts this callback API into synchronous test flow. `ObjectUnderFileSystemTest` checks one object-store listing case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsDirectoryStatus.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsDirectoryStatus.java

### Purpose
`UfsDirectoryStatus` is the concrete `UfsStatus` variant for directories returned from UFS status and listing operations.

### Important APIs, Types, And Functions
Constructors accept name, owner, group, mode, optional last-modified time, and optional xattrs. The copy constructor delegates to `UfsStatus`. `copy()` returns a deep-ish copy of the status object, and `toString()` uses the inherited `toStringHelper`.

### Control Flow
Construction sets `isDirectory=true`; all field access and equality behavior comes from `UfsStatus`.

### State And Persistence
Instances hold only metadata in memory. The inherited copy constructor clones the xattr map but not the byte-array values inside it.

### Dependencies And Integration Points
Object stores synthesize this type from directory marker objects and common prefixes. Other UFS implementations return it from `getDirectoryStatus`, `getStatus`, and listings.

### Risks
It is annotated `@NotThreadSafe`; `setName` inherited from `UfsStatus` mutates listing results. Mutable xattr byte arrays can leak changes across copies.

### Test Signals
`UfsDirectoryStatusTest` verifies directory/file booleans, owner/group/mode/name getters, and copy equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsDirectoryStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsFileStatus.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsFileStatus.java

### Purpose
`UfsFileStatus` is the concrete `UfsStatus` variant for files. It adds content hash, content length, and block size metadata used for metadata sync, fingerprints, Web UI display, and block-size planning.

### Important APIs, Types, And Functions
Constants are `INVALID_CONTENT_HASH` as an empty string and `UNKNOWN_BLOCK_SIZE` as `-1`. Main constructors accept name, content hash, length, last-modified time, owner, group, mode, optional xattrs, and block size. Deprecated constructors keep older call sites working by filling `UNKNOWN_BLOCK_SIZE`. Accessors expose content hash, length, and block size.

### Control Flow
Construction sets `isDirectory=false`. `copy()` uses the copy constructor; `toString()` includes content hash and length in addition to base fields.

### State And Persistence
Instances are in-memory metadata snapshots. Copying clones the xattr map via the base copy constructor but shares each xattr byte array.

### Dependencies And Integration Points
`ObjectUnderFileSystem` creates this from `ObjectStatus`, with optional CRC64 xattr. `Fingerprint` uses content hash and permission fields to compare metadata/content. `UnderFileSystem` implementors return it from file status methods.

### Risks
Equality and hash code are inherited from `UfsStatus` and do not include file-specific fields such as content hash, content length, last-modified time, or block size. This is intentional or legacy behavior but risky if callers use equality as full metadata equality.

### Test Signals
`UfsFileStatusTest` verifies getters, file/directory booleans, last-modified time, block size, and copy equality. `FingerprintTest` exercises fingerprint creation with content hash overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsFileStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsLoadResult.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsLoadResult.java

### Purpose
`UfsLoadResult` is the result container for async UFS load/listing operations. It packages a stream of statuses with pagination and summary metadata.

### Important APIs, Types, And Functions
The constructor stores `Stream<UfsStatus>`, item count, nullable continuation token, nullable last item URI, truncation flag, first-item-is-file flag, and object-store flag. Getters expose these values; `getLastItem` wraps the nullable URI in `Optional`.

### Control Flow
There is no internal processing. Producers such as `BaseUnderFileSystem.performListingAsync` build the stream and count, then consumers read metadata through accessors.

### State And Persistence
State is immutable references, but the contained stream is single-use and the underlying `UfsStatus` objects may be mutable through `setName`.

### Dependencies And Integration Points
Used by `UfsClient.performListingAsync` callbacks and metadata sync. It carries `AlluxioURI` for the last item and signals whether follow-up listing should continue through continuation tokens.

### Risks
The method name `isIsObjectStore()` is awkward but public. Because `Stream` is one-shot, callbacks must not attempt multiple traversals. `itemsCount` must match the stream or progress accounting will be wrong.

### Test Signals
`ObjectUnderFileSystemTest` checks item count and first status for an async object-store listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsLoadResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsManager.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsManager.java

### Purpose
`UfsManager` is the service-level registry interface for UFS clients keyed by Alluxio mount ids, root, and journal locations.

### Important APIs, Types, And Functions
The nested `UfsClient` lazily creates and caches an `UnderFileSystem` from a supplier and exposes `acquireUfsResource()` plus `getUfsMountPointUri()`. The outer interface declares `addMount`, `addMountWithRecorder`, `removeMount`, `get`, `getRoot`, `getJournal`, and `hasMount`.

### Control Flow
`UfsClient.acquireUfsResource` uses an `AtomicReference` compare-and-set to initialize the underlying UFS once. If two callers race, the losing newly created UFS is closed. A metrics counter named `UfsSessionCount-Ufs:<escaped mount>` is incremented for each acquired resource and decremented when the `CloseableResource` is closed.

### State And Persistence
The nested client stores the cached UFS, mount URI, supplier, and session counter in memory. The manager implementation, outside this file, stores mount mappings. No direct persistence occurs here.

### Dependencies And Integration Points
Integrates with `UnderFileSystem`, `UnderFileSystemConfiguration`, `Recorder`, `CloseableResource`, Alluxio metrics, and status exceptions. Used by master/worker services to share and lifecycle-manage UFS access.

### Risks
Callers must close the returned `CloseableResource` or the session counter leaks. If the supplier returns an unusable UFS or throws unchecked exceptions, acquire fails. The cached UFS is not replaced after later failures unless implementation removal/close logic handles it elsewhere.

### Test Signals
No direct tests in this subset. Metric/session behavior is typically covered by UFS manager implementation tests elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsMode.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsMode.java

### Purpose
`UfsMode` enumerates the effective operation mode for under storage during normal operation or maintenance.

### Important APIs, Types, And Functions
The enum values are `NO_ACCESS`, `READ_ONLY`, and `READ_WRITE`.

### Control Flow
No behavior is defined. `BaseUnderFileSystem.getOperationMode` maps a physical-store state to one of these modes and defaults to `READ_WRITE`.

### State And Persistence
No state beyond enum constants.

### Dependencies And Integration Points
Used by mount and physical-UFS state logic to gate reads/writes or disable access.

### Risks
Consumers must consistently enforce the mode; the enum by itself has no policy.

### Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsMode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsStatus.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsStatus.java

### Purpose
`UfsStatus` is the abstract base metadata record for UFS files and directories returned by status and listing APIs.

### Important APIs, Types, And Functions
Fields include directory flag, nullable last-modified time, mutable name, owner, group, mode, and nullable xattr map. `copy()` is abstract. `convertToNames` converts a status array to a string array. Accessors expose file/directory flags, owner/group/mode/name/time/xattrs. `setName` mutates and returns `this`. Equality/hash code use name, directory flag, owner, group, mode, and xattr map.

### Control Flow
Subclasses call protected constructors. Copy construction clones the xattr map if present. `toStringHelper` standardizes subclass string output.

### State And Persistence
The status object is mutable through `mName`, and the xattr map and byte-array values are not deeply immutable. It is only an in-memory snapshot of UFS metadata.

### Dependencies And Integration Points
Used throughout UFS APIs, object-store listing conversion, metadata sync, and fingerprint creation. `BaseUnderFileSystem.performListingAsync` mutates names to become full paths.

### Risks
Marked `@NotThreadSafe`. Equality excludes last-modified time and file-specific data in `UfsFileStatus`, so it is not a full metadata comparison. `getXAttr` may return null despite its comment saying empty map when none.

### Test Signals
Directory and file status tests cover basic getters and copy equality. Fingerprint tests cover interactions with metadata fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UfsStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystem.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystem.java

### Purpose
`UnderFileSystem` is the central public contract for storage systems beneath Alluxio. It defines file, directory, metadata, ACL, fingerprint, active sync, listing, and lifecycle operations and distinguishes ordinary operations from eventual-consistency-aware variants.

### Important APIs, Types, And Functions
The nested `Factory` creates wrapped UFS instances by consulting `UnderFileSystemFactoryRegistry`, trying eligible factories with recorder logging and context classloader switching, wrapping successful clients in `UnderFileSystemWithLogging`, and exposing `createForRoot` for root mount configuration. `SpaceType` enumerates total/free/used space.

The interface includes lifecycle (`cleanup`, `close`, connect from master/worker), create/delete/rename/open/mkdir APIs, status and listing APIs, ACL/owner/mode mutation, file locations, fingerprints, operation mode, physical stores, object/seekable flags, URI resolution, flush support, active sync polling, sync point management, and inherited async listing/rate limiter methods from `UfsClient`.

### Control Flow
The factory path is important: find all factories, iterate in order, switch the current thread context classloader to the factory classloader, call `factory.create`, wrap in logging, return first success, and collate suppressed errors if all candidates fail. Root creation pulls root UFS URI, read-only flag, and root mount options from configuration.

### State And Persistence
The interface holds no state. Implementations persist data in their backing stores and may hold connections, credentials, threads, caches, and mount-specific configuration.

### Dependencies And Integration Points
This is used by Alluxio master, worker, journal, metadata sync, and mount machinery. It depends on Alluxio configuration, recorder, ACL types, `UfsStatus` types, option classes, `SyncInfo`, and `AlluxioURI`.

### Risks
The API is broad and includes legacy/deprecated methods. Implementations must honor eventual-consistency variants, atomic create semantics, full-path listing expectations for async sync, and seekable-stream contracts. Factory selection can be affected by service loader ordering, shading, and version matching.

### Test Signals
`UnderFileSystemTest` verifies that core-only factory discovery does not claim local, HDFS, OSS, S3, S3A, or Gluster paths without external modules. Many method contracts are tested through concrete UFS modules outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemConfiguration.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemConfiguration.java

### Purpose
`UnderFileSystemConfiguration` wraps an `AlluxioConfiguration` with UFS-specific behavior, mainly read-only state and mount-specific option precedence.

### Important APIs, Types, And Functions
Static constructors are `defaults(AlluxioConfiguration)` and `emptyConfig()`. Instance methods include `isReadOnly`, `createMountSpecificConf`, `getMountSpecificConf`, and `toUserPropertyMap`. The rest of the class delegates the `AlluxioConfiguration` interface to `mAlluxioConf`.

### Control Flow
`createMountSpecificConf` copies all properties, merges the provided mount map with `Source.MOUNT_OPTION`, and returns a new configuration preserving the read-only flag. `getMountSpecificConf` scans keys whose source is `MOUNT_OPTION`. `toUserPropertyMap` walks user keys and stringifies values while preserving nulls.

### State And Persistence
State is the wrapped configuration and immutable read-only flag. Creating mount-specific config copies property state but does not mutate the original.

### Dependencies And Integration Points
Used by UFS factories, root mount creation, object-store implementations, and options defaults. It depends on `AlluxioProperties`, `InstancedConfiguration`, property `Source`, and `ConfigurationValueOptions`.

### Risks
The class is `@NotThreadSafe` because the wrapped configuration may be mutable. Mount-specific maps accept `Object` values keyed by property names, so invalid key/value types fail later during configuration resolution. `EMPTY_CONFIG` is shared and should remain effectively immutable.

### Test Signals
`UnderFileSystemConfigurationTest` checks global property lookup, mount-specific override, missing property behavior, `isSet`, preservation of read-only, repeated mount-specific creation without mutating the base, and mount-specific conf extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemFactory.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemFactory.java

### Purpose
`UnderFileSystemFactory` is the extension-provider interface for creating UFS clients for supported paths.

### Important APIs, Types, And Functions
It extends `ExtensionFactory<UnderFileSystem, UnderFileSystemConfiguration>`. Implementations provide `create(String, UnderFileSystemConfiguration)` and `supportsPath(String)`. Defaults include `supportsPath(String, UnderFileSystemConfiguration)` delegating to the path-only variant and `getVersion()` returning an empty string.

### Control Flow
Factory registry discovery asks factories whether they support a path/config and then calls `create` on selected candidates. The interface documents that `create` should throw `IllegalArgumentException` when unsupported or insufficiently configured.

### State And Persistence
No state is declared. Implementations may hold provider-specific static metadata.

### Dependencies And Integration Points
Discovered via service loading through `UnderFileSystemFactoryRegistry` and extension jars matching `alluxio-underfs-*.jar`.

### Risks
Incorrect `supportsPath` behavior can make a factory shadow a better implementation or produce misleading creation failures. Version strings interact with strict version matching in the registry.

### Test Signals
`UnderFileSystemTest` indirectly checks registry behavior when no external factories should match certain schemes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemFactoryRegistry.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemFactoryRegistry.java

### Purpose
`UnderFileSystemFactoryRegistry` centralizes discovery, registration, version filtering, and lookup of UFS factories.

### Important APIs, Types, And Functions
Static methods include `available`, `find`, `findAllWithRecorder`, `getSupportedVersions`, `register`, `unregister`, and `reset`. The static registry is an `ExtensionFactoryRegistry<UnderFileSystemFactory, UnderFileSystemConfiguration>` configured with jar pattern `alluxio-underfs-*.jar`.

### Control Flow
Initialization happens in a synchronized `init`. `find` calls `findAllWithRecorder` and returns the first eligible factory or null with a warning. `findAllWithRecorder` asks the extension registry for candidates, warns/records supported versions when a configured `UNDERFS_VERSION` has no eligible factories, and optionally filters by exact `getVersion()` when strict version matching is enabled. `getSupportedVersions` unsets the requested version on a copy and gathers non-empty version strings from otherwise supporting factories.

### State And Persistence
State is the static registry instance and the service-loaded/manual factory list. No persistent storage is touched.

### Dependencies And Integration Points
Integrates Java `ServiceLoader`, Alluxio extension discovery, `Recorder`, and UFS version configuration keys. It is the first selection point used by `UnderFileSystem.Factory`.

### Risks
The class is marked `@NotThreadSafe`; static mutation through register/unregister/reset can affect concurrent tests or runtime factory lookup. Shaded jars can drop service metadata unless Maven service resource transformers are used. Strict version matching can filter out all factories even when path support exists.

### Test Signals
`UnderFileSystemTest` uses `find` to verify no unwanted core factory claims local or external-module schemes in a core-only classpath.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemFactoryRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemWithLogging.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemWithLogging.java

### Purpose
`UnderFileSystemWithLogging` is a decorator around any `UnderFileSystem` implementation. It logs entry/exit for IO-capable methods, records per-method timers and failure counters, warns on slow calls, filters invalid listing names containing `?`, and tags metrics with UFS identity and optionally user.

### Important APIs, Types, And Functions
The wrapper stores the delegate, UFS configuration, original path, escaped metric path, and logging threshold. Nearly all `UnderFileSystem` methods are forwarded through the private `call(UfsCallable<T>)` helper. `UfsCallable` supplies `call`, `methodName`, and argument string formatting. `filterInvalidPaths` exists for arrays and iterators. `getQualifiedMetricName` and `getQualifiedFailureMetricName` build metric names with `TAG_UFS`, `TAG_UFS_TYPE`, and possibly `TAG_USER`.

### Control Flow
For wrapped calls, `call` logs debug entry, starts a Dropwizard timer, invokes the delegate, logs debug success, emits a warning if duration exceeds `UNDERFS_LOGGING_THRESHOLD`, and returns. On `IOException`, it increments the failure counter, logs debug error, optionally warns, and rethrows. Methods that do not throw IO, such as operation mode, physical stores, object-storage flag, seekable flag, and active-sync support, usually forward directly. `performListingAsync` is wrapped despite being callback-based; any unexpected `IOException` becomes an internal runtime exception.

### State And Persistence
No UFS data is persisted by the wrapper. It persists runtime observability into the metrics system and logs. The wrapper does not own the delegate lifecycle beyond forwarding `close` and `cleanup`.

### Dependencies And Integration Points
Created by `UnderFileSystem.Factory` around successful provider clients. It integrates with `MetricsSystem`, `Metric`, authenticated client user state, security utilities, and Alluxio logging.

### Risks
Observability code can change behavior: listing results with `?` are silently filtered with warnings. `getFileStatus(String, GetFileStatusOptions)` forwards to `mUnderFileSystem.getFileStatus(path)` instead of passing the options, so option flags such as real content hash can be ignored through the wrapper. A method name typo, `RenameRenableDirectory`, affects metric naming. Slow-call logging may expose path/option strings in logs.

### Test Signals
No direct wrapper test is in this subset. Indirect factory tests create wrapped clients only when factories are present. Listing filter behavior and option forwarding merit targeted tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/UnderFileSystemWithLogging.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/CreateOptions.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/CreateOptions.java

### Purpose
`CreateOptions` carries per-call file creation options for UFS implementations.

### Important APIs, Types, And Functions
Defaults are built from the authorization umask in `AlluxioConfiguration`. Fields are create-parent, ensure-atomic, owner, group, mode, and optional ACL. Fluent setters update each field; getters expose them. Equality, hash code, and `toString` cover all fields.

### Control Flow
The private constructor sets create parent false, ensure atomic false, owner/group null, ACL null, and file mode to `ModeUtils.applyFileUMask(Mode.defaults(), authUmask)`.

### State And Persistence
Mutable in-memory option object only. UFS implementations decide how to persist owner, group, mode, ACL, and atomicity semantics.

### Dependencies And Integration Points
Used by `UnderFileSystem.create`, `ObjectUnderFileSystem.create`, and default create behavior inherited from `BaseUnderFileSystem`.

### Risks
`BaseUnderFileSystem.create(String)` overrides the default by setting create parent true, while direct `CreateOptions.defaults` has false. Callers must be explicit when parent creation needs to match master metadata behavior. The ACL object is stored by reference.

### Test Signals
`CreateOptionsTest` verifies defaults, security-enabled defaults, field setters, and equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/CreateOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/DeleteOptions.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/DeleteOptions.java

### Purpose
`DeleteOptions` carries delete-directory semantics, currently just recursive deletion.

### Important APIs, Types, And Functions
`defaults()` returns a new option with recursive false. `isRecursive` and fluent `setRecursive` expose the flag. Equality, hash code, and `toString` include the flag.

### Control Flow
The private constructor initializes non-recursive behavior. `ObjectUnderFileSystem.deleteDirectory` uses the flag to reject non-empty directories or to recursively list and batch delete descendants.

### State And Persistence
Mutable in-memory option object only.

### Dependencies And Integration Points
Used by `UnderFileSystem.deleteDirectory` and eventual-consistency variants.

### Risks
Non-recursive is the safe default. Accidentally setting recursive true can delete a tree; provider implementations must honor the flag.

### Test Signals
`DeleteOptionsTest` verifies default false, setter behavior, and equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/DeleteOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/FileLocationOptions.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/FileLocationOptions.java

### Purpose
`FileLocationOptions` carries an offset for querying physical file locations from a UFS.

### Important APIs, Types, And Functions
`defaults()` initializes offset zero. `getOffset` and `setOffset` expose the offset. Equality, hash code, and `toString` include it.

### Control Flow
The option is passed to `UnderFileSystem.getFileLocations(path, options)`. Object stores return null by default because locations are unsupported.

### State And Persistence
Mutable in-memory option only.

### Dependencies And Integration Points
Used by storage-aware scheduling/location queries in UFS implementations that can map file offsets to hosts.

### Risks
There is no validation for negative offsets in this object; implementations must validate if needed.

### Test Signals
`FileLocationOptionsTest` verifies default offset and setter behavior across several offsets, plus equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/FileLocationOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/GetFileStatusOptions.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/GetFileStatusOptions.java

### Purpose
`GetFileStatusOptions` carries optional behavior for file-status lookup, currently whether to include a real content hash.

### Important APIs, Types, And Functions
`defaults()` creates a new object with `includeRealContentHash=false`. `isIncludeRealContentHash` and `setIncludeRealContentHash` expose the flag.

### Control Flow
The flag is passed to `UnderFileSystem.getFileStatus(path, options)` so implementations can choose cheap placeholder hashes or compute/fetch stronger hashes.

### State And Persistence
Mutable in-memory option only.

### Dependencies And Integration Points
Used by file status and fingerprint-related flows. `UnderFileSystemWithLogging` currently drops this option when forwarding, which is an integration risk.

### Risks
No equals/hash/toString unlike other option classes. Callers going through the logging wrapper may not get requested real content hash behavior.

### Test Signals
No direct test for this class is in the requested subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/GetFileStatusOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/ListOptions.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/ListOptions.java

### Purpose
`ListOptions` carries directory listing semantics, currently whether listing should be recursive.

### Important APIs, Types, And Functions
`defaults()` returns recursive false. `isRecursive` and `setRecursive` expose the flag. Equality, hash code, and `toString` include it.

### Control Flow
`BaseUnderFileSystem.listStatus(path, options)` implements recursive traversal when true. `ObjectUnderFileSystem` passes the flag down to object listing and synthetic directory population.

### State And Persistence
Mutable in-memory option only.

### Dependencies And Integration Points
Used by UFS listing, metadata sync, recursive delete, and recursive rename logic.

### Risks
Recursive listing can be expensive and memory-heavy, especially for non-object UFS fallback which collects full arrays. Object-store recursive listings must correctly infer pseudo-directories.

### Test Signals
`ListOptionsTest` verifies default false, setter behavior, and equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/ListOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/MkdirsOptions.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/MkdirsOptions.java

### Purpose
`MkdirsOptions` carries per-call directory creation options for UFS implementations.

### Important APIs, Types, And Functions
Defaults come from authorization umask. Fields are create-parent, owner, group, and mode. Fluent setters update them; equality, hash code, and `toString` cover all fields.

### Control Flow
The constructor sets create parent true, owner/group null, and directory mode to `ModeUtils.applyDirectoryUMask(Mode.defaults(), authUmask)`. `ObjectUnderFileSystem.mkdirs` uses create-parent to decide whether to recursively create parent marker objects or fail when the parent is absent.

### State And Persistence
Mutable in-memory option only. UFS implementations persist resulting directory markers and metadata if supported.

### Dependencies And Integration Points
Used by `UnderFileSystem.mkdirs` and default mkdir behavior in `BaseUnderFileSystem`.

### Risks
Default parent creation can create more UFS state than a caller expects. Owner/group are null by default even when security is enabled; callers must set explicit metadata when needed.

### Test Signals
`MkdirsOptionsTest` verifies default create-parent true, null owner/group, umask-applied mode, field setters, and equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/MkdirsOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/OpenOptions.java -->
## sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/OpenOptions.java

### Purpose
`OpenOptions` carries read-open parameters for UFS files.

### Important APIs, Types, And Functions
Defaults are offset zero, length `Long.MAX_VALUE`, recover-failed-open false, and position-short false. Getters and fluent setters expose offset, maximum length, recovery behavior, and small positioned-read hint. Equality, hash code, and `toString` include all fields.

### Control Flow
`BaseUnderFileSystem.open(path)` uses defaults. `ObjectUnderFileSystem.open` passes the options plus a one-attempt retry policy to `openObject`; `openExistingFile` passes the full eventual-consistency retry policy.

### State And Persistence
Mutable in-memory option only. No persistence.

### Dependencies And Integration Points
Used by UFS implementations to select range reads, retry open behavior, and optimize positioned reads.

### Risks
No local validation for negative offsets or lengths. The `positionShort` hint must not alter correctness for normal reads.

### Test Signals
`OpenOptionsTest` verifies default offset, setter behavior for offset, and equality. It does not test length, recovery, or position-short flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/main/java/alluxio/underfs/options/OpenOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/FingerprintTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/FingerprintTest.java

### Purpose
`FingerprintTest` validates serialization, parsing, matching, ACL inclusion, and string sanitization for the `Fingerprint` class using UFS status objects.

### Important APIs, Types, And Functions
Tests call `Fingerprint.create`, `serialize`, `parse`, `matchMetadata`, `matchContent`, `getTag`, and `sanitizeString`. They create both `UfsFileStatus` and `UfsDirectoryStatus` instances and an `AccessControlList`.

### Control Flow
The parse tests create file, directory, and invalid fingerprints, serialize them, parse them back, and compare serialization. Matching creates baseline, metadata-changed, and content-hash-changed file statuses and asserts metadata/content comparisons. ACL testing serializes an ACL-bearing fingerprint and checks parsed ACL tag text.

### State And Persistence
All state is random in-memory test data. No filesystem state is used.

### Dependencies And Integration Points
Provides regression coverage for UFS status fields as they feed Alluxio metadata fingerprints, including optional ACL data and content-hash override.

### Risks
Random values can make failures harder to reproduce without seeded output. The test does not cover xattrs, block size comparison, or malformed serialized fingerprints beyond invalid status creation.

### Test Signals
Strong signal for stable fingerprint round-tripping, metadata-vs-content matching semantics, ACL tag formatting, and sanitization of spaces/pipes into underscores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/FingerprintTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/MockObjectUnderFileSystem.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/MockObjectUnderFileSystem.java

### Purpose
`MockObjectUnderFileSystem` is a minimal concrete subclass of `ObjectUnderFileSystem` for unit tests.

### Important APIs, Types, And Functions
It implements all abstract object-store hooks with inert return values: false, null, or no-op. `setMode` and `setOwner` are no-ops.

### Control Flow
The class does not model storage. Tests subclass or Mockito selected methods when they need behavior.

### State And Persistence
Only inherited state exists. No object data is persisted.

### Dependencies And Integration Points
Used by `ObjectUnderFileSystemTest` to access protected retry behavior and to override listing/status methods for async listing tests.

### Risks
Because many methods return null, using it without overriding required hooks can produce null pointer failures unrelated to production behavior.

### Test Signals
It is a fixture, not an assertion-bearing test. Its usefulness is enabling focused tests of superclass logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/MockObjectUnderFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/ObjectUnderFileSystemTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/ObjectUnderFileSystemTest.java

### Purpose
`ObjectUnderFileSystemTest` checks selected superclass behavior for object UFS implementations.

### Important APIs, Types, And Functions
`testRetryOnException` directly exercises protected `retryOnException` using a mocked `ObjectStoreOperation`. `testListObjectStorageDescendantTypeNone` builds an anonymous object UFS overriding status/listing methods and calls `UnderFileSystemTestUtil.performListingAsyncAndGetResult`.

### Control Flow
The retry test configures max retries to 20, verifies a `SocketException` is retried and succeeds, then verifies `FileNotFoundException` is thrown without broad retry. The async listing test sets two child file statuses under `root`, requests `DescendantType.NONE`, and expects one item representing the base path.

### State And Persistence
Uses configuration rule state and in-memory mock/anonymous classes. No real object store.

### Dependencies And Integration Points
Depends on Mockito, JUnit, `ConfigurationRule`, `DescendantType`, `ListOptions`, and `UnderFileSystemTestUtil`.

### Risks
Coverage is narrow. It does not cover delete/rename batching, directory marker creation, chunk iteration, or recursive object listing. Anonymous overrides bypass much real superclass listing code.

### Test Signals
Useful signal for retry exception classification and metadata-sync behavior for object-store `DescendantType.NONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/ObjectUnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsDirectoryStatusTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsDirectoryStatusTest.java

### Purpose
Tests the basic `UfsDirectoryStatus` metadata contract.

### Important APIs, Types, And Functions
The tests construct `UfsDirectoryStatus`, call name, type, owner, group, and mode getters, and exercise the copy constructor.

### Control Flow
`fields` verifies fixed values. `copy` constructs a copy and asserts equality.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Validates the directory status variant used by UFS listing and status APIs.

### Risks
Does not test last-modified time, xattrs, `copy()`, `toString`, or `setName`.

### Test Signals
Confirms directory instances report `isDirectory=true`, `isFile=false`, and preserve permission metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsDirectoryStatusTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsFileStatusTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsFileStatusTest.java

### Purpose
Tests the basic `UfsFileStatus` metadata contract.

### Important APIs, Types, And Functions
The tests construct `UfsFileStatus`, call content hash, content length, type, last-modified, owner, group, mode, block-size, and name getters, and exercise the copy constructor.

### Control Flow
`fields` verifies a randomly generated status. `copy` creates a copy and asserts equality.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Validates the file status variant used by file status APIs, listings, and fingerprint tests.

### Risks
Random inputs are unseeded. Equality assertions do not detect missing content fields because base equality excludes them.

### Test Signals
Confirms file instances report `isDirectory=false`, `isFile=true`, and preserve primary file metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UfsFileStatusTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemConfigurationTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemConfigurationTest.java

### Purpose
Tests UFS configuration precedence, read-only preservation, and mount-specific configuration isolation.

### Important APIs, Types, And Functions
Exercises `UnderFileSystemConfiguration.defaults`, constructor, `createMountSpecificConf`, `getMountSpecificConf`, `get`, `getInt`, `isSet`, and `isReadOnly`.

### Control Flow
Tests set and unset S3 keys and listing length in copied/modifiable configurations. They verify global values are visible, mount-specific values override globals or fill missing keys, read-only survives cloning, repeated mount-specific creation does not accumulate prior mount options, and the base configuration remains without mount-specific values.

### State And Persistence
Uses `ConfigurationRule` and copied global configuration in memory. No persistence.

### Dependencies And Integration Points
Provides regression coverage for mount table option propagation into UFS factories and implementations.

### Risks
The first test constructs a config from `Configuration.global()` while setting `mConfiguration`, which relies on global/test configuration behavior. It does not test `toUserPropertyMap`, source labeling for multiple properties, or validation.

### Test Signals
Strong signal that mount options have higher precedence than global config and that option merging is non-mutating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemConfigurationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTest.java

### Purpose
Tests UFS factory discovery boundaries in the core module.

### Important APIs, Types, And Functions
Calls `UnderFileSystemFactoryRegistry.find` for local and external-module schemes. Uses JUnit `Assume` to run external-factory checks only when the core classpath has exactly one available implementation.

### Control Flow
`coreFactory` asserts local paths and `file://` paths do not resolve to a core UFS factory. `externalFactory` asserts HDFS, OSS, S3, S3A, and GlusterFS paths do not resolve without their separate modules.

### State And Persistence
Reads static registry state only.

### Dependencies And Integration Points
Guards extension split behavior: core common should not accidentally provide factories for schemes owned by external modules.

### Risks
Classpaths with additional factories skip the external test via `Assume`, reducing coverage in integrated builds.

### Test Signals
Useful signal for service-loader packaging and module boundary regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTestUtil.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTestUtil.java

### Purpose
`UnderFileSystemTestUtil` contains helper methods for UFS unit tests.

### Important APIs, Types, And Functions
`performListingAsyncAndGetResult` invokes `UnderFileSystem.performListingAsync` and waits for completion using a `CountDownLatch`, storing either result or error in `AtomicReference`s.

### Control Flow
The helper calls `performListingAsync` with null continuation/start-after, `checkStatus` set to true only for `DescendantType.NONE`, and callbacks that set result/error then count down. After `await`, it throws any callback error or returns the result.

### State And Persistence
Uses transient synchronization primitives only.

### Dependencies And Integration Points
Used by async listing tests to make callback APIs testable in synchronous JUnit methods.

### Risks
There is no timeout, so a broken async implementation that never calls back will hang the test. It does not close streams from the returned result.

### Test Signals
Supports concise tests for async metadata sync behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/UnderFileSystemTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/CreateOptionsTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/CreateOptionsTest.java

### Purpose
Tests defaults, security interaction, setters, and equality for `CreateOptions`.

### Important APIs, Types, And Functions
Uses `CreateOptions.defaults`, getters/setters, `ModeUtils.applyFileUMask`, and Guava `EqualsTester`.

### Control Flow
Default tests verify create-parent false, ensure-atomic false, null owner/group, and umask-applied file mode. Security-enabled test configures simple auth and group mapping but expects the same null owner/group default. Field test sets randomized values and checks getters.

### State And Persistence
Mutates modifiable global configuration in test setup; no filesystem persistence.

### Dependencies And Integration Points
Protects the option defaults consumed by UFS create operations.

### Risks
Does not test ACL setter or `toString`/hash code explicitly beyond equality.

### Test Signals
Confirms file create options do not implicitly choose owner/group, even with security enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/CreateOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/DeleteOptionsTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/DeleteOptionsTest.java

### Purpose
Tests `DeleteOptions` default and setter behavior.

### Important APIs, Types, And Functions
Uses `DeleteOptions.defaults`, `isRecursive`, `setRecursive`, and `CommonUtils.testEquals`.

### Control Flow
The default test expects recursive false. The fields test toggles false and true and checks each value.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects delete-directory semantics for UFS operations.

### Risks
No negative or concurrency concerns; coverage is intentionally narrow.

### Test Signals
Confirms non-recursive delete is the default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/DeleteOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/FileLocationOptionsTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/FileLocationOptionsTest.java

### Purpose
Tests `FileLocationOptions` offset behavior.

### Important APIs, Types, And Functions
Uses `FileLocationOptions.defaults`, `getOffset`, `setOffset`, and equality helper.

### Control Flow
Default offset is asserted as zero. The fields test iterates several positive offsets and checks each value.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects option behavior used by UFS file-location APIs.

### Risks
Does not test negative or very large offsets.

### Test Signals
Confirms offset defaults and mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/FileLocationOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/ListOptionsTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/ListOptionsTest.java

### Purpose
Tests `ListOptions` recursive flag behavior.

### Important APIs, Types, And Functions
Uses `ListOptions.defaults`, `isRecursive`, `setRecursive`, and equality helper.

### Control Flow
Default recursive false is asserted, then the flag is set to false and true and checked.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects listing behavior used by metadata sync and recursive operations.

### Risks
No coverage for interactions with actual listing implementations.

### Test Signals
Confirms non-recursive listing is the default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/ListOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/MkdirsOptionsTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/MkdirsOptionsTest.java

### Purpose
Tests defaults, security interaction, setters, and equality for `MkdirsOptions`.

### Important APIs, Types, And Functions
Uses `MkdirsOptions.defaults`, getters/setters, `ModeUtils.applyDirectoryUMask`, and Guava `EqualsTester`.

### Control Flow
Default tests verify create-parent true, null owner/group, and umask-applied directory mode. Security-enabled test configures a copied conf but calls defaults with the global configuration, still expecting null owner/group and default mode. Field test sets randomized create-parent, owner, group, and mode.

### State And Persistence
In-memory configuration and option state only.

### Dependencies And Integration Points
Protects mkdir option defaults consumed by UFS directory creation.

### Risks
The security-enabled test creates `conf` but passes `mConfiguration`, so it mostly verifies defaults rather than the configured object. No coverage for `toString` beyond equality.

### Test Signals
Confirms recursive parent creation is the default for mkdirs and security does not implicitly fill owner/group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/MkdirsOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/OpenOptionsTest.java -->
## sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/OpenOptionsTest.java

### Purpose
Tests selected `OpenOptions` behavior.

### Important APIs, Types, And Functions
Uses `OpenOptions.defaults`, `getOffset`, `setOffset`, and equality helper.

### Control Flow
Default offset is asserted as zero. Several offsets are set and verified.

### State And Persistence
In-memory only.

### Dependencies And Integration Points
Protects defaults used by `UnderFileSystem.open`.

### Risks
It does not verify length default, recover-failed-open flag, position-short flag, negative values, or string output.

### Test Signals
Confirms offset defaults and mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/common/src/test/java/alluxio/underfs/options/OpenOptionsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/pom.xml -->
## sources/distributed-fs/alluxio/core/server/common/pom.xml

### Purpose
This Maven module descriptor defines `alluxio-core-server-common`, the shared server-side utility jar for Alluxio core services.

### Important APIs, Types, And Functions
The artifact inherits from `alluxio-core-server`, packages as `jar`, names the module "Alluxio Core - Server - Common Utilities", defines `build.path`, and pins `alluxio.ratis.version` to `2.4.1`.

### Control Flow
Maven uses this file to resolve dependencies and build/test the module. There is no runtime control flow.

### State And Persistence
Build state is Maven artifact metadata and dependency resolution. No application persistence.

### Dependencies And Integration Points
External dependencies include Kryo, Apache Ratis server/grpc, Atomix Catalyst transport, Jackson, Guava, JAXB runtime, Commons CLI/Lang/Compress, Dropwizard metrics, Prometheus clients, Servlet/JAX-RS APIs, Curator, Jetty, protobuf Jackson datatype, and LZ4. Internal dependencies are `alluxio-core-common`, `alluxio-core-transport`, and the core-common test jar for tests.

### Risks
Server common is a dependency-heavy module; version drift in Ratis, Jackson, Jetty, or metrics libraries can affect masters/workers. The Catalyst dependency is explicitly marked with a TODO for removal. Runtime JAXB is required by AWS SDK paths.

### Test Signals
Maven compilation and module tests validate dependency compatibility. The listed Java utilities depend on these declared internal/external libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/DefaultStorageTierAssoc.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/DefaultStorageTierAssoc.java

### Purpose
`DefaultStorageTierAssoc` implements `StorageTierAssoc` by mapping storage tier aliases to ordinal positions and back.

### Important APIs, Types, And Functions
Constructors build an immutable bidirectional map either from configuration level/template keys or an explicit ordered alias list. `interpretOrdinal` clamps positive ordinals to the last tier and negative ordinals relative to the bottom tier. Public methods are `getAlias`, `getOrdinal`, `size`, `getOrderedStorageAliases`, and `intersectionList`.

### Control Flow
Config construction reads the number of levels and each alias from `Configuration`. Alias lookup interprets the ordinal then uses the inverse bimap. `intersectionList` creates adjacent tier pairs from top to bottom using `BlockStoreLocation.anyDirInTier`.

### State And Persistence
State is an immutable bimap; no persistence. Thread-safety relies on immutability.

### Dependencies And Integration Points
Used by worker/master storage-tier logic to reason about tier hierarchy and move intersections. Depends on `Configuration`, `PropertyKey.Template`, Guava `ImmutableBiMap`, and `BlockStoreLocation`.

### Risks
Duplicate aliases cause bimap build failures. `getOrdinal` will unbox a null value if alias is unknown, causing a null pointer exception. Empty alias lists would make ordinal interpretation invalid.

### Test Signals
No direct test in this subset, but storage tier scheduling and movement tests should cover ordered aliases and intersections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/DefaultStorageTierAssoc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Process.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Process.java

### Purpose
`Process` is the common lifecycle interface for Alluxio processes.

### Important APIs, Types, And Functions
It declares `start`, `stop`, and `waitForReady(int timeoutMs)`.

### Control Flow
Implementations start and block until stopped, stop synchronously, and report readiness within a timeout. `ProcessUtils.run` and shutdown hooks use this contract.

### State And Persistence
No state in the interface. Implementations hold process services, threads, ports, and persisted state.

### Dependencies And Integration Points
Used by master, worker, and other daemon entry points through `ProcessUtils`.

### Risks
`start` is expected to block; implementations that return early alter process main behavior. `waitForReady` has a TODO to replace it with serving-state semantics.

### Test Signals
No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Process.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/ProcessUtils.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/ProcessUtils.java

### Purpose
`ProcessUtils` contains daemon lifecycle helpers for running processes, fatal exits, shutdown hooks, and diagnostic dumps on exit or failover.

### Important APIs, Types, And Functions
`run(Process)` logs environment/version, starts the process, dumps diagnostics, and exits 0; on uncaught throwable it tries to stop the process, dumps diagnostics, and exits -1. `fatalError` logs or throws in test mode, dumps diagnostics, and exits. `stopProcessOnShutdown` adds a shutdown hook. `dumpInformationOnExit` and `dumpInformationOnFailover` write metrics and thread stacks. Private `dumpMetrics` and `dumpStacks` write timestamped files.

### Control Flow
Exit dumping only runs for process types in `COLLECT_ON_EXIT` (`MASTER`, `WORKER`) and when config enables it. A synchronized `sInfoDumpOnExitCheck` prevents duplicate exit dumps. Failover dump is asynchronous and returns futures, with metrics submitted before stacks to race less with shutdown.

### State And Persistence
Static state includes `COLLECT_ON_EXIT`, `sInfoDumpOnExitCheck`, and a date formatter. Persistent side effects are JSON metrics files and text stack dump files under `LOGS_DIR`.

### Dependencies And Integration Points
Depends on Alluxio configuration, metrics servlet object mapper, metrics registry, runtime constants, `CommonUtils.PROCESS_TYPE`, thread utilities, Guava `Throwables`, and Java executors. Used by server `main` methods and failover handling.

### Risks
The methods call `System.exit`, so tests must set `TEST_MODE` where fatal paths are exercised. Diagnostic dumping can fail due to log directory permissions or serialization issues. Shutdown hook and normal exit paths can race; the synchronized guard only protects exit dump, not process stop.

### Test Signals
No direct tests in this subset. Integration tests around daemon startup/shutdown and failover diagnostics are the likely coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/ProcessUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Registry.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Registry.java

### Purpose
`Registry` manages `Server` instances inside an Alluxio process, including lookup, dependency-ordered start, reverse-order stop, and close.

### Important APIs, Types, And Functions
The registry maps server classes to instances under a `ReentrantLock`. Public methods are `get`, `get` with timeout, `add`, `getServers`, `start`, `stop`, and `close`. Private `getTransitiveDeps` computes dependencies, and `DependencyComparator` orders servers.

### Control Flow
`get` waits up to a timeout for a server class to appear, then type-checks and casts it. `getServers` sorts registered servers: if left depends on right, left compares after right; if right depends on left, left compares before right; otherwise names determine order. `start` starts in sorted dependency order and stops already-started servers if a later start throws. `stop` and `close` traverse the reverse order.

### State And Persistence
State is an in-memory registry map and lock. No persistence.

### Dependencies And Integration Points
Used by process implementations to wire master/worker internal servers. Depends on `Server`, `LockResource`, `CommonUtils.waitFor`, `WaitForOptions`, and Guava `Lists.reverse`.

### Risks
`getTransitiveDeps` reads `mRegistry` without holding `mLock` when called during sorting, so concurrent mutation can produce inconsistent ordering. Dependency cycles are detected only when a dependency path reaches the original server, not necessarily all malformed graphs. Failed start stops servers in start order, not reverse start order.

### Test Signals
No direct tests in this subset. Server lifecycle tests should cover dependency ordering and failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/Registry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RestUtils.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RestUtils.java

### Purpose
`RestUtils` centralizes REST endpoint invocation, authentication user setup, response creation, and exception-to-error-response conversion.

### Important APIs, Types, And Functions
`call(RestCallable<T>, AlluxioConfiguration, Map<String,Object>)` and overload without headers wrap endpoint logic. `RestCallable<T>` is the endpoint functional interface. `ErrorResponse` carries gRPC status code and message. Private `createResponse` handles success values, and `createErrorResponse` maps exceptions through `AlluxioStatusException`.

### Control Flow
Before invoking an endpoint, `call` sets `AuthenticatedClientUser` from `ServerUserState.global()` when security is enabled and no client user is set. It returns an error response if that setup fails. It then invokes the callable, creates an OK response, or catches any exception and returns a server-error response entity.

### State And Persistence
It may set thread-local/authenticated client user state. No persistence.

### Dependencies And Integration Points
Used by Alluxio REST resources. Depends on JAX-RS `Response`, Jackson `ObjectMapper`, gRPC `Status`, security utilities, and Alluxio status exceptions.

### Risks
All endpoint exceptions produce HTTP 500 via `Response.serverError()` even though the entity carries a more specific gRPC status code. String responses are explicitly JSON-encoded but headers are not applied in the string branch. Void handling checks `object instanceof Void`, which does not catch null returns.

### Test Signals
No direct test in this subset. REST endpoint tests should check JSON string behavior, error entities, headers, and auth setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcSensitiveConfigMask.java -->
## sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcSensitiveConfigMask.java

### Purpose
`RpcSensitiveConfigMask` masks credential-bearing mount properties in RPC messages before logging or exposing them.

### Important APIs, Types, And Functions
The singleton `CREDENTIAL_FIELD_MASKER` implements `SensitiveConfigMask.maskObjects`. It handles `MountPOptions`, `MountPRequest`, `UfsInfo`, `GetUfsInfoPResponse`, and `UpdateMountPRequest`. `copyAndMaskProperties` copies non-credential properties and replaces credential values with `"Masked"`.

### Control Flow
`maskObjects` creates a new object array, pattern-matches each argument type, clones the protobuf builder, clears properties in the relevant nested `MountPOptions`, copies masked properties from the original map, and builds the sanitized message. Unrecognized arguments pass through unchanged.

### State And Persistence
Stateless aside from the singleton. It does not mutate original protobuf messages.

### Dependencies And Integration Points
Integrates with RPC logging/masking infrastructure, protobuf-generated mount messages, `CredentialPropertyKeys`, and `SensitiveConfigMask`.

### Risks
Only known message shapes are masked. New RPC messages that directly or indirectly contain `MountPOptions` require explicit additions or credentials can leak. `copyAndMaskProperties` uses raw `Entry` types, losing generic type safety.

### Test Signals
No direct tests in this subset. Logging tests should verify each supported message type masks all keys in `CredentialPropertyKeys.getCredentials()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/RpcSensitiveConfigMask.java -->
