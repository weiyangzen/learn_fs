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
