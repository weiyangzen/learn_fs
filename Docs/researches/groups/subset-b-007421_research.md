# subset-b-007421 Research

Grouped research for HDFS client sources in `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReaderStrategy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReaderStrategy.java

Purpose: `ReaderStrategy` abstracts the destination of a block read so HDFS read paths can copy from `BlockReader` or cached `ByteBuffer` sources without caring whether the caller supplied a byte array or a `ByteBuffer`. The file contains the package-private interface plus `ByteArrayStrategy` and `ByteBufferStrategy`.

Important APIs/types/functions: `ReaderStrategy.readFromBlock(BlockReader)`, `readFromBlock(BlockReader,int)`, `readFromBuffer(ByteBuffer)`, `readFromBuffer(ByteBuffer,int)`, `getReadBuffer()`, and `getTargetLength()` define the strategy contract. `ByteArrayStrategy` wraps a byte array, offset, and target length. `ByteBufferStrategy` wraps a user `ByteBuffer` and records the original remaining length as the target length. Both classes receive `ReadStatistics` and `DFSClient`, although this file does not use them directly; they preserve constructor compatibility with read code that may pass statistics context.

Control flow: array reads call `BlockReader.read(byte[], offset, length)` and advance the mutable offset only for positive reads. Buffer reads duplicate the source buffer so the source position is not changed, then copy exactly the requested length for arrays. `ByteBufferStrategy.readFromBlock` duplicates the destination buffer, constrains the duplicate limit to the requested length, calls `BlockReader.read(ByteBuffer)`, and only advances the real destination position when bytes were read. `ByteBufferStrategy.readFromBuffer` bounds the copy by destination remaining, source remaining, and requested length.

State and persistence behavior: state is in-memory only. The array strategy mutates its offset. The buffer strategy mutates the caller-supplied buffer position. There is no persistence, synchronization, or cleanup. Comments explicitly say behavior is not defined under concurrent use.

Dependencies and integration points: callers include HDFS input stream and striped read code that need a common read target abstraction. It depends on `BlockReader`, `DFSClient`, `ReadStatistics`, `IOException`, and `ByteBuffer`.

Risks: `ByteArrayStrategy.readFromBuffer(src, length)` assumes `length <= src.remaining()` and that the destination has enough room; invalid callers will get `BufferUnderflowException` or array bounds errors rather than checked `IOException`. `ByteBufferStrategy.readFromBlock` assumes `length <= readBuf.remaining()` when setting the duplicate limit. Tests should cover short reads, EOF negative returns, ByteBuffer position changes, source buffer immutability, and bounded-copy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReaderStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/RemotePeerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/RemotePeerFactory.java

Purpose: `RemotePeerFactory` is a private HDFS client extension point for constructing connected remote `Peer` instances used by block readers. It isolates socket creation, optional SASL/encryption setup, and DataNode identity handling from consumers such as `BlockReaderFactory`.

Important APIs/types/functions: the only method is `Peer newConnectedPeer(InetSocketAddress addr, Token<BlockTokenIdentifier> blockToken, DatanodeID datanodeId) throws IOException`. Inputs are the target socket address, block token for SASL or block access negotiation, and the destination DataNode identity.

Control flow: the interface has no implementation in this file. Implementations are expected to connect to the supplied address, wrap or negotiate the stream as configured, authenticate/authorize using the block token, and return a ready `Peer`. Failures are surfaced as `IOException`.

State and persistence behavior: this file defines no state. Implementations may use socket caches or security state, but the contract here returns a new connected peer from the caller perspective.

Dependencies and integration points: `BlockReaderFactory.nextTcpPeer()` calls this interface when peer-cache reuse is unavailable. `Peer` is the HDFS network abstraction consumed by `BlockReaderRemote`. `DatanodeID` and `BlockTokenIdentifier` tie the connection to HDFS block-transfer security.

Risks: because the interface abstracts security negotiation, callers must distinguish security exceptions from stale-socket I/O failures after implementations throw. Tests should inject implementations that return a peer, throw token/encryption errors, throw ordinary `IOException`, and verify `BlockReaderFactory` fallback and retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/RemotePeerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessor.java

Purpose: `ReplicaAccessor` is a public stable plugin API that lets external code provide direct access to an HDFS block replica, bypassing normal `BlockReader` construction when a specialized local, hardware, or network path is available.

Important APIs/types/functions: implementations must provide positional `read(long pos, byte[] buf, int off, int len)`, positional `read(long pos, ByteBuffer buf)`, `close()`, `isLocal()`, and `isShortCircuit()`. The default `getNetworkDistance()` returns `0` for local access and `Integer.MAX_VALUE` otherwise.

Control flow: the API is pull based. HDFS builds an accessor through `ReplicaAccessorBuilder`, wraps it in `ExternalBlockReader`, and calls positional reads. The contract says reads return a full requested count unless EOF is reached, and return `-1` only when no bytes can be returned at EOF. `close()` should leave the accessor closed even if it throws.

State and persistence behavior: this abstract class has no fields, but implementors commonly hold file descriptors, device handles, or network resources. The visible length is supplied at build time, so implementations should not expose bytes appended later unless reopened through HDFS.

Dependencies and integration points: `BlockReaderFactory.tryToCreateExternalBlockReader()` constructs plugin builders configured through `dfs.client.replica.accessor.builder.classes` and wraps successful `ReplicaAccessor` instances. The API contributes local, short-circuit, and network-distance read statistics through `isLocal`, `isShortCircuit`, and `getNetworkDistance`.

Risks: incorrect EOF semantics can break HDFS read loops that expect no short reads before EOF. ByteBuffer implementations must advance buffer position consistently. Resource leaks are possible if `close()` throws before cleanup. Tests should validate EOF behavior, byte-array and ByteBuffer parity, statistics classification, network-distance override behavior, and cleanup on caller exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessorBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessorBuilder.java

Purpose: `ReplicaAccessorBuilder` is the public stable builder API for external replica-access plugins. It lets HDFS pass all block, security, checksum, client, configuration, and visibility metadata to a plugin before the plugin decides whether it can create a `ReplicaAccessor`.

Important APIs/types/functions: setters include `setFileName`, `setBlock(long,String)`, `setGenerationStamp`, `setVerifyChecksum`, `setClientName`, `setAllowShortCircuitReads`, `setVisibleLength`, `setConfiguration`, and `setBlockAccessToken`. `build()` returns either a usable `ReplicaAccessor` or `null` when the plugin cannot handle the request.

Control flow: `BlockReaderFactory` reflectively instantiates each configured builder class, serializes the block token into bytes, invokes the setters, and calls `build()`. If `build()` returns an accessor, HDFS assumes it works and does not attempt a normal block reader for that read. If `null` is returned, the next plugin or normal reader path is tried.

State and persistence behavior: this abstract class has no state; concrete builders accumulate the setter values. `setVisibleLength` is an important consistency boundary: it tells plugins the maximum block length visible to the current file open, and later appends require reopening the file.

Dependencies and integration points: the builder consumes `Configuration` and returns `ReplicaAccessor`. It integrates with client configuration key `HdfsClientConfigKeys.REPLICA_ACCESSOR_BUILDER_CLASSES_KEY` and `BlockReaderFactory.tryToCreateExternalBlockReader()`.

Risks: plugin builders must perform permission and setup checks in `build()`; HDFS treats a non-null accessor as authoritative. Failing to honor `verifyChecksum`, block token, generation stamp, or visible length can expose stale or unauthorized data. Tests should use fake builders that return null, throw during construction, throw in build, and return accessors to validate fallback and isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessorBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StatefulStripeReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StatefulStripeReader.java

Purpose: `StatefulStripeReader` specializes `StripeReader` for reading a complete `AlignedStripe` that belongs to a single stripe. It uses buffers owned by `DFSStripedInputStream` so decoded or fetched data can be placed into the current stripe buffer and parity buffer.

Important APIs/types/functions: constructor forwards the aligned stripe, EC policy, target blocks, block-reader state, corrupted-block tracker, raw erasure decoder, and striped input stream to the base class. Overrides are `prepareDecodeInputs()`, `prepareParityChunk(int)`, and `decode()`.

Control flow: `prepareDecodeInputs()` duplicates the current stripe buffer under synchronization on `dfsStripedInputStream`, creates the `decodeInputs` array if needed, and maps each data unit into a slice based on `alignedStripe` offset/span, cell size, and data index. Missing data chunks get `StripingChunk` wrappers around the same buffers. `prepareParityChunk()` validates that the target index is a parity slot and unprepared, slices the parity buffer for the stripe span, creates an `ECChunk`, and installs a `StripingChunk`. `decode()` finalizes inputs and calls `decodeAndFillBuffer(false)` because stateful reads already target the current stripe buffer.

State and persistence behavior: all state is transient and buffer backed. It mutates `decodeInputs` and `alignedStripe.chunks`; no file-system metadata is persisted. Synchronization is limited to safely duplicating the current stripe buffer reference.

Dependencies and integration points: depends on `StripeReader`, `DFSStripedInputStream`, `StripedBlockUtil`, `ECChunk`, `RawErasureDecoder`, `ErasureCodingPolicy`, and `LocatedBlock`. It participates in erasure-coded reads after block layout has produced an aligned stripe.

Risks: buffer slicing math is sensitive to `bufOff % cellSize`, `cellSize * i`, and span length. Bad alignment can corrupt data placement or decode inputs. Tests should cover single-stripe partial offsets, missing data chunks, parity read preparation, direct/non-direct decoder preferences through the base class, and decode behavior where output already resides in the current stripe buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StatefulStripeReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StripeReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StripeReader.java

Purpose: `StripeReader` is the abstract engine for reading an erasure-coded aligned stripe. It schedules parallel internal-block reads, tracks missing/corrupt chunks, fetches parity when needed, and invokes a raw erasure decoder to reconstruct unavailable data.

Important APIs/types/functions: nested `ReaderRetryPolicy` tracks one refetch allowance each for encryption key and block token. Nested `BlockReaderInfo` holds a `BlockReader`, its `DatanodeInfo`, current block-reader offset, and a skip flag for failed readers. Key methods are `readStripe()`, `readChunk()`, `readCells()`, `readToBuffer()`, `readDataForDecoding()`, `readParityChunks()`, `finalizeDecodeInputs()`, `decodeAndFillBuffer(boolean)`, `prepareErasedIndices()`, and abstract hooks `prepareDecodeInputs`, `prepareParityChunk`, and `decode`.

Control flow: `readStripe()` submits reads for requested data chunks. If any block location or read is missing, it ensures all needed data chunks have decode buffers and reads enough parity chunks to tolerate the missing count. Futures complete through `StripedBlockUtil.getNextCompletedStripedRead`. Successful reads mark chunks `FETCHED`, update offsets, and may cancel remaining work once all data chunks are fetched. Failed reads mark chunks `MISSING`, close the reader, increment missing count, and may trigger additional data/parity reads. After all pending futures settle, any missing chunks are decoded.

State and persistence behavior: state is in-memory per stripe: futures, reader offsets, chunk states, missing/fetched counters, decode input buffers, and a `readTo` bound passed to block-reader creation. It records corrupted blocks in `CorruptedBlocks` and updates read statistics, but persists no namespace or block metadata.

Dependencies and integration points: integrates with `DFSStripedInputStream` for block-reader creation, current readers, thread pool, stats, and cleanup; `StripedBlockUtil` for chunk state and completion handling; `RawErasureDecoder` for reconstruction; `ReadStatistics` through `ByteBufferStrategy`; and HDFS corruption tracking.

Risks: missing count must never exceed parity count; otherwise the method clears futures and throws. Checksum failures clear buffers, close readers, and record corruption, so tests should verify retry/decode paths after checksum exceptions. Other risk areas are stale reader offsets, future cancellation without interrupt, partial reads that unexpectedly return EOF, and decode input finalization for fetched chunk buffers versus all-zero chunks. Test signals include EC degraded reads, corrupt internal blocks, parity scarcity, interrupted reads, all-zero chunks, short-circuit/read stats attribution, and cross-cell aligned stripes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StripeReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StripedDataStreamer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StripedDataStreamer.java

Purpose: `StripedDataStreamer` extends `DataStreamer` for erasure-coded striped writes. A `DFSStripedOutputStream` owns multiple streamers, one per internal block index, and a shared coordinator serializes NameNode interactions and pipeline recovery decisions across those streamers.

Important APIs/types/functions: constructor passes normal streamer dependencies to `DataStreamer` and stores a `Coordinator` plus stripe index. `getIndex()`, `isHealthy()`, `endBlock()`, `peekFollowingBlock()`, `setExternalError()`, and `toString()` expose state. `setupPipelineForCreate()` and `setupPipelineInternal()` implement striped block allocation and recovery behavior.

Control flow: on block creation, `getFollowingBlock()` polls the coordinator's per-index following-block queue, sets current block, resets counters, installs the block token, and creates a block output stream to the assigned DataNode/storage. If creation fails, the bad node is excluded and an `IOException` is thrown. `endBlock()` offers the completed internal block to the coordinator before normal streamer cleanup. During recovery, `setupPipelineInternal()` loops while the client is running, handles restarting and bad DataNodes, takes a new block with fresh generation stamp/token from the coordinator, reconnects the pipeline, reports success/failure to the coordinator, waits for all streamers' aggregate result, and updates generation stamp or closes/restarts as needed.

State and persistence behavior: mutable state is inherited streamer block, access token, bytes sent, queues, error state, excluded nodes, and closed state. Persistent HDFS effects happen indirectly through DataNode block writes and NameNode block generation stamps coordinated by `DFSStripedOutputStream`.

Dependencies and integration points: tightly coupled with `DFSStripedOutputStream.Coordinator`, `DataStreamer`, `LocatedBlock`, `DatanodeInfo`, storage metadata arrays, `DataChecksum`, `CachingStrategy`, `ByteArrayManager`, and test hooks such as `failPacket4Testing`.

Risks: recovery is coordinated across streamers; one streamer's premature close or stale update can affect the whole block group. Unlike replicated writes, DataNode error handling closes the striped streamer rather than replacing the node locally. Tests should cover block group allocation ordering, bad-node exclusion, external error notification waking `dataQueue`, generation-stamp synchronization, coordinator timeouts, and partial streamer failure during recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/StripedDataStreamer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/UnknownCipherSuiteException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/UnknownCipherSuiteException.java

Purpose: `UnknownCipherSuiteException` is a small HDFS-specific `IOException` used when encrypted HDFS metadata or negotiation references a cipher suite not understood by the client.

Important APIs/types/functions: the class exposes a single constructor `UnknownCipherSuiteException(String unknown)` that formats `"Unknown CipherSuite: " + unknown` as the exception message.

Control flow: there is no internal branching. Callers construct and throw it when cipher suite parsing or validation fails.

State and persistence behavior: the only state is the inherited exception message. No persistent metadata is modified.

Dependencies and integration points: depends only on `java.io.IOException`. It integrates with crypto protocol handling elsewhere in HDFS client code, where checked exceptions are preferred for unsupported encryption metadata.

Risks: this exception intentionally carries the unknown value in the message; tests should verify user-facing diagnostics are clear but do not leak sensitive material if callers pass raw metadata. It should be caught distinctly only where unsupported ciphers can trigger fallback or upgrade messaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/UnknownCipherSuiteException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/UnknownCryptoProtocolVersionException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/UnknownCryptoProtocolVersionException.java

Purpose: `UnknownCryptoProtocolVersionException` is a checked HDFS client exception for unsupported crypto protocol versions found during encryption metadata processing or negotiation.

Important APIs/types/functions: the sole constructor `UnknownCryptoProtocolVersionException(String unknown)` builds the message `"Unknown CryptoProtocolVersion: " + unknown`.

Control flow: no internal control flow exists. The class serves as a typed signal for callers that a crypto protocol version is unrecognized.

State and persistence behavior: state is limited to the inherited exception message. There is no persistence or cleanup.

Dependencies and integration points: depends on `java.io.IOException` and is expected to be thrown by HDFS crypto code that parses file encryption information or data-transfer encryption protocol fields.

Risks: because it represents compatibility failure, tests should validate that newer/unknown protocol values fail clearly and do not silently downgrade crypto behavior. Diagnostic content should remain safe if the unknown string originates from serialized metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/UnknownCryptoProtocolVersionException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ViewDistributedFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ViewDistributedFileSystem.java

Purpose: `ViewDistributedFileSystem` is an HDFS-compatible `DistributedFileSystem` subclass that delegates path-based operations through `ViewFileSystemOverloadScheme` while preserving many DFS-specific APIs. It lets users configure `fs.hdfs.impl` to this class and get mount-table behavior with a DistributedFileSystem-shaped API surface.

Important APIs/types/functions: fields are `vfs` for the mounted view filesystem and `defaultDFS` for the fallback/base HDFS. `initialize()` first calls `super.initialize`, then tries to initialize `ViewFileSystemOverloadScheme`; if mounting fails it initializes the normal DFS client and behaves like regular DFS. `initDFSClient()` is intentionally empty because viewfs initialization owns setup. Helpers `checkDFS(FileSystem,String)` and `checkDefaultDFS(FileSystem,String)` enforce whether an operation needs a mounted target to be HDFS or a fallback cluster.

Control flow: almost every override follows one of four patterns. If `vfs == null`, delegate to `super`. Simple path APIs delegate directly to `vfs` (`open`, `create`, `delete`, listing, ACLs, xattrs, checksums, capabilities). DFS-specific path APIs resolve mount info, validate target `DistributedFileSystem`, translate to the target path, and call the target DFS (`recoverLease`, favored-node create/append, snapshots, encryption zone per path, EC policy per path, open-file listing by path). Cluster-wide APIs use `defaultDFS` and fail without a fallback (`safeMode`, block counts, datanode stats, namespace operations, key provider, inotify, global open files). Multi-child APIs iterate all child DFS instances and aggregate or collect `MultipleIOException` (`cache directives/pools`, EC policy administration, trash roots).

State and persistence behavior: this class stores only runtime filesystem delegates and inherited statistics/configuration. Persistent effects are delegated to child file systems: namespace mutations, quotas, snapshots, cache pools, encryption zones, xattrs, EC policies, and writes. `close()` closes `vfs` then calls `super.close()`.

Dependencies and integration points: integrates with `ViewFileSystemOverloadScheme`, `DistributedFileSystem`, `FileSystem`, HDFS protocol types, tokens, cache APIs, snapshots, encryption, EC, ACL/xattr APIs, and `MultipleIOException`.

Risks: path translation correctness is the primary risk. Cross-filesystem rename is explicitly rejected. Several APIs are unsupported or fallback-only (`createPathHandle`, symlinks, many cluster-wide operations without fallback). A notable suspicious implementation is `getCorruptBlocksCount()` returning `defaultDFS.getLowRedundancyBlocksCount()` in view mode, which appears semantically wrong. `getInotifyEventStream(long lastReadTxid)` ignores `lastReadTxid` when delegating in view mode. `primitiveCreate` passes `f` instead of `mountPathInfo.getPathOnTarget()` to the target DFS, unlike surrounding methods. `createNonRecursive` passes `bufferSize` where `blockSize` is expected in both branches. Tests should cover mounted versus no-mount initialization, fallback absence, path translation for every DFS-specific method, multi-child aggregation failure behavior, unsupported methods, and parity with `DistributedFileSystem` for cluster-wide calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ViewDistributedFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/XAttrHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/XAttrHelper.java

Purpose: `XAttrHelper` centralizes HDFS extended-attribute name parsing, prefix formatting, list construction, and map conversion. It is private client-side support for xattr APIs.

Important APIs/types/functions: `buildXAttr(String)`, `buildXAttr(String,byte[])`, `buildXAttrAsList(String)`, `getFirstXAttrValue(List<XAttr>)`, `getFirstXAttr(List<XAttr>)`, `buildXAttrMap(List<XAttr>)`, `getPrefixedName(XAttr)`, `getPrefixedName(NameSpace,String)`, and `buildXAttrs(List<String>)`.

Control flow: `buildXAttr` validates non-null names, requires a prefix followed by a dot, rejects empty local names, maps case-insensitive prefixes `user`, `trusted`, `system`, `security`, and `raw` to `XAttr.NameSpace`, and builds an `XAttr` with the substring after the dot. List and map helpers use the builder or prefixed-name conversion. Null xattr values are converted to empty byte arrays for API callers that need to distinguish existing-empty from missing.

State and persistence behavior: stateless utility class. It allocates lists/maps and `XAttr` objects but persists nothing.

Dependencies and integration points: uses `HadoopIllegalArgumentException`, `XAttr`, `XAttr.NameSpace`, Hadoop `Lists`, Guava-compatible `Maps`, `StringUtils`, and `Preconditions`. It feeds HDFS xattr RPC request/response conversion paths and user-facing xattr maps.

Risks: prefix matching is case-insensitive but generated names are lower-case namespace strings plus original local name. Empty values are normalized to `new byte[0]`, which callers must not confuse with absent xattrs (`null` return from `getFirstXAttrValue`). Tests should cover invalid prefixes, missing dot, empty local names, all namespace prefixes, case variants, null lists, empty lists, null values, and round-tripping prefixed names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/XAttrHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/BlockReportOptions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/BlockReportOptions.java

Purpose: `BlockReportOptions` is a public evolving immutable value object for manually triggering DataNode block reports with optional incremental mode and optional NameNode target address.

Important APIs/types/functions: fields are `incremental` and `namenodeAddr`. Accessors are `isIncremental()` and `getNamenodeAddr()`. Nested `Factory` provides `setIncremental(boolean)`, `setNamenodeAddr(InetSocketAddress)`, and `build()`. `toString()` exposes both fields for diagnostics.

Control flow: callers create a `Factory`, mutate builder fields, and call `build()`, which invokes the private constructor. Defaults are full block report (`incremental=false`) and no explicit NameNode address.

State and persistence behavior: `BlockReportOptions` instances are immutable references after construction. The builder is mutable and reusable. There is no persistence in this class.

Dependencies and integration points: depends on `InetSocketAddress` and Hadoop audience/stability annotations. It integrates with HDFS administrative paths that trigger block reports against DataNodes/NameNodes.

Risks: no validation is performed for the NameNode address; downstream code must handle null or unresolved addresses. Tests should verify defaults, builder mutation, immutability of produced options relative to later builder changes, and `toString()` content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/BlockReportOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/CreateEncryptionZoneFlag.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/CreateEncryptionZoneFlag.java

Purpose: `CreateEncryptionZoneFlag` is a public evolving enum used by `HdfsAdmin.createEncryptionZone(Path,String,EnumSet)` to select extra behavior when creating an HDFS encryption zone.

Important APIs/types/functions: enum values are `NO_TRASH` with mode `0x00` and `PROVISION_TRASH` with mode `0x01`. `valueOf(short mode)` maps wire/config modes back to enum values, returning `null` for unknown values. `getMode()` exposes the short mode.

Control flow: callers pass an `EnumSet<CreateEncryptionZoneFlag>`. `HdfsAdmin` creates the encryption zone, then provisions `.Trash/` if `PROVISION_TRASH` is present and rejects a set containing both `PROVISION_TRASH` and `NO_TRASH`.

State and persistence behavior: enum constants are static immutable values. Persistent effects happen only in callers that create encryption zones or trash directories.

Dependencies and integration points: referenced by `HdfsAdmin`; imports `Path` and `EnumSet` for Javadoc. It is part of the public client API for encryption-zone administration.

Risks: `valueOf(short)` returning null for unknown modes requires callers to null-check. `NO_TRASH` has mode zero, so empty flag sets and explicit `NO_TRASH` are semantically close in callers. Tests should cover mode mapping, unknown mode handling, and conflicting flag validation in `HdfsAdmin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/CreateEncryptionZoneFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/DfsPathCapabilities.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/DfsPathCapabilities.java

Purpose: `DfsPathCapabilities` provides the shared implementation of `hasPathCapability` for DFS and WebHDFS clients. It maps standardized Hadoop capability strings to HDFS-supported booleans or indicates that the caller should defer to a superclass.

Important APIs/types/functions: `hasPathCapability(Path path, String capability)` validates arguments through `PathCapabilitiesSupport.validatePathCapabilityArgs` and returns `Optional<Boolean>`.

Control flow: a switch returns `Optional.of(true)` for HDFS capabilities including ACLs, append, checksums, concat, corrupt block listing, multipart uploader, path handles, permissions, snapshots, storage policy, xattrs, truncate, and EC policy open-file option. For symlinks it returns `Optional.of(FileSystem.areSymlinksEnabled())`. Unknown capabilities return `Optional.empty()`.

State and persistence behavior: stateless final utility class with private constructor. It performs no I/O and persists no state.

Dependencies and integration points: uses `CommonPathCapabilities`, `Options.OpenFileOptions`, `FileSystem`, `Path`, and the capability validation helper. It is called by DFS-family filesystem implementations to keep capability reporting consistent.

Risks: returning true is a contract to higher layers; if a DFS variant does not support one listed capability, it must override or avoid using this helper. Tests should cover all listed capability constants, symlink enabled/disabled behavior, validation failures for null/empty inputs, and `Optional.empty()` fallback for unknown strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/DfsPathCapabilities.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsAdmin.java

Purpose: `HdfsAdmin` is the public evolving administrative facade for HDFS. It wraps a `DistributedFileSystem` and exposes quota, snapshot, cache, encryption, storage policy, erasure coding, inotify, and open-file operations without requiring applications to use `DistributedFileSystem` or CLI-oriented `DFSAdmin` directly.

Important APIs/types/functions: constructor `HdfsAdmin(URI,Configuration)` resolves a `FileSystem`, unwraps `ViewFileSystemOverloadScheme` to its raw DFS when needed, and rejects non-HDFS filesystems. `TRASH_PERMISSION` is `rwxrwxrwx` with sticky bit for snapshot/EZ trash provisioning. Methods include namespace/space/storage-type quota setters, snapshot allow/disallow and trash provisioning, cache directive/pool CRUD/listing, `getKeyProvider`, deprecated and flag-based `createEncryptionZone`, encryption-zone listing and re-encryption, `getFileEncryptionInfo`, inotify stream creation, storage policy CRUD, EC policy CRUD and status, `satisfyStoragePolicy`, and open-file listing.

Control flow: almost all methods delegate directly to `dfs` or `dfs.getClient()`. `allowSnapshot` provisions snapshot trash after allowing snapshots if enabled by the target DFS. Flag-based `createEncryptionZone` calls `dfs.createEncryptionZone` first, then provisions EZ trash when `PROVISION_TRASH` is present, rejecting the simultaneous presence of `NO_TRASH`. List methods return `RemoteIterator` objects whose batching/consistency semantics are documented by the underlying DFS.

State and persistence behavior: persistent effects are administrative HDFS mutations delegated to the NameNode: quotas, cache directives/pools, encryption zone metadata, storage policies, EC policy definitions/states, snapshot settings, and open-file queries. Local state is only the final `DistributedFileSystem` reference.

Dependencies and integration points: integrates with `FileSystem`, `DistributedFileSystem`, `ViewFileSystemOverloadScheme`, HDFS protocol types, key providers, ACL/security exceptions, storage policy and EC APIs, and inotify.

Risks: flag-based encryption-zone creation is not atomic with trash provisioning; a failure after zone creation can leave a zone without provisioned trash. Constructor unwrapping depends on default URI/raw FS behavior under viewfs. Most methods rely on NameNode authorization and can throw `AccessControlException`. Tests should cover non-HDFS rejection, viewfs raw DFS resolution, flag conflict validation, trash provisioning behavior, iterator delegation, and all direct delegate calls with mocked DFS failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsAdmin.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsClientConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsClientConfigKeys.java

Purpose: `HdfsClientConfigKeys` is the private central constant interface for HDFS client configuration keys and defaults. It covers core block/replication defaults, WebHDFS behavior, NameNode addresses, client socket/cache settings, short-circuit and mmap reads, retry/failover, write/pipeline behavior, erasure coding, security/data-transfer options, health probes, and deprecated compatibility keys.

Important APIs/types/functions: top-level constants include `DFS_BLOCK_SIZE_KEY/DEFAULT`, replication defaults, WebHDFS user/ACL patterns and security knobs, client socket/cache/domain-socket settings, checksum settings, data transfer protection/encryption keys, replica accessor builder classes key, dead-node detection keys, read-block-location refresh keys, and miscellaneous lease/fsck/congestion settings. Nested interfaces organize `DeprecatedKeys`, `Retry`, `Failover`, `Write` with nested `ByteArrayManager` and `ECRedundancy`, `BlockWrite` with nested `ReplaceDatanodeOnFailure`, `Read` with nested `ShortCircuit`, top-level `ShortCircuit`, `Mmap`, `HedgedRead`, `StripedRead`, and `HttpClient`.

Control flow: no executable logic beyond constant initialization. Consumers import keys and defaults to parse `Configuration` values into concrete client config objects such as `DfsClientConf`.

State and persistence behavior: all values are static constants. Configuration persistence happens outside this file in Hadoop configuration resources and runtime `Configuration` objects.

Dependencies and integration points: uses `HdfsConstants` for default data socket size and `TimeUnit` for millisecond defaults. This interface is referenced throughout HDFS client, WebHDFS, failover, read/write, short-circuit, mmap, EC, and security code.

Risks: this file is a compatibility surface; changing key names or defaults can break deployments. Some defaults strongly affect performance and failure behavior, such as socket cache capacity/expiry, striped read thread pool size, dead-node detection intervals, retry windows, and short-circuit/mmap toggles. Test signals are mostly configuration parsing tests: verify defaults, deprecated key translation, boundary values, nested prefix composition, and interactions with `DfsClientConf`. A typo-like constant `DFS_CLIENT_EC_WRITE_FAILED_BLOCKS_TOLERATED_DEFAILT` is part of the API surface and should be handled cautiously.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsClientConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataInputStream.java

Purpose: `HdfsDataInputStream` is the public evolving HDFS implementation of `FSDataInputStream`. It exposes HDFS-specific read state and statistics while supporting both plain `DFSInputStream` and encrypted `CryptoInputStream` wrappers.

Important APIs/types/functions: constructors accept `DFSInputStream` or `CryptoInputStream`; the crypto constructor verifies the wrapped stream is a `DFSInputStream`. `getWrappedStream()` returns the actual stream stored in the superclass. Private `getDFSInputStream()` unwraps crypto when needed. Public HDFS-specific methods are `getCurrentDatanode()`, `getCurrentBlock()`, `getAllBlocks()`, `getVisibleLength()`, `getReadStatistics()`, and `clearReadStatistics()`.

Control flow: all HDFS-specific methods delegate to the underlying `DFSInputStream`, unwrapping crypto first. `getAllBlocks()` may perform I/O through the underlying stream. Statistics can exceed application-visible bytes because buffering may read ahead.

State and persistence behavior: this class stores no fields beyond inherited stream state. Persistent HDFS state is not changed. It exposes transient client read state such as current DataNode, current block, located blocks, file length, and read statistics.

Dependencies and integration points: integrates with `FSDataInputStream`, `CryptoInputStream`, `DFSInputStream`, `ReadStatistics`, `DatanodeInfo`, `ExtendedBlock`, and `LocatedBlock`. It is returned by HDFS open paths when callers need HDFS-specific read inspection.

Risks: type assumptions are strict; passing a crypto stream that does not wrap `DFSInputStream` fails immediately. Methods expose mutable/read-live underlying state, so callers should not assume stable block lists during concurrent reads. Tests should cover plain and crypto construction, unwrap behavior, statistics clearing, visible length including under-construction last block, and delegation while encrypted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataOutputStream.java

Purpose: `HdfsDataOutputStream` is the public evolving HDFS implementation of `FSDataOutputStream`. It exposes HDFS-specific write controls, especially current pipeline replication and sync flags, while supporting encrypted output streams.

Important APIs/types/functions: constructors accept `DFSOutputStream` or `CryptoOutputStream`, with optional start position. Crypto constructors verify the wrapped stream is a `DFSOutputStream`. `getCurrentBlockReplication()` returns the current valid replica count from the underlying DFS output stream. `hsync(EnumSet<SyncFlag>)` exposes detailed HDFS sync semantics. `SyncFlag` values are `UPDATE_LENGTH` and `END_BLOCK`.

Control flow: methods call `getWrappedStream()`, unwrap crypto if present, and delegate to `DFSOutputStream`. `hsync` flushes the crypto stream before unwrapping so encrypted buffered bytes reach the DFS stream before sync. `UPDATE_LENGTH` asks the NameNode to update block length; `END_BLOCK` syncs and rolls to a new block.

State and persistence behavior: this class stores no additional state. Persistent effects happen through the delegated `DFSOutputStream`: DataNode flushes, NameNode length updates, block finalization, and new block allocation.

Dependencies and integration points: integrates with `FSDataOutputStream`, `CryptoOutputStream`, `DFSOutputStream`, `FileSystem.Statistics`, and HDFS write/sync paths.

Risks: incorrect wrapping would cause `ClassCastException`, guarded by constructor checks for crypto but not for inherited `getWrappedStream()` state mutation. `hsync` with `END_BLOCK` changes block layout and should be tested with appends and encrypted streams. Tests should cover crypto flush-before-sync, current replication after pipeline failures, start-position constructors, and both sync flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsDataOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsUtils.java

Purpose: `HdfsUtils` is a public evolving utility class. In this file it provides a health check that determines whether an HDFS URI is reachable and not in safe mode.

Important APIs/types/functions: `LOG` is an SLF4J logger. `isHealthy(URI uri)` validates the URI scheme, constructs a fresh `Configuration`, disables filesystem caching for the scheme, disables HDFS client retry policy, sets IPC max connect retries to zero, opens a `DistributedFileSystem`, queries safe mode with `SAFEMODE_GET`, and returns true only when safe mode is false.

Control flow: non-HDFS schemes throw `IllegalArgumentException`. DFS open and safe-mode query are inside try-with-resources. Any `IOException` logs at debug and returns false. Successful safe-mode query logs the result at debug and returns the negated safe-mode flag.

State and persistence behavior: no persistent changes are intended. `setSafeMode(SAFEMODE_GET)` is a query action. The method creates and closes a fresh filesystem instance with cache disabled to avoid reusing unhealthy clients.

Dependencies and integration points: integrates with `FileSystem`, `DistributedFileSystem`, `Configuration`, `CommonConfigurationKeysPublic`, `HdfsConstants`, `HdfsClientConfigKeys.Retry`, and safe-mode RPCs.

Risks: health is intentionally narrow: reachable and not in safe mode. It does not check DataNode availability, under-replication, write ability, or HA observer state. Disabling retries makes it fast but sensitive to transient connection failures. Tests should cover scheme validation, cache-disable configuration, safe-mode true/false, IOException returning false, and resource closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/HdfsUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderFactory.java

Purpose: `BlockReaderFactory` builds the best available `BlockReader` for a block read. It prefers configured external `ReplicaAccessor` plugins, then short-circuit local readers, then data transfer over UNIX domain sockets, and finally remote TCP block readers.

Important APIs/types/functions: it is a `ShortCircuitReplicaCreator`. Builder-style setters configure file name, `ExtendedBlock`, token, start offset, checksum flag, client name, DataNode/storage, short-circuit permission, `ClientContext`, length, caching strategy, address, UGI, `RemotePeerFactory`, and `Configuration`. `build()` is the main entry point. Key helpers include `tryToCreateExternalBlockReader`, `getLegacyBlockReaderLocal`, `getBlockReaderLocal`, `createShortCircuitReplicaInfo`, `requestFileDescriptors`, `getRemoteBlockReaderFromDomain`, `getRemoteBlockReaderFromTcp`, `nextDomainPeer`, `nextTcpPeer`, `isSecurityException`, and `getRemoteBlockReader`.

Control flow: `build()` validates configuration and non-negative length, then tries external accessors. If allowed and configured, it tries legacy or modern local short-circuit reads. If domain-socket data traffic is enabled, it tries remote block reader over a domain socket. Any local/domain I/O failure falls back to TCP unless security exceptions require caller action. TCP construction reuses peer-cache entries up to `remainingCacheTries`, otherwise uses `RemotePeerFactory`. Short-circuit modern reads fetch/create a cached `ShortCircuitReplica`; replica creation requests file descriptors from the DataNode over a domain socket and handles success, unsupported access, token errors, and unknown statuses.

State and persistence behavior: state is per-factory mutable configuration plus cached `pathInfo` and remaining peer-cache tries. It mutates `ClientContext` caches: peer cache, short-circuit cache, shared-memory slots, and domain socket path disable/short-circuit disable states. Persistent HDFS metadata is not changed, but block-token and encryption-key failures signal higher-level refresh.

Dependencies and integration points: integrates with `DfsClientConf`, `ClientContext`, `DomainSocketFactory`, `ShortCircuitCache`, `ShortCircuitReplica`, `BlockReaderLocal`, `BlockReaderLocalLegacy`, `BlockReaderRemote`, `RemotePeerFactory`, data-transfer `Sender`, protobuf block-op responses, block tokens, DataNode IDs, and external `ReplicaAccessorBuilder` plugins.

Risks: security exceptions must not be swallowed as stale sockets; `isSecurityException` enforces that distinction. Descriptor-passing failures can leak slots or file descriptors unless cleanup paths run correctly. Domain socket path disabling is a performance and availability control. External accessor plugins are loaded reflectively and catch `Throwable`, so bad plugins should not prevent normal reads but can add latency/log noise. Tests should cover fallback ordering, cache retry exhaustion, stale cached peers, token/encryption errors, descriptor response statuses, slot cleanup, receipt verification, legacy disable behavior, TCP-disabled test mode, and plugin success/null/throw cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderLocal.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderLocal.java

Purpose: `BlockReaderLocal` implements short-circuit local HDFS block reads. When the client is colocated with a DataNode and has received block and metadata file descriptors, it reads directly from local file channels instead of using DataNode socket data transfer.

Important APIs/types/functions: nested `Builder` configures short-circuit buffer size, checksum verification, readahead, filename, `ShortCircuitReplica`, start offset, block, storage type, and short-circuit config. Main read APIs implement `BlockReader`: `read(ByteBuffer)`, `read(byte[],int,int)`, `skip(long)`, `available()`, `close()`, `readFully`, `readAll`, `isShortCircuit`, `getClientMmap`, `getDataChecksum`, and `getNetworkDistance`. Internal helpers manage direct buffers and checksums: `fillBuffer`, `fillDataBuf`, `readWithBounceBuffer`, `readWithoutBounceBuffer`, `createNoChecksumContext`, and `releaseNoChecksumContext`.

Control flow: construction opens data and metadata channels from the replica, reads the metadata checksum header, computes checksum chunk sizes, max allocated chunks, and effective readahead. Reads first decide whether checksums can be skipped: because verification is disabled, storage is transient, or the replica can be anchored. Zero readahead plus no checksum uses direct channel reads without bounce buffers. Otherwise the reader drains any existing data buffer, uses a fast direct path for aligned direct buffers large enough for a full readahead window, or fills a bounce buffer aligned to checksum chunks. `fillBuffer` reads data at `dataPos`, advances it, reads corresponding checksums when needed, and verifies chunked sums. `close` unrefs the replica and returns direct buffers to the pool.

State and persistence behavior: mutable state includes `closed`, replica refcount, data/checksum channels, `dataPos`, direct bounce buffers, checksum settings, and static optional metrics. It does not persist HDFS metadata. Anchoring affects DataNode-side eviction behavior for short-circuit replicas while reads or safe mmaps are active.

Dependencies and integration points: integrates with `ShortCircuitReplica`, `ClientMmap`, `BlockMetadataHeader`, `DataChecksum`, `DirectBufferPool`, `BlockReaderIoProvider`, short-circuit metrics, storage types, and `BlockReaderFactory`.

Risks: buffer and position accounting are subtle. `freeDataBufIfExists()` moves `dataPos` backward by unread buffered bytes; incorrect calls can duplicate or skip data. Checksum verification requires chunk alignment and complete metadata reads. Transient storage skips anchoring because checksums are unavailable. Tests should cover aligned and unaligned reads, byte array versus direct/non-direct ByteBuffer paths, EOF semantics, skip across buffered data, checksum failure, zero readahead, transient storage, mmap anchoring, close idempotence, metrics initialization, and buffer-pool return behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/impl/BlockReaderLocal.java -->
