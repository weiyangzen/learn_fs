# subset-b-008118 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneFileSystem.java

## Purpose
Minimal Hadoop `FileSystem` implementation for the rooted Ozone `ofs://` scheme. It maps Hadoop filesystem calls onto Ozone volumes, buckets, keys, snapshots, trash roots, and bucket links while avoiding Hadoop 3-only extension points so it can be shared by compatibility modules.

## Important APIs, types, and functions
The class extends `FileSystem`, creates a `BasicRootedOzoneClientAdapterImpl`, and exposes `open`, `create`, `createNonRecursive`, `rename`, `delete`, `listStatus`, `getFileStatus`, `getContentSummary`, snapshot APIs, `getTrashRoot(s)`, symlink target lookup for bucket links, `setTimes`, and `setSafeModeUtil`. Helper types include `OzoneListingIterator`, `RenameIterator`, `DeleteIterator`, `DeleteIteratorWithFSO`, `DeleteIteratorFactory`, and `OzoneFileStatusIterator`. Conversion is mediated by `FileStatusAdapter`.

## Control flow
`initialize` validates `ofs://authority`, parses OM host/service id and port, builds a canonical URI, determines hsync and datastream settings, creates the adapter, and sets `/user/<shortUser>` as working directory. Read/write methods convert `Path` to Ozone key strings and wrap adapter streams in Hadoop `FSData*Stream`. Rename and delete first classify the `OFSPath` as root, volume, bucket, file, directory, link bucket, or FSO bucket, then either call single adapter operations or iterate prefixed key batches. Listing repeatedly calls adapter `listStatus` with a start key, deduplicating the first element of later pages.

## State and persistence behavior
Local mutable state is configuration-derived: URI, user name, working directory, listing page size, hsync flag, datastream flag, and streaming threshold. Durable mutations happen through the adapter: key create/delete/rename, fake directory marker creation, volume and bucket deletion, snapshot create/rename/delete, and file mtime/atime updates. Recursive content summary performs live tree traversal rather than caching. Fake parent directories are recreated after deletes or renames when object-store directory markers would otherwise disappear.

## Dependencies and integration points
This is the main Hadoop API bridge for OFS. It depends on `OFSPath`, `OzoneFSUtils`, `OzoneClientAdapter`, Ozone OM exceptions and bucket metadata, OpenTelemetry tracing, Hadoop `FileSystem` statistics, Hadoop snapshot/trash/symlink contracts, and Ozone configuration keys for listing and streaming. Full Hadoop 3 subclasses override hooks for storage statistics, token issuers, stream capabilities, and lease recovery.

## Risks and edge cases
Risk concentrates in path classification and recursive iteration. Cross-bucket rename is rejected, root deletion is refused, recursive volume delete is intentionally unsupported, nonrecursive nonempty directory deletion throws, and FSO buckets use different delete/rename paths. Link buckets have POSIX-like trailing slash behavior that determines whether the link or target contents are deleted. Listing pagination depends on `startPath` and duplicate suppression. `pathToKey` rejects invalid names and special-cases `/NONE` in status and setTimes for DistCp. Datastream auto-selection changes stream implementation after a byte threshold, so hsync/capability behavior must remain aligned.

## Test signals
Direct unit coverage in this work item checks default block size, OFS symlink support, snapshot return paths, and OFS path parsing. Broader expected signals come from Hadoop filesystem contract tests, snapshot/trash behavior, link bucket behavior, recursive delete/rename integration tests, stream capability tests, and storage statistics checks in Hadoop 3 modules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSDataStreamOutput.java

## Purpose
Hadoop 3-capable wrapper for Ozone datastream output. It adds `StreamCapabilities` to `OzoneFSDataStreamOutput` while keeping the base stream usable in Hadoop 2 modules that cannot reference the capability interface.

## Important APIs, types, and functions
The constructor accepts an existing `OzoneFSDataStreamOutput` and hsync-enabled flag, reuses the wrapped `ByteBufferStreamOutput`, and implements `hasCapability`. Capability checks are meaningful only when the wrapped stream is a `KeyDataStreamOutput`; `hflush` and `hsync` report true only when hsync is enabled.

## Control flow
`hasCapability` lowercases the requested capability and delegates to `hasWrappedCapability`. Unknown capabilities, non-key datastream implementations, and disabled hsync all return false.

## State and persistence behavior
The only state is the boolean hsync capability flag. Durable writes and flushes are handled by the inherited datastream wrapper and underlying Ozone client stream.

## Dependencies and integration points
Used by Hadoop 3/full `OzoneFileSystem` and `RootedOzoneFileSystem` hooks when datastream output is selected by the filesystem threshold logic. It depends on Hadoop `StreamCapabilities`, HDDS `ByteBufferStreamOutput`, Ozone `KeyDataStreamOutput`, and Hadoop `StringUtils`.

## Risks and test signals
The main risk is a mismatch between advertised hsync/hflush support and actual stream behavior, especially if new datastream output classes are introduced. Stream capability assertions should cover both enabled and disabled hsync and datastream vs non-datastream wrapped outputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSDataStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSInputStream.java

## Purpose
Hadoop 3 input stream wrapper that advertises Ozone FS read capabilities. It keeps base read behavior in `OzoneFSInputStream` and only adds `StreamCapabilities`.

## Important APIs, types, and functions
The class is package-private and final. `hasCapability` reports support for `READBYTEBUFFER`, `UNBUFFER`, and `PREADBYTEBUFFER`; all other capabilities return false after lowercasing.

## Control flow
Construction passes the wrapped `InputStream` and `FileSystem.Statistics` to the parent. Runtime operations are inherited from `OzoneFSInputStream`; capability checks are local string switches.

## State and persistence behavior
No additional state exists. Reads, seeks, positioned reads, unbuffer, and byte counters are handled by the parent and underlying stream.

## Dependencies and integration points
Created by Hadoop 3/full filesystem subclasses from `createFSInputStream`. It integrates with clients such as `FSDataInputStream.hasCapability`, Hadoop vector/read-buffer APIs, and Ozone key input streams.

## Risks and test signals
The advertised capabilities assume the parent can satisfy byte-buffer and positioned byte-buffer reads for all wrapped inputs. Tests in `TestOzoneFSInputStream` check `READBYTEBUFFER`; additional coverage should include unbuffer and positioned byte-buffer behavior for direct and heap buffers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSOutputStream.java

## Purpose
Hadoop 3 output stream wrapper that advertises hflush/hsync support for normal Ozone key output streams and deliberately avoids advertising it for EC streams.

## Important APIs, types, and functions
The class extends `OzoneFSOutputStream` and implements `StreamCapabilities`. It unwraps `CryptoOutputStream` before checking the real output stream. `KeyOutputStream` supports `HFLUSH` and `HSYNC` only when hsync is enabled; `ECKeyOutputStream` returns false.

## Control flow
`hasCapability` pulls the `OzoneOutputStream`'s underlying `OutputStream`, unwraps encryption if present, then applies type-specific capability rules. Unknown stream types fall back to `StoreImplementationUtils.hasCapability`.

## State and persistence behavior
Only the hsync-enabled flag is held locally. Persistence and sync semantics remain delegated to the inherited wrapper and Ozone output stream.

## Dependencies and integration points
Used by full Hadoop 3 filesystems. It integrates with encrypted buckets, EC buckets, Hadoop stream capability probing, and the `OzoneFSUtils.canEnableHsync` configuration gate from base filesystem initialization.

## Risks and test signals
The largest risk is over-advertising sync support on EC or encrypted streams. Tests should validate capability results for plain replicated, encrypted replicated, EC, and disabled hsync cases, and should confirm that advertised hsync calls succeed end to end.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/CapableOzoneFSOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Constants.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Constants.java

## Purpose
Small constants holder for Ozone filesystem implementation defaults and configuration keys shared across compatibility modules.

## Important APIs, types, and functions
It defines `OZONE_DEFAULT_USER`, `OZONE_USER_DIR`, `BUFFER_DIR_KEY`, `BUFFER_TMP_KEY`, and `LISTING_PAGE_SIZE`. The private constructor prevents instantiation.

## Control flow
There is no runtime control flow. Consumers statically import or reference constants.

## State and persistence behavior
No state is stored. Constants influence working-directory defaults and buffer/listing behavior elsewhere.

## Dependencies and integration points
`BasicRootedOzoneFileSystem` uses the default user and `/user` root when initializing home/working directories. Other Ozone FS code may use buffer keys for local temporary write buffering.

## Risks and test signals
Changing constant values can alter default home directories or listing/buffer defaults globally. Tests that assert working directory, home directory, and default listing behavior would catch accidental contract changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Constants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/FileStatusAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/FileStatusAdapter.java

## Purpose
Compatibility data carrier for file status metadata that can be converted into Hadoop 2 or Hadoop 3 `FileStatus` constructors by platform-specific filesystem classes.

## Important APIs, types, and functions
The final class stores length, disk consumed, path, directory flag, replication, block size, modification/access times, permission bits, owner, group, symlink, block locations, encryption flag, and EC flag. It exposes getters, `isFile`, `isDir`, `getBlockLocations`, and a diagnostic `toString`.

## Control flow
Construction copies the supplied `BlockLocation[]` into an internal list. Consumers call getters and filesystem-specific `constructFileStatus` methods to build Hadoop-native status objects.

## State and persistence behavior
Instances are immutable except the internal list reference is private and only exposed as copied arrays. It represents live OM metadata but does not persist anything itself.

## Dependencies and integration points
Produced by `OzoneClientAdapter.listStatus` and `getFileStatus`, then consumed by `BasicRootedOzoneFileSystem`, `BasicOzoneFileSystem`, and Hadoop 2/3 status constructors. It carries block locations for `LocatedFileStatus` conversion and encryption/EC flags where supported.

## Risks and test signals
Constructor parameter ordering is long and error-prone. Risks include dropping block locations, losing symlink/encryption/EC metadata in Hadoop 2 conversions, or stale disk consumed values affecting content summaries. Listing, getFileStatus, and content summary tests should verify every field that downstream contracts rely on.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/FileStatusAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/LeaseRecoveryClientDNHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/LeaseRecoveryClientDNHandler.java

## Purpose
Client-side lease recovery helper that contacts datanodes through the adapter to determine actual block lengths before committing OM recovery metadata.

## Important APIs, types, and functions
The static `getOmKeyLocationInfos` method accepts `LeaseKeyInfo`, `OzoneClientAdapter`, and a force-recovery flag. It compares finalized key locations with open-key locations, calls `adapter.finalizeBlock`, updates block lengths, and returns the recovered location list.

## Control flow
The method handles three cases: open file table has an extra final block, open penultimate block length differs from file table final block with matching local ID, or open and closed tables have the same block count. On datanode `NO_SUCH_BLOCK` or `CONTAINER_NOT_FOUND`, it retries the file-table final block when that aligns with the open penultimate block. Other failures are thrown unless force recovery is enabled.

## State and persistence behavior
The method mutates `OmKeyLocationInfo` lengths in memory and may append an open final block to the file-table list. Durable recovery occurs later when filesystem code builds `OmKeyArgs` and calls `adapter.recoverFile`.

## Dependencies and integration points
Used by Hadoop 3/main and rooted lease recovery implementations. It depends on OM lease metadata, HDDS `StorageContainerException` result codes, datanode block finalization via `OzoneClientAdapter`, and `FORCE_LEASE_RECOVERY_ENV`.

## Risks and test signals
The logic is sensitive to block list ordering and local ID comparisons. Incorrect fallback can commit wrong file length or skip a valid final block. Tests should cover one-block files, extra open final blocks, mismatched penultimate lengths, missing containers, no-such-block, and forced vs strict recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/LeaseRecoveryClientDNHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/O3fsDtFetcher.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/O3fsDtFetcher.java

## Purpose
Delegation-token fetcher for the `hadoop dtutil` command and the `o3fs` URL scheme.

## Important APIs, types, and functions
Implements Hadoop `DtFetcher`. `getServiceName` returns the Ozone URI scheme, `isTokenRequired` mirrors Hadoop security state, and `addDelegationTokens` creates a `FileSystem`, fetches a delegation token, adds it to `Credentials`, and returns it.

## Control flow
If the supplied URL lacks the `o3fs` prefix, it prepends `o3fs://`. It then opens the filesystem for that URI, calls `getDelegationToken(renewer)`, fails with `IOException` if no token is returned, and stores the token under its service.

## State and persistence behavior
No local state is persisted. The observable mutation is adding the token to the provided credentials object.

## Dependencies and integration points
Integrates Hadoop security, `FileSystem.get`, `Credentials`, `Token`, and Ozone delegation token implementation. It is service-loaded by Hadoop tooling rather than called by filesystem paths directly.

## Risks and test signals
Bad URL normalization or null token handling would break secure job submission and dtutil workflows. Tests should exercise prefixed and unprefixed URLs, secure vs insecure mode, token insertion, and failure when the filesystem returns null.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/O3fsDtFetcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapter.java

## Purpose
Narrow adapter interface between Hadoop filesystem classes and Ozone client/OM APIs. It stabilizes the signatures shared across Hadoop compatibility modules and classloaders.

## Important APIs, types, and functions
The interface covers lifecycle, read/create stream operations, rename, directory create, single and batched deletes, key iteration, status listing, delegation tokens, server defaults, encryption key providers, canonical service name, replication, checksums, snapshots, snapshot diffs, lease recovery, block finalization, timestamps, file-closed checks, and safe mode.

## Control flow
Implementations translate Hadoop-oriented path strings and metadata requests into Ozone object store, volume, bucket, key, and OM protocol operations. Filesystem classes treat this interface as the only mutation/query surface.

## State and persistence behavior
The interface itself has no state. Its methods drive all persistent Ozone filesystem mutations: key data, directory markers, metadata, snapshots, recovery commits, and safe mode transitions.

## Dependencies and integration points
It references only the necessary Hadoop and Ozone types: streams, `FileStatusAdapter`, `BasicKeyInfo`, tokens, `OzoneFsServerDefaults`, `LeaseKeyInfo`, `OmKeyArgs`, `OmKeyLocationInfo`, and `SnapshotDiffReport`. Implementations in this subset add storage statistic forwarding.

## Risks and test signals
Because all filesystem behavior funnels through this API, signature changes have cross-module impact. Tests should verify adapter implementations preserve semantics for recursive operations, snapshot paths, token renewal, lease recovery, and capability-dependent stream creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapterImpl.java

## Purpose
Full-featured adapter implementation for bucket-scoped `o3fs://` filesystems that adds storage statistic accounting to `BasicOzoneClientAdapterImpl`.

## Important APIs, types, and functions
It provides constructors for default configuration, `OzoneConfiguration`, or explicit OM host/port plus volume and bucket. It overrides protected `incrementCounter` to update `OzoneFSStorageStatistics`.

## Control flow
All functional behavior is inherited from `BasicOzoneClientAdapterImpl`; this subclass only wires a statistics object and increments it when base adapter operations call the hook.

## State and persistence behavior
The local state is an optional `OzoneFSStorageStatistics` reference. Persistent Ozone state is managed by the inherited adapter.

## Dependencies and integration points
Created by Hadoop 3/main `OzoneFileSystem` so object-store operation counters and Hadoop storage statistics reflect adapter-level operations such as objects read, created, renamed, deleted, listed, and queried.

## Risks and test signals
Risk is low but important for observability: missing statistics wiring makes `StorageStatistics` under-report work. Tests should verify counters change for file create, read, list, delete, and rename through the full filesystem.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapterImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneDelegationTokenRenewer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneDelegationTokenRenewer.java

## Purpose
Hadoop token renewer for Ozone delegation tokens.

## Important APIs, types, and functions
Extends `TokenRenewer`. `getKind` returns `OzoneTokenIdentifier.KIND_NAME`; `handleKind` matches that kind; `isManaged` returns true. `renew` and `cancel` cast the token, build an `OzoneConfiguration`, open an `OzoneClient` with the token, and call object-store token renewal/cancel APIs.

## Control flow
A static initializer activates Ozone configuration resources. Each renew/cancel operation opens a short-lived authenticated client in a try-with-resources block and delegates to OM through the object store.

## State and persistence behavior
No state is retained. Renewal extends token validity in OM security state; cancel invalidates it.

## Dependencies and integration points
Integrates Hadoop token lifecycle services, Ozone client factory, `OzoneConfiguration`, `OzoneTokenIdentifier`, and OM token management.

## Risks and test signals
Incorrect token kind handling or missing config activation would break long-running secure jobs. Tests should cover kind matching, successful renew/cancel with a mocked or mini-cluster OM, and propagation of IO failures from the object store.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneDelegationTokenRenewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSDataStreamOutput.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSDataStreamOutput.java

## Purpose
ByteBuffer-oriented output stream wrapper for Ozone datastream writes.

## Important APIs, types, and functions
Extends `ByteBufferOutputStream`, wraps `ByteBufferStreamOutput`, and implements `write(ByteBuffer,int,int)`, `flush`, `close`, `hflush`, `hsync`, and a protected accessor for capability wrappers.

## Control flow
Every operation delegates directly to the underlying datastream output. `hflush` aliases to `hsync`; `hsync` runs inside a tracing span.

## State and persistence behavior
Local state is the wrapped datastream. Data durability and block/container persistence are handled by Ozone datastream internals.

## Dependencies and integration points
Created by adapter `createStreamFile` and selected by `BasicRootedOzoneFileSystem` or `BasicOzoneFileSystem` when datastream is enabled and the selector threshold is exceeded. Hadoop 3 capability wrappers reuse the protected accessor.

## Risks and test signals
The wrapper is thin, so risks are mostly capability and lifecycle mismatches: close/flush must propagate exactly once, hsync must map to datastream sync semantics, and byte-buffer slices must be honored. Tests should write heap and direct buffers through datastream mode and verify persisted content and sync behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSDataStreamOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSInputStream.java

## Purpose
Hadoop `FSInputStream` wrapper for Ozone key input streams with byte counting, tracing, byte-buffer reads, unbuffer support, and positioned byte-buffer reads.

## Important APIs, types, and functions
Implements `ByteBufferReadable`, `CanUnbuffer`, and `ByteBufferPositionedReadable`. Key methods include single-byte and array reads, `seek`, `getPos`, `skip`, `available`, `read(ByteBuffer)`, `unbuffer`, `read(long, ByteBuffer)`, and `readFully(long, ByteBuffer)`.

## Control flow
Normal reads delegate to the wrapped input and increment Hadoop statistics. ByteBuffer reads prefer a wrapped `ByteBufferReadable`; otherwise they read via the backing array or a temporary byte array. Positioned reads prefer `ExtendedInputStream.readFully(position, buf)`; fallback saves the old position, seeks, reads via `ByteBufferReadable`, handles EOF as `-1`, and seeks back in `finally`.

## State and persistence behavior
The wrapper holds an input stream and optional statistics object. It does not cache data or persist state; it mutates the wrapped stream cursor during seek/fallback positioned reads.

## Dependencies and integration points
Used by `FSDataInputStream` from Ozone filesystem `open`. It integrates with Ozone `KeyInputStream`, Hadoop crypto streams, byte-buffer APIs, and tracing.

## Risks and test signals
Fallback `read(ByteBuffer)` uses `available()` to size reads, which can be surprising for streams where availability is not remaining length. Positioned-read fallback assumes the wrapped stream is both `Seekable` and `ByteBufferReadable`. Existing tests cover heap/direct ByteBuffer reads, EOF position preservation, capability wrapping, and crypto unbuffer forwarding; further tests should cover positioned direct-buffer reads and statistics increments.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSOutputStream.java

## Purpose
OutputStream and `Syncable` wrapper for Ozone `OzoneOutputStream`.

## Important APIs, types, and functions
Implements `write(int)`, `write(byte[],int,int)`, synchronized `flush`, synchronized `close`, `hflush`, `hsync`, and a protected `getWrappedOutputStream` accessor.

## Control flow
Writes and flush/sync operations are delegated to the Ozone stream under tracing spans. `hflush` maps to `hsync`, and `close` delegates directly.

## State and persistence behavior
The only local state is the wrapped output stream. Persistent data and metadata are created by the Ozone client stream when bytes are written, synced, and closed.

## Dependencies and integration points
Created by adapter `createFile`, wrapped in Hadoop `FSDataOutputStream`, and further wrapped by Hadoop 3 `CapableOzoneFSOutputStream`. It participates in tracing and hsync support.

## Risks and test signals
Risk is low but lifecycle-sensitive: close errors must propagate and sync capability must match the actual wrapped stream. Tests should verify write content, flush/hsync propagation, close behavior, and encrypted/EC stream handling through the capable wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSStorageStatistics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSStorageStatistics.java

## Purpose
Hadoop `StorageStatistics` implementation for Ozone filesystem operation and object counters.

## Important APIs, types, and functions
The class extends `StorageStatistics`, implements `Iterable<LongStatistic>`, initializes an `EnumMap<Statistic, AtomicLong>`, exposes `incrementCounter`, `getLongStatistics`, `getLong`, `isTracked`, `reset`, and a testing `snapshot`.

## Control flow
Construction creates a zero counter for every `Statistic`. `incrementCounter` atomically updates a counter. Iteration exposes immutable entry traversal as Hadoop long statistics.

## State and persistence behavior
All state is in-memory per filesystem instance. Counters are resettable and do not persist across process or filesystem lifecycle.

## Dependencies and integration points
Used by full Hadoop 3 filesystems and adapter implementations. It bridges `Statistic` enum symbols to Hadoop storage statistics consumers and reports the Ozone URI scheme.

## Risks and test signals
Counters can be incomplete if filesystem methods forget to call `incrementCounter` or adapter hooks are not wired. Tests should verify tracked symbols, reset behavior, iterator behavior, and counter increments across high-level filesystem and low-level object operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneFSStorageStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzonePathCapabilities.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzonePathCapabilities.java

## Purpose
Shared helper for Hadoop `hasPathCapability` implementations across `o3fs` and `ofs`.

## Important APIs, types, and functions
The static `hasPathCapability(Path,String)` validates arguments through Hadoop `PathCapabilitiesSupport` and returns true for ACLs, checksums, snapshots, and lease recovery.

## Control flow
Capability strings are normalized/validated by Hadoop support code, then matched in a switch. Unknown capabilities return false so callers can fall back to the superclass.

## State and persistence behavior
No state or persistence exists.

## Dependencies and integration points
Full Hadoop 3 `OzoneFileSystem` and `RootedOzoneFileSystem` call this before delegating to `super.hasPathCapability`. It advertises cross-filesystem Ozone features to Hadoop clients.

## Risks and test signals
The helper currently returns a boolean rather than tri-state, so false can mean either unsupported or "let superclass decide" depending on caller convention. Tests should verify every advertised capability and confirm unknown capabilities preserve expected superclass behavior in concrete filesystems.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzonePathCapabilities.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneClientAdapterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneClientAdapterImpl.java

## Purpose
Full-featured adapter implementation for rooted `ofs://` filesystems that adds storage statistics to `BasicRootedOzoneClientAdapterImpl`.

## Important APIs, types, and functions
Constructors support default configuration, explicit `OzoneConfiguration`, or OM host/port plus `ConfigurationSource`. The override of `incrementCounter` forwards counts to optional `OzoneFSStorageStatistics`.

## Control flow
All filesystem operations are inherited. This subclass only wires statistics so inherited adapter code can report object-level activity.

## State and persistence behavior
Local state is an optional statistics reference. Durable Ozone state changes happen in inherited adapter methods.

## Dependencies and integration points
Created by full Hadoop 3/main `RootedOzoneFileSystem`. It integrates rooted OFS adapter operations with Hadoop storage statistics.

## Risks and test signals
Behavioral risk is limited to observability and constructor selection. Tests should verify rooted filesystem operations increment expected object counters and that null statistics remains safe.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneClientAdapterImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Statistic.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Statistic.java

## Purpose
Defines the set of Ozone filesystem storage statistic counters and their Hadoop-visible symbols.

## Important APIs, types, and functions
Enum entries cover object operations (`objects_created`, `objects_read`, etc.) and filesystem method invocations (`op_create`, `op_open`, `op_recover_file`, `op_set_safe_mode`, and others). `fromSymbol` maps strings to enum values, while `getSymbol`, `getDescription`, and `toString` expose metadata.

## Control flow
A static map is populated at class load from all enum values. Lookups are constant-time and return null for unknown symbols.

## State and persistence behavior
The enum and symbol map are static immutable process state. Counts live in `OzoneFSStorageStatistics`, not here.

## Dependencies and integration points
Symbols reuse Hadoop `StorageStatistics.CommonStatisticNames` where available and add Ozone-specific names for object and lease/safe-mode operations. Filesystem and adapter classes increment these values.

## Risks and test signals
Changing symbols is an external compatibility break for monitoring and tests. New filesystem methods should add counters consistently. Tests should validate `fromSymbol`, uniqueness of symbols, descriptions, and stats increments for new enum values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/Statistic.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/package-info.java

## Purpose
Package-level documentation and annotations for common Ozone filesystem implementation classes.

## Important APIs, types, and functions
Declares the `org.apache.hadoop.fs.ozone` package as `InterfaceAudience.Private` and `InterfaceStability.Evolving`, indicating implementation-detail status with evolving compatibility.

## Control flow
No runtime control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Applies documentation-level API contract to common filesystem code shared by Hadoop 2, Hadoop 3, and main Ozone filesystem modules.

## Risks and test signals
No direct tests are needed. The signal is build/Javadoc/package annotation correctness and developer awareness that these classes are not stable public APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestBasicOzoneFileSystems.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestBasicOzoneFileSystems.java

## Purpose
Parameterized unit tests for shared behavior in `BasicOzoneFileSystem` and `BasicRootedOzoneFileSystem`.

## Important APIs, types, and functions
The `data` method supplies both filesystem implementations. Tests cover default block size from `OZONE_SCM_BLOCK_SIZE`, customized block size parsing, pseudo-POSIX symlink support, and snapshot return path construction. Mockito spies and mocked adapters isolate snapshot creation.

## Control flow
Each parameterized test sets an `OzoneConfiguration` or spies the filesystem, performs a single API call, and asserts common or implementation-specific results. Snapshot tests mock adapter `createSnapshot` to return a fixed name and compare the returned path under the bucket snapshot root.

## State and persistence behavior
No real Ozone state is used. State is local configuration and mocked adapter behavior.

## Dependencies and integration points
Exercises Hadoop `FileSystem` defaults, Ozone configuration storage-size parsing, `OM_SNAPSHOT_INDICATOR`, and both `o3fs` and `ofs` path formats.

## Risks and test signals
The tests guard compatibility-sensitive return values, especially snapshot path trimming and rooted-only symlink support. They do not cover actual OM snapshot creation, link bucket behavior, or initialized filesystem URIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestBasicOzoneFileSystems.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOFSPath.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOFSPath.java

## Purpose
Unit tests for `OFSPath` parsing semantics used heavily by rooted filesystem operations.

## Important APIs, types, and functions
Tests construct `OFSPath` from strings with volume, bucket, key, spaces, trailing slashes, empty input, authority, and `/tmp` mount syntax. Assertions check authority, volume, bucket, mount, key name, non-key path, mount detection, and string rendering.

## Control flow
Each test creates one or more `OFSPath` instances against an `OzoneConfiguration` and asserts parsed components. The mount test uses `OFSPath.getTempMountBucketNameOfCurrentUser` to derive the expected current-user temporary bucket name.

## State and persistence behavior
No persistent state is used. Parsing depends on current user for `/tmp` mount bucket naming.

## Dependencies and integration points
These signals support `BasicRootedOzoneFileSystem` rename/delete/trash/symlink logic because that class relies on accurate `OFSPath` classification and key/non-key split.

## Risks and test signals
Trailing slash behavior is contract-heavy: bucket paths normalize differently than key directory paths. Missing cases include snapshot paths, link buckets, invalid names, root-only paths, and authority edge cases with malformed ports.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOFSPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java

## Purpose
Unit tests for byte-buffer read behavior and capability/unbuffer integration in `OzoneFSInputStream`.

## Important APIs, types, and functions
Tests cover `read(ByteBuffer)` for heap and direct buffers, empty streams, EOF streams, `CapableOzoneFSInputStream.hasCapability`, and `CryptoInputStream.unbuffer` forwarding to a mocked `KeyInputStream`.

## Control flow
Nested loops exercise stream lengths, buffer capacities, and initial positions. Expected content is generated from random bytes and compared after the read. EOF tests ensure buffer position remains unchanged. Crypto test builds a mocked codec/decryptor and verifies one `unbuffer` call reaches the key stream.

## State and persistence behavior
All streams are in-memory byte arrays or mocks. No Ozone state is used.

## Dependencies and integration points
The test validates Hadoop byte-buffer APIs, stream capability flags, Hadoop crypto wrappers, and Ozone `KeyInputStream` unbuffer behavior that matters for cache release under encrypted reads.

## Risks and test signals
Strong signal exists for normal `read(ByteBuffer)`, EOF behavior, and unbuffer forwarding. Gaps remain for positioned byte-buffer reads, `ExtendedInputStream` fast path, statistics increments, read-only buffers, and fallback behavior when `available()` is misleading.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/package-info.java

## Purpose
Package documentation for Ozone FS contract tests.

## Important APIs, types, and functions
Declares the `org.apache.hadoop.fs.ozone` test package and labels it as Ozone FS contract tests.

## Control flow
No runtime control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Provides package-level context for unit and contract tests around common filesystem behavior.

## Risks and test signals
No direct behavioral risk. Build success confirms the package declaration remains valid.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/pom.xml

## Purpose
Maven module for Hadoop 2-compatible Ozone filesystem distribution.

## Important APIs, types, and functions
Builds artifact `ozone-filesystem-hadoop2`. Dependencies include Hadoop 2 `hadoop-common` as provided, `hadoop-hdfs-client`, `ozone-filesystem-shaded`, Ratis thirdparty misc, SLF4J, reload4j, and Ozone test-jar. Plugins compile generated sources, unpack the shaded filesystem jar into classes, run SpotBugs, copy source files into generated sources, and replace unshaded protobuf references.

## Control flow
During `generate-sources`, antrun copies `src/main/java` to `target/generated-sources/java`. During `process-sources`, replacer rewrites `com.google.protobuf` references to the Ozone shaded prefix. During `prepare-package`, the dependency plugin unpacks `ozone-filesystem-shaded`.

## State and persistence behavior
Build output is generated under `target/`; no runtime state is defined.

## Dependencies and integration points
This module packages compatibility classes that omit Hadoop 3 APIs and supplies Hadoop 2 RPC transport. It depends on the shaded common filesystem payload while avoiding conflicts with Hadoop-provided dependencies.

## Risks and test signals
Build risks include source-rewrite drift, shading mismatches, and dependency conflicts with Hadoop 2 classpaths. Signals are Maven compile/package, SpotBugs scoped to `org.apache.hadoop.fs.ozone.*`, and the Hadoop 2-specific `TestOmKeyInfoWithHadoop2`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27OmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27OmTransportFactory.java

## Purpose
Hadoop 2.7 OM transport factory that creates RPC transports with failover support.

## Important APIs, types, and functions
Implements `OmTransportFactory`. `createOmTransport` takes a `ConfigurationSource`, `UserGroupInformation`, and OM service ID, and returns a new `Hadoop27RpcTransport`.

## Control flow
No branching beyond construction. All transport behavior is delegated to `Hadoop27RpcTransport`.

## State and persistence behavior
The factory is stateless.

## Dependencies and integration points
Used where Ozone client code discovers an OM transport factory on a Hadoop 2 classpath. It bridges Ozone OM protocol abstractions to the Hadoop 2 shaded RPC implementation.

## Risks and test signals
Risk is limited to service discovery and constructor compatibility. Tests should verify client initialization with Hadoop 2 selects this factory and can submit OM requests through the returned transport.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27OmTransportFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27RpcTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27RpcTransport.java

## Purpose
Hadoop 2-compatible OM protobuf RPC transport with leader/follower failover support.

## Important APIs, types, and functions
Implements `OmTransport`. Constructor configures Hadoop protobuf RPC engine, creates `HadoopRpcOMFailoverProxyProvider`, reads follower-read and failover settings, builds `HadoopRpcOMFollowerReadFailoverProxyProvider`, and creates an `OzoneManagerProtocolPB` proxy. `submitRequest`, `getDelegationTokenService`, and `close` implement the transport API.

## Control flow
`submitRequest` sends the protobuf request with a null controller. Non-leader `ServiceException`s are converted into a generic leader-connection `IOException`; other service exceptions are converted through Hadoop protobuf helper. `close` closes the follower-read provider when present, otherwise the base failover provider.

## State and persistence behavior
Local state is the RPC proxy and failover providers. Persistent metadata changes depend on the OM request payload.

## Dependencies and integration points
This class depends on relocated Hadoop 2 IPC packages (`org.apache.hadoop.ipc_`), Ozone OM failover providers, follower-read consistency config, protobuf OM request/response types, and Ratis leader semantics.

## Risks and test signals
The main risks are exception translation losing detail, `getDelegationTokenService` returning null, and follower-read consistency defaults failing to parse. Tests should submit read and write requests through HA configurations, verify failover behavior, and exercise not-leader exceptions on Hadoop 2.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27RpcTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java

## Purpose
Hadoop 2 `AbstractFileSystem` adapter for the bucket-scoped `o3fs` scheme.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`. Constructor delegates to a new Hadoop 2-compatible `OzoneFileSystem` with scheme `o3fs` and no authority requirement. `getUriDefaultPort` returns `-1`; `finalize` closes the wrapped filesystem.

## Control flow
All FileContext operations are delegated through `DelegateToFileSystem` to `OzoneFileSystem`.

## State and persistence behavior
Local state lives in the delegate superclass. Durable state is whatever the underlying filesystem mutates.

## Dependencies and integration points
Provides FileContext API support for Hadoop 2 users of `o3fs`.

## Risks and test signals
Use of `finalize` is lifecycle-fragile and not deterministic. Tests should instantiate through FileContext and verify basic create/list/open/delete behavior and URI default port semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java

## Purpose
Minimal Hadoop 2-compatible `o3fs` filesystem implementation.

## Important APIs, types, and functions
Extends `BasicOzoneFileSystem` and overrides `constructFileStatus` to call the Hadoop 2 `FileStatus` constructor, which lacks newer encryption and erasure-coded arguments.

## Control flow
All filesystem behavior is inherited. File status conversion maps fields from `FileStatusAdapter` to the Hadoop 2 constructor.

## State and persistence behavior
No additional state is introduced. Persistent behavior is inherited from the basic filesystem and adapter.

## Dependencies and integration points
Used by Hadoop 2 `OzFs` and `FileSystem` resolution. It is intentionally missing Hadoop 3 interfaces such as `StreamCapabilities`, `LeaseRecoverable`, and `KeyProviderTokenIssuer`.

## Risks and test signals
Metadata loss for encryption/EC flags is expected because Hadoop 2 lacks those constructor fields. Tests should verify status construction remains compatible on a Hadoop 2 classpath and basic filesystem operations still work.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java

## Purpose
Hadoop 2 `AbstractFileSystem` adapter for rooted `ofs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, constructs a Hadoop 2-compatible `RootedOzoneFileSystem`, uses scheme `ofs`, returns default port `-1`, and closes the delegate in `finalize`.

## Control flow
FileContext calls delegate to the rooted filesystem instance.

## State and persistence behavior
Only delegate state is held locally; durable changes occur through the underlying filesystem.

## Dependencies and integration points
Exposes OFS to Hadoop 2 FileContext users, including volume/bucket path semantics supplied by `BasicRootedOzoneFileSystem`.

## Risks and test signals
Lifecycle close through finalization is nondeterministic. Tests should verify FileContext resolution and rooted path operations on Hadoop 2.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java

## Purpose
Minimal Hadoop 2-compatible rooted OFS implementation.

## Important APIs, types, and functions
Extends `BasicRootedOzoneFileSystem` and overrides `constructFileStatus` to use the Hadoop 2 `FileStatus` constructor without encrypted/EC fields.

## Control flow
All operations are inherited from the basic rooted filesystem; only status construction differs.

## State and persistence behavior
No additional state. Persistent state changes are inherited via Ozone adapter calls.

## Dependencies and integration points
Used by Hadoop 2 `RootedOzFs` and `FileSystem` resolution for `ofs://` paths.

## Risks and test signals
Expected metadata truncation for Hadoop 2 must not break path/list/status behavior. Tests should cover rooted status conversion, symlink-like bucket link targets where supported by base code, and basic operations on a Hadoop 2 classpath.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/package-info.java

## Purpose
Package documentation and annotations for Hadoop 2 Ozone filesystem compatibility classes.

## Important APIs, types, and functions
Marks the package private and evolving with HDDS annotations.

## Control flow
No runtime control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Documents that Hadoop 2 compatibility classes are implementation details even though they are instantiated by Hadoop filesystem service discovery.

## Risks and test signals
No direct runtime risk. Build/Javadoc validation is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/test/java/org/apache/hadoop/fs/TestOmKeyInfoWithHadoop2.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/test/java/org/apache/hadoop/fs/TestOmKeyInfoWithHadoop2.java

## Purpose
Hadoop 2 classpath smoke test for `OmKeyInfo` behavior and protobuf conversion.

## Important APIs, types, and functions
The package-private class extends `org.apache.hadoop.ozone.om.helpers.TestOmKeyInfo` without adding methods, causing the inherited test suite to run under the Hadoop 2 filesystem module.

## Control flow
JUnit discovers inherited tests from the superclass.

## State and persistence behavior
State behavior is defined by the inherited OM key info tests. This file adds no state.

## Dependencies and integration points
Validates that Ozone OM helper tests still pass when Hadoop 2 compatibility dependencies and shading are on the classpath.

## Risks and test signals
The signal is classpath compatibility rather than new behavior. Failures usually indicate dependency relocation, protobuf, or Hadoop 2 API incompatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/test/java/org/apache/hadoop/fs/TestOmKeyInfoWithHadoop2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/pom.xml

## Purpose
Maven module for Hadoop 3-compatible shaded Ozone filesystem distribution.

## Important APIs, types, and functions
Builds artifact `ozone-filesystem-hadoop3`, skips tests in this module, depends on `ozone-filesystem-shaded`, SLF4J, reload4j provided, and Hadoop common provided. The dependency plugin unpacks the shaded jar during `prepare-package`; SpotBugs analyzes `org.apache.hadoop.fs.ozone.*`.

## Control flow
Package preparation unpacks shaded filesystem classes and resources into this module's classes, while local Hadoop 3 compatibility classes compile normally.

## State and persistence behavior
Only Maven target build outputs are created.

## Dependencies and integration points
This is the Hadoop 3 distribution wrapper that exposes stream capabilities and full Hadoop 3 APIs while embedding the shaded common Ozone FS implementation.

## Risks and test signals
Risks are dependency conflicts and missing tests in the module itself. Validation relies on compile/package, dependency analysis exceptions, SpotBugs, and downstream integration tests using the produced jar.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java

## Purpose
Hadoop 3 `AbstractFileSystem` adapter for `o3fs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, delegates to a new Hadoop 3 `OzoneFileSystem`, and uses the Ozone URI scheme. `finalize` closes the delegate.

## Control flow
FileContext operations route through `DelegateToFileSystem` to the underlying full filesystem.

## State and persistence behavior
State is held by the delegate and underlying filesystem. Durable mutations are delegated.

## Dependencies and integration points
Provides FileContext support for Hadoop 3 clients and participates in Hadoop filesystem service loading.

## Risks and test signals
The missing `getUriDefaultPort` override differs from Hadoop 2 but relies on delegate defaults. Tests should verify FileContext URI resolution and lifecycle behavior on Hadoop 3.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java

## Purpose
Full Hadoop 3 bucket-scoped Ozone filesystem for `o3fs`, adding token issuer, lease recovery, safe mode, storage statistics, and stream capabilities to `BasicOzoneFileSystem`.

## Important APIs, types, and functions
Implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`. It manages `OzoneFSStorageStatistics`, creates `OzoneClientAdapterImpl`, wraps input/output/datastreams in capable wrappers, exposes key provider token issuers, implements `hasPathCapability`, `recoverLease`, `isFileClosed`, and `setSafeMode`.

## Control flow
Construction reads the `FORCE_LEASE_RECOVERY_ENV` system property. `recoverLease` prepares recovery through the adapter, treats `KEY_ALREADY_CLOSED` as success, asks `LeaseRecoveryClientDNHandler` for finalized block lengths, builds `OmKeyArgs` with summed length and recovered locations, and commits recovery through the adapter.

## State and persistence behavior
Local state is statistics and the force-recovery flag. Persistent changes include file recovery commits and safe mode actions through OM; key provider access may include external KMS token issuer integration.

## Dependencies and integration points
Connects Hadoop 3 APIs to Ozone adapters, storage statistics, lease recovery helper, OM lease metadata, encryption key providers, and path capability helper.

## Risks and test signals
Lease recovery can commit incorrect lengths if block recovery data is wrong. `isFileClosed` lacks a storage statistic increment in this Hadoop 3 variant. Tests should cover token issuers, hsync capabilities, recoverLease strict/forced paths, safe mode, and storage statistics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java

## Purpose
Hadoop 3 `AbstractFileSystem` adapter for rooted `ofs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, delegates to a new full `RootedOzoneFileSystem`, and uses scheme `ofs`. `finalize` closes the delegate.

## Control flow
All FileContext requests are delegated to the rooted filesystem.

## State and persistence behavior
State and persistence are owned by the delegate filesystem.

## Dependencies and integration points
Provides Hadoop 3 FileContext integration for OFS volume/bucket paths.

## Risks and test signals
Lifecycle finalization is nondeterministic. FileContext tests should cover initialization, URI handling, create/list/delete, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java

## Purpose
Full Hadoop 3 rooted OFS implementation with encryption token issuer support, lease recovery, safe mode, storage statistics, and stream capabilities.

## Important APIs, types, and functions
Extends `BasicRootedOzoneFileSystem` and implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`. It creates `RootedOzoneClientAdapterImpl`, wraps streams in capable wrappers, exposes key provider APIs, reports storage statistics, implements path capabilities, `recoverLease`, `isFileClosed`, and `setSafeMode`.

## Control flow
Recovery mirrors the bucket-scoped filesystem: prepare with adapter, return success if already closed, finalize block lengths through `LeaseRecoveryClientDNHandler`, build `OmKeyArgs`, then call `recoverFile`. `isFileClosed` qualifies the path and delegates to the adapter.

## State and persistence behavior
Local state is the storage statistics object and force-recovery flag. Persistent mutations occur through recovery commits and safe-mode requests to OM.

## Dependencies and integration points
Integrates rooted path translation from the base filesystem with Hadoop 3 token issuer and lease recovery APIs. It uses `RootedOzoneClientAdapterImpl`, `OzonePathCapabilities`, and the common lease-recovery helper.

## Risks and test signals
Risk mirrors `OzoneFileSystem` with additional rooted path complexity. This variant increments read operations for `isFileClosed`, unlike the `o3fs` Hadoop 3 class. Tests should cover OFS recovery paths, capability probing, stats, and key-provider token issuers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/package-info.java

## Purpose
Package documentation and annotations for Hadoop 3 Ozone filesystem compatibility classes.

## Important APIs, types, and functions
Marks `org.apache.hadoop.fs.ozone` as private and evolving.

## Control flow
No runtime control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Documents compatibility wrapper classes that are loaded by Hadoop but treated as internal implementation details.

## Risks and test signals
No direct runtime risk. Build and Javadoc/package annotation checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop3/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-shaded/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-shaded/pom.xml

## Purpose
Builds the shaded Ozone filesystem jar used by Hadoop 2 and Hadoop 3 filesystem compatibility artifacts.

## Important APIs, types, and functions
The module packages `ozone-filesystem-common` plus selected dependencies with relocations for many third-party packages. It excludes Hadoop-provided APIs, logging APIs, and selected native artifacts, uses `ServicesResourceTransformer`, unpacks Netty/Ratis native libraries, and renames native library files to match shaded prefixes.

## Control flow
The shade plugin runs during `package`, relocating `org`, `com`, `google`, `io`, `okio`, `okhttp3`, and other namespaces while excluding Hadoop/Ozone/logging/JDK-adjacent packages. The dependency plugin unpacks native dependencies during `validate`, and copy-rename runs during `generate-sources` to align native library names with relocated class names.

## State and persistence behavior
State is build output under `target/classes` and the shaded jar. Runtime persistence is not defined.

## Dependencies and integration points
This is a packaging boundary for filesystem clients that need Ozone dependencies without colliding with Hadoop distributions. It integrates with Ratis, Netty native transports/TLS, protobuf, and Maven shade relocation rules.

## Risks and test signals
The relocation pattern for `com` is intentionally broad due to a noted timeout issue, creating risk of unintended shading. Native library filtering/renaming is fragile across platform classifiers. Signals are Maven package, dependency conflict tests, client smoke tests on Linux/macOS architectures, and service loader validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-shaded/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/pom.xml

## Purpose
Main unshaded Ozone filesystem module for the current Hadoop dependency line.

## Important APIs, types, and functions
Builds artifact `ozone-filesystem`, depending on OpenTelemetry API, Hadoop common, HDDS common/config, Ozone common, Ozone filesystem common, Ratis common, and SLF4J. It disables annotation processing, builds a test jar, and lists dependencies during compile.

## Control flow
The module compiles direct filesystem classes against the main Hadoop dependency set and uses Maven jar/dependency plugins for test artifacts and dependency listing.

## State and persistence behavior
Only build outputs are created.

## Dependencies and integration points
This module provides the non-shaded full filesystem classes in `ozonefs/src/main/java`, including POSIX variants and traced Hadoop 3 APIs.

## Risks and test signals
Dependency version drift can break Hadoop API compatibility. Tests should run filesystem unit and contract suites against this artifact, especially where it differs from the shaded Hadoop 3 wrapper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java

## Purpose
Main-module `AbstractFileSystem` adapter for `o3fs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, constructs a main-module `OzoneFileSystem`, uses the Ozone URI scheme, and closes the delegate in `finalize`.

## Control flow
FileContext calls delegate to the full bucket-scoped filesystem.

## State and persistence behavior
State is delegate-owned. Durable Ozone mutations are handled by the underlying filesystem.

## Dependencies and integration points
Exposes `o3fs` through Hadoop FileContext in the main non-shaded artifact.

## Risks and test signals
Same lifecycle risk as compatibility adapters due to `finalize`. FileContext contract tests should cover this class against the main artifact.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java

## Purpose
Main unshaded full `o3fs` filesystem implementation.

## Important APIs, types, and functions
Extends `BasicOzoneFileSystem`, implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`, maintains `OzoneFSStorageStatistics`, creates `OzoneClientAdapterImpl`, wraps streams with capability classes, exposes key provider issuers, path capabilities, lease recovery, file-closed check, and safe mode.

## Control flow
The behavior matches the Hadoop 3 compatibility version: construction reads force-recovery property, recovery prepares OM lease info, handles already-closed keys, finalizes block lengths, builds `OmKeyArgs`, and commits recovery. Stream creation hooks return capable wrappers.

## State and persistence behavior
Local state is statistics and force recovery. Persistent effects include file recovery commits, safe mode toggles, and normal inherited filesystem mutations.

## Dependencies and integration points
This is the main artifact's bridge from Hadoop clients to Ozone adapter, key providers, lease recovery, and storage statistics.

## Risks and test signals
Risks are identical to the Hadoop 3 `o3fs` class, including lease recovery correctness and stats coverage. Tests should compare main and hadoop3 behavior to avoid drift.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/OzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixOzoneFileSystem.java

## Purpose
POSIX-oriented `o3fs` variant that forces create semantics compatible with clients expecting an existing inode-like file before writing.

## Important APIs, types, and functions
Extends `OzoneFileSystem` and overrides `create(Path, FsPermission, boolean, int, short, long, Progressable)`.

## Control flow
`create` calls `super.create`, immediately closes the returned stream, then calls `super.create` again and returns the second stream. This creates/closes an initial empty file before opening the actual write stream.

## State and persistence behavior
The first create persists an empty key and close metadata; the second create overwrites/reopens according to inherited create semantics. This doubles create-side effects.

## Dependencies and integration points
Used where pseudo-POSIX create behavior is configured for bucket-scoped Ozone FS.

## Risks and test signals
The double-create can produce extra metrics, extra OM operations, and failure modes if overwrite is false or the first close succeeds but the second create fails. Tests should cover overwrite true/false, failure cleanup, and observable metadata after interrupted second create.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixRootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixRootedOzoneFileSystem.java

## Purpose
POSIX-oriented rooted OFS variant with double-create behavior.

## Important APIs, types, and functions
Extends `RootedOzoneFileSystem` and overrides the standard `create` method.

## Control flow
The method creates and closes a first stream, then creates again and returns the second stream.

## State and persistence behavior
Persists an initial empty key before the real write stream. All path translation and mutation semantics come from rooted OFS.

## Dependencies and integration points
Used for POSIX-like behavior with `ofs://` volume/bucket paths.

## Risks and test signals
Same double-create risks as `PosixOzoneFileSystem`, plus rooted path classification risks. Tests should cover rooted paths, overwrite behavior, metrics, and failure after the first close.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/PosixRootedOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java

## Purpose
Main-module `AbstractFileSystem` adapter for rooted `ofs`.

## Important APIs, types, and functions
Extends `DelegateToFileSystem`, constructs `RootedOzoneFileSystem`, uses `ofs` scheme, and closes the delegate in `finalize`.

## Control flow
FileContext APIs delegate to the rooted filesystem.

## State and persistence behavior
State is delegate-owned; persistence is handled by underlying OFS.

## Dependencies and integration points
Provides FileContext integration for rooted Ozone paths in the main artifact.

## Risks and test signals
Lifecycle and URI-resolution risks mirror other `RootedOzFs` variants. FileContext tests should cover rooted operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java

## Purpose
Main unshaded full rooted OFS implementation with tracing around lease recovery and file-closed checks.

## Important APIs, types, and functions
Extends `BasicRootedOzoneFileSystem`, implements `KeyProviderTokenIssuer`, `LeaseRecoverable`, and `SafeMode`, manages storage statistics, creates `RootedOzoneClientAdapterImpl`, wraps streams with capability classes, and implements traced `recoverLease`/`isFileClosed`.

## Control flow
`recoverLease` opens an `ofs recoverLease` tracing span and delegates to `recoverLeaseTraced`, which sets the path attribute, prepares recovery, handles already-closed keys, finalizes block lengths, builds `OmKeyArgs`, and commits recovery. `isFileClosed` opens an `ofs isFileClosed` span, sets an operation attribute, increments write ops, and delegates to the adapter.

## State and persistence behavior
Local state is statistics and force-recovery flag. Persistent effects are inherited filesystem mutations, recovery commits, and safe-mode changes. File-closed checks are read-like but increment write ops in this main-module implementation.

## Dependencies and integration points
Integrates rooted filesystem behavior with OpenTelemetry tracing, key providers, lease recovery, storage statistics, and path capability helper.

## Risks and test signals
The write-op increment in `isFileClosed` may be intentional or a metrics bug compared with other variants. Tests should assert tracing attributes where supported, recovery semantics, stats deltas, and parity with `ozonefs-hadoop3` unless divergence is deliberate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/package-info.java

## Purpose
Package-level documentation for main Ozone filesystem implementation classes.

## Important APIs, types, and functions
Marks `org.apache.hadoop.fs.ozone` private and evolving.

## Control flow
No runtime control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Communicates that main filesystem classes are implementation details even though Hadoop instantiates them through service/configuration mechanisms.

## Risks and test signals
No direct runtime risk. Build and documentation generation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/pom.xml

## Purpose
Top-level Apache Ozone Maven aggregator.

## Important APIs, types, and functions
Declares artifact `ozone` with packaging `pom`, lists core modules including clients, OM, datanode, recon, ozonefs, and gateway modules, configures jar/test-jar exclusions for web/node assets, and processes remote resource bundles. Profiles add `iceberg`, shaded Ozone filesystem modules, go-offline modules, and parallel-test surefire settings.

## Control flow
Default build includes standard modules. The `build-with-ozonefs` profile activates when `skipShade` is not set and adds `ozonefs-hadoop2`, `ozonefs-hadoop3`, and `ozonefs-shaded`. Parallel test profile adjusts fork directories and system properties.

## State and persistence behavior
Defines Maven build graph and generated build outputs only.

## Dependencies and integration points
This file determines when filesystem compatibility modules and recon codegen participate in the overall Ozone build.

## Risks and test signals
Profile activation errors can omit release-critical filesystem artifacts. Parallel-test configuration changes can cause test workspace collisions. Signals are full Maven reactor builds under default, `skipShade`, go-offline, JDK 11+, and parallel-test profiles.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/pom.xml

## Purpose
Maven module for Recon jOOQ code generation support.

## Important APIs, types, and functions
Builds artifact `ozone-reconcodegen`, skips tests, and depends on Guice, Commons IO, Derby, Hadoop common, jOOQ runtime/codegen/meta, SLF4J, Spring TX, and provided JAXB API. Compiler annotation processing is disabled.

## Control flow
The module compiles code generation and schema definition classes used to create generated Recon DAO/POJO sources from programmatic schema definitions.

## State and persistence behavior
Build output is under `target`; runtime codegen creates temporary Derby databases and generated source directories when invoked.

## Dependencies and integration points
Supports the Recon module by producing jOOQ classes for schema tables. It integrates with Guice multibindings and Derby metadata.

## Risks and test signals
Tests are skipped, so regressions surface during downstream code generation or Recon compilation. Build validation should run the generator against a temp output and compile generated sources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/JooqCodeGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/JooqCodeGenerator.java

## Purpose
Command-line utility that initializes Recon schemas in an embedded Derby database and runs jOOQ code generation for DAOs and POJOs.

## Important APIs, types, and functions
`JooqCodeGenerator` is Guice-injected with all `ReconSchemaDefinition` bindings. `initializeSchema` invokes each definition. `generateSourceCode` builds jOOQ JAXB configuration for Derby, schema `RECON`, DAOs, empty catalogs, `TableNamingStrategy`, and target package `org.apache.ozone.recon.schema.generated`. `LocalDataSourceProvider` creates and cleans up a temp Derby database.

## Control flow
`main` requires an output directory, builds an injector with `ReconSchemaGenerationModule` plus local datasource bindings, initializes schema, generates source code, and cleans up the Derby directory. SQL and generation failures are logged and rethrown as initializer errors.

## State and persistence behavior
Creates a temporary Derby database under `java.io.tmpdir` with a monotonic timestamp and deletes it after generation. Generated Java sources are written to the caller-provided output directory.

## Dependencies and integration points
Integrates Guice multibindings, Derby, jOOQ codegen, schema definitions, `SqlDbUtils`, and Recon generated-source build steps.

## Risks and test signals
Cleanup is skipped if an earlier fatal error exits before the final cleanup call. Static datasource initialization logs but does not stop immediately on DB creation failure. Tests should invoke `main` with a temp output, assert generated classes/tables, and verify temp DB cleanup on success and failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/JooqCodeGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/TableNamingStrategy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/TableNamingStrategy.java

## Purpose
Custom jOOQ generator strategy that gives generated table classes distinct names from POJOs.

## Important APIs, types, and functions
Extends `DefaultGeneratorStrategy` and overrides `getJavaClassName`. For `TableDefinition` in `Mode.DEFAULT`, it converts output table names to camel case after replacing spaces, hyphens, and dots with underscores, then appends `Table`.

## Control flow
Only table default-mode definitions receive the custom suffix. All other definitions and modes delegate to the superclass.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Referenced by `JooqCodeGenerator` strategy configuration. It affects generated Recon class names and therefore downstream source imports.

## Risks and test signals
Changing the naming strategy is a source compatibility break for generated code users. Tests should generate schemas with names containing punctuation and verify table class names and POJO names do not collide.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/TableNamingStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/package-info.java

## Purpose
Package documentation for Recon code generation support.

## Important APIs, types, and functions
Documents the package as support for generating entities and DAOs.

## Control flow
No runtime control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Applies to `JooqCodeGenerator` and `TableNamingStrategy`.

## Risks and test signals
No direct runtime risk. Build/Javadoc success is sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/codegen/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ContainerSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ContainerSchemaDefinition.java

## Purpose
Programmatic Recon schema definition for unhealthy container tracking.

## Important APIs, types, and functions
Implements `ReconSchemaDefinition` as a Guice singleton. Defines `UNHEALTHY_CONTAINERS`, columns for container ID/state/timestamps/replica counts/delta/reason, primary key on `(container_id, container_state)`, check constraint over `UnHealthyContainerStates`, and composite index `idx_state_container_id`.

## Control flow
`initializeSchema` opens a datasource connection, creates a jOOQ DSL context, checks table existence through `SqlDbUtils.TABLE_EXISTS_CHECK`, and creates the table/index if missing.

## State and persistence behavior
Persists Derby/SQL table and index DDL in the target Recon schema. The class retains the datasource and last DSL context.

## Dependencies and integration points
Bound into `ReconSchemaGenerationModule` and used by `JooqCodeGenerator`. Runtime Recon code relies on the generated jOOQ artifacts and table layout for unhealthy container queries and pagination.

## Risks and test signals
The check constraint must stay aligned with enum values used by Recon. Existing databases will not be migrated by this create-if-missing path. The composite index encodes important pagination performance assumptions. Tests should verify DDL, constraints, generated classes, and query plans for state-filtered pagination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ContainerSchemaDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaDefinition.java

## Purpose
Common interface for Recon schema providers used by code generation and schema initialization.

## Important APIs, types, and functions
Declares one method, `initializeSchema()`, which executes DDL and may throw `SQLException`.

## Control flow
Implementations are invoked by `JooqCodeGenerator.initializeSchema` after Guice multibinding discovery.

## State and persistence behavior
The interface has no state. Implementations persist tables, indexes, and constraints.

## Dependencies and integration points
Implemented by container, task, utilization, stats, and schema-version definitions. New schema definitions must also be bound in `ReconSchemaGenerationModule`.

## Risks and test signals
The interface is intentionally minimal; it does not model migrations, ordering, or idempotency beyond each implementation. Tests should ensure every bound definition can run repeatedly against an existing schema.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaGenerationModule.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaGenerationModule.java

## Purpose
Guice module that registers all Recon schema definitions used by the jOOQ generator.

## Important APIs, types, and functions
Extends `AbstractModule`. In `configure`, creates a `Multibinder<ReconSchemaDefinition>` and adds bindings for `UtilizationSchemaDefinition`, `ContainerSchemaDefinition`, `ReconTaskSchemaDefinition`, `StatsSchemaDefinition`, and `SchemaVersionTableDefinition`.

## Control flow
When Guice builds the injector, all bindings contribute to the injected set consumed by `JooqCodeGenerator`.

## State and persistence behavior
No state is stored in the module. Persistence happens through bound schema definitions.

## Dependencies and integration points
This is the discovery point for codegen schema classes. New schema definitions are invisible to generation until bound here.

## Risks and test signals
Forgetting a binding silently omits tables from generated jOOQ code. Tests should assert the bound set contains every expected definition and that generated output includes each table.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconSchemaGenerationModule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconTaskSchemaDefinition.java -->
# sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconTaskSchemaDefinition.java

## Purpose
Programmatic Recon schema definition for tracking Recon task execution state.

## Important APIs, types, and functions
Implements `ReconSchemaDefinition` as a Guice singleton. Defines `RECON_TASK_STATUS` with columns `task_name`, `last_updated_timestamp`, `last_updated_seq_number`, `last_task_run_status`, and `is_current_task_running`, with primary key `task_name`.

## Control flow
`initializeSchema` obtains a connection, checks for the table, and calls `createReconTaskStatusTable` when absent. DDL is built with jOOQ `DSL.using(conn).createTableIfNotExists`.

## State and persistence behavior
Persists the task status table in the Recon SQL schema. The class holds only the datasource reference.

## Dependencies and integration points
Bound in `ReconSchemaGenerationModule` and consumed by `JooqCodeGenerator`. Runtime Recon task management depends on the generated DAO/POJO for this table.

## Risks and test signals
There is no migration path for existing tables with older columns. Integer status/running fields require consistent interpretation by task code. Tests should validate idempotent initialization, generated classes, primary key constraint, and runtime task status reads/writes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon-codegen/src/main/java/org/apache/ozone/recon/schema/ReconTaskSchemaDefinition.java -->
