# subset-b-007347 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnionStorageStatistics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnionStorageStatistics.java

## Purpose
Combines multiple StorageStatistics instances behind one StorageStatistics view. It exposes a union iterator, first-match getLong lookup, aggregate isTracked lookup, and reset fan-out across delegates.

## Important APIs, Types, and Functions
UnionStorageStatistics extends StorageStatistics; LongStatisticIterator walks each delegate getLongStatistics(); getLong(), isTracked(), reset().

## Control Flow
Construction validates name, array, and elements. Iteration advances delegate iterators lazily; lookups scan delegates in order and return the first non-null value.

## State and Persistence Behavior
Holds only references to delegate statistics. reset mutates every delegate counter set; there is no persistence except the delegates statistics state.

## Dependencies and Integration Points
Depends on StorageStatistics and Preconditions. Used where one filesystem wants one statistics object spanning multiple internal stores.

## Risks and Test Signals
Iterator boundary logic and delegate ordering are the main risks. Test empty/single/multiple delegates, duplicate keys, reset propagation, and iterator exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnionStorageStatistics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnresolvedLinkException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnresolvedLinkException.java

## Purpose
Checked IOException signaling that a filesystem symlink or link-like path component could not be resolved.

## Important APIs, Types, and Functions
Constructors: no-arg and message constructor. Public type extends IOException.

## Control Flow
No internal flow; callers throw it during link resolution and higher layers may retry through FileContext/FSLinkResolver.

## State and Persistence Behavior
No state beyond IOException message/stack.

## Dependencies and Integration Points
Integrated with FSLinkResolver, FileContext, AbstractFileSystem, and path resolution code.

## Risks and Test Signals
Compatibility risk is exception taxonomy. Tests should verify symlink resolution APIs surface this specific checked type where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnresolvedLinkException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedFileSystemException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedFileSystemException.java

## Purpose
Checked IOException used when no implementation or support exists for a requested filesystem scheme.

## Important APIs, Types, and Functions
Single message constructor; public stable exception type.

## Control Flow
No control flow; raised by filesystem lookup/initialization paths.

## State and Persistence Behavior
No persistent state beyond serialized exception fields.

## Dependencies and Integration Points
Integrated with FileSystem and AbstractFileSystem factory code and scheme resolution.

## Risks and Test Signals
Tests should cover unknown schemes and preserve message content used in diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedFileSystemException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedMultipartUploaderException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedMultipartUploaderException.java

## Purpose
Checked IOException indicating multipart upload is unavailable for a filesystem or path.

## Important APIs, Types, and Functions
Single message constructor; public stable type.

## Control Flow
No internal flow; callers throw when MultipartUploaderBuilder or filesystem capability paths cannot satisfy the request.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Integrated with MultipartUploader, MultipartUploaderBuilder, and filesystem capability code.

## Risks and Test Signals
Tests should assert unsupported stores fail with this type rather than generic IOException or UnsupportedOperationException.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UnsupportedMultipartUploaderException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UploadHandle.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UploadHandle.java

## Purpose
Opaque serializable handle for multipart upload IDs.

## Important APIs, Types, and Functions
bytes() returns a ByteBuffer view; default toByteArray() copies remaining bytes; equals(Object) is part of the contract.

## Control Flow
toByteArray obtains bytes(), allocates an array sized to remaining(), and consumes that returned buffer view with get().

## State and Persistence Behavior
State lives in implementations such as BBUploadHandle. Callers must treat the handle as opaque and serializable.

## Dependencies and Integration Points
Used by MultipartUploader startUpload/putPart/complete/abort and FileSystemMultipartUploader.

## Risks and Test Signals
Risk is mutable ByteBuffer position or backing array leakage. Tests should verify repeat toByteArray behavior for implementations and equality consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/UploadHandle.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/VectoredReadUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/VectoredReadUtils.java

## Purpose
Utility class for Hadoop vectored IO: validates ranges, supplies a default synchronous vectored read implementation, handles direct-buffer fallback reads, sorts/merges ranges, slices combined reads, and answers default vector capability probes.

## Important APIs, Types, and Functions
Key APIs: validateRangeRequest(), validateAndSortRanges(), readVectored(), readRangeFrom(), readInDirectBuffer(), isOrderedDisjoint(), roundDown(), roundUp(), mergeSortedRanges(), sliceTo(), hasVectorIOCapability().

## Control Flow
Default readVectored validates/sorts ranges then sets each FileRange future from readRangeFrom. readRangeFrom allocates a ByteBuffer, uses ByteBufferPositionedReadable when available, otherwise falls back to PositionedReadable array reads or chunked direct-buffer reads with a 64 KiB temp buffer. Range validation sorts inputs, rejects overlaps, negative lengths, negative offsets, and optional file-length overruns. mergeSortedRanges rounds to chunk boundaries and coalesces nearby reads through CombinedFileRange.

## State and Persistence Behavior
No durable state. It creates ByteBuffers/futures and calls a release consumer on read failure so caller-owned pools can reclaim buffers.

## Dependencies and Integration Points
Depends on FileRange, PositionedReadable, ByteBufferPositionedReadable, CombinedFileRange, StreamCapabilities, CompletableFuture, and Function4RaisingIOE. Filesystem implementations use it for common vector IO behavior.

## Risks and Test Signals
Risks include overlap math, integer truncation when combined ranges exceed int length, direct-buffer position/limit mistakes, and futures completed with leaked buffers on failure. Tests should cover empty lists, EOF boundaries, direct and heap buffers, merging thresholds, slicing offsets, and capability casing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/VectoredReadUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WindowsGetSpaceUsed.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WindowsGetSpaceUsed.java

## Purpose
Windows implementation of cached disk-usage accounting that avoids shelling out and uses DUHelper.

## Important APIs, Types, and Functions
Constructor accepts CachingGetSpaceUsed.Builder; refresh() sets used from DUHelper.getFolderUsage(getDirPath()).

## Control Flow
Superclass owns cache interval/jitter/initial value. refresh is invoked by the caching mechanism and atomically replaces the used counter.

## State and Persistence Behavior
Maintains only inherited cached used value. No persistence; it samples local filesystem usage.

## Dependencies and Integration Points
Depends on CachingGetSpaceUsed and DUHelper. Selected for Windows local space accounting.

## Risks and Test Signals
Risks are platform-specific path handling and DUHelper failures. Tests should cover builder initialization and refresh values for files/directories on Windows-like paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WindowsGetSpaceUsed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WithErasureCoding.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WithErasureCoding.java

## Purpose
Marker/extension interface for filesystems that expose erasure-coding policy queries and updates.

## Important APIs, Types, and Functions
getErasureCodingPolicyName(FileStatus) and setErasureCodingPolicy(Path,String).

## Control Flow
Implementations supply all behavior. Callers check filesystem instanceof WithErasureCoding before invoking.

## State and Persistence Behavior
No state in the interface. Implementations may mutate persistent filesystem metadata when setting policy.

## Dependencies and Integration Points
Integrates with FileSystem implementations and FileStatus-based EC reporting.

## Risks and Test Signals
Risks are null-on-error semantics for query hiding operational failures. Tests should verify supported/unsupported FS behavior and invalid policy/path errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/WithErasureCoding.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrCodec.java

## Purpose
Enum and helpers for extended-attribute value string encodings used by shell, HTTP, and JSON-facing paths.

## Important APIs, Types, and Functions
Enum values TEXT, HEX, BASE64; decodeValue(String); encodeValue(byte[], XAttrCodec).

## Control Flow
decodeValue recognizes quoted text, 0x/0X hex, 0s/0S base64, otherwise UTF-8 text. encodeValue emits prefixed hex/base64 or quoted UTF-8 text.

## State and Persistence Behavior
Stateless except a shared Commons Codec Base64 instance. Output bytes are caller-owned.

## Dependencies and Integration Points
Depends on commons-codec Hex/Base64 and StandardCharsets. Used by xattr CLI/web interfaces and filesystem xattr APIs.

## Risks and Test Signals
Risks include malformed hex wrapping, base64 leniency, quote handling without escaping, and null decode returning null. Tests should cover all prefixes, invalid hex, mixed case, empty values, and non-ASCII UTF-8.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrSetFlag.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrSetFlag.java

## Purpose
Enum modeling xattr create/replace preconditions.

## Important APIs, Types, and Functions
CREATE and REPLACE values carry short flags; validate(String, boolean, EnumSet<XAttrSetFlag>).

## Control Flow
validate requires a non-empty flag set. If the xattr exists, REPLACE must be present; if absent, CREATE must be present.

## State and Persistence Behavior
No mutable state. Persistent effect occurs in callers that perform xattr mutation after validation.

## Dependencies and Integration Points
Integrated with FileSystem xattr setters and NameNode-side xattr handling.

## Risks and Test Signals
Tests should cover create-only, replace-only, both flags, null/empty flags, and exception message paths for existing/non-existing attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/XAttrSetFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ZeroCopyUnavailableException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ZeroCopyUnavailableException.java

## Purpose
IOException used when zero-copy read support cannot be provided.

## Important APIs, Types, and Functions
Constructors accept message, message plus exception, or exception only.

## Control Flow
No internal flow; thrown by zero-copy/ByteBuffer read paths when prerequisites are missing.

## State and Persistence Behavior
No state beyond IOException cause/message.

## Dependencies and Integration Points
Related to FSDataInputStream enhanced ByteBuffer/zero-copy APIs.

## Risks and Test Signals
Tests should verify callers degrade or surface this exception consistently when zero-copy is disabled or unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ZeroCopyUnavailableException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditConstants.java

## Purpose
Central constant holder for audit parameter names and audit header fields.

## Important APIs, Types, and Functions
Constants include referrer origin, command, filesystem id, job/task/thread/process/principal/path/range/timestamp fields, and DELETE_KEYS_SIZE.

## Control Flow
No control flow; private constructor prevents instantiation.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Used by audit span/context/header implementations, especially S3A audit integration.

## Risks and Test Signals
Risks are string drift breaking log/header parsers. Tests should treat constants as compatibility surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditStatisticNames.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditStatisticNames.java

## Purpose
Constant holder for audit-related metric/statistic names.

## Important APIs, Types, and Functions
AUDIT_FAILURE, AUDIT_REQUEST_EXECUTION, AUDIT_SPAN_CREATION, AUDIT_ACCESS_CHECK_FAILURE.

## Control Flow
No flow; private constructor.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Integrated with filesystem audit metrics and statistics collectors.

## Risks and Test Signals
Tests should verify metrics producers and consumers use the same names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/AuditStatisticNames.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/CommonAuditContext.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/CommonAuditContext.java

## Purpose
Thread-local and global context map for audit spans. It carries common key/value data such as process id, current thread id, command entry point, and user-supplied audit attributes.

## Important APIs, Types, and Functions
Public APIs include currentAuditContext(), put/remove/get/reset/containsKey(), getEvaluatedEntries(), global set/get/remove, getGlobalContextEntries(), currentThreadID(), and noteEntryPoint(Object).

## Control Flow
A static process UUID is installed globally under PARAM_PROCESS. ACTIVE_CONTEXT lazily creates one CommonAuditContext per thread and init() adds PARAM_THREAD1 as a dynamic supplier. put(String,String) stores constant suppliers; put(String,Supplier) stores dynamic suppliers. noteEntryPoint records the simple class name under PARAM_COMMAND if absent.

## State and Persistence Behavior
Global state is a ConcurrentHashMap shared by all threads. Per-thread context stores Supplier<String> values in a ConcurrentHashMap and may be retained by audit spans crossing thread boundaries. No durable persistence.

## Dependencies and Integration Points
Depends on AuditConstants, ThreadLocal, ConcurrentHashMap, UUID, and SLF4J. Used by filesystem audit spans and HTTP referrer audit header construction.

## Risks and Test Signals
Main risks are supplier memory retention, supplier thread-safety, global context overuse, and stale thread-local entries in pooled threads. Tests should cover reset, dynamic thread IDs, concurrent global iteration, noteEntryPoint idempotence, and supplier evaluation after span handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/CommonAuditContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/package-info.java

## Purpose
Package documentation and audience/stability annotations for common filesystem audit support.

## Important APIs, Types, and Functions
No runtime APIs; declares package org.apache.hadoop.fs.audit with Public/Unstable annotations.

## Control Flow
No control flow.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Defines package-level contract for audit context/constants consumed by filesystem connectors.

## Risks and Test Signals
Risk is documentation/annotation drift. Compile/package annotation checks are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/audit/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataInputStream.java

## Purpose
FSDataInputStream wrapper that decrypts data through Hadoop CryptoInputStream while preserving FSDataInputStream API shape.

## Important APIs, Types, and Functions
Two constructors accept FSDataInputStream, CryptoCodec, key, IV, and optional buffer size.

## Control Flow
Constructor wraps the source stream in CryptoInputStream and passes it to FSDataInputStream super.

## State and Persistence Behavior
No added state; CryptoInputStream owns cipher position and delegates reads to the underlying stream.

## Dependencies and Integration Points
Depends on CryptoCodec, CryptoInputStream, and FSDataInputStream. Used by encryption-aware filesystems.

## Risks and Test Signals
Risks are cipher position/IV correctness and preserving seek/position behavior from the wrapped stream. Tests should read with/without explicit buffer size and verify close propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataOutputStream.java

## Purpose
FSDataOutputStream wrapper that encrypts writes with CryptoOutputStream and delegates position reporting to the original FSDataOutputStream.

## Important APIs, Types, and Functions
Constructors accept FSDataOutputStream, CryptoCodec, key/IV, optional buffer size, and closeOutputStream flag; getPos() returns fsOut.getPos().

## Control Flow
Constructors seed CryptoOutputStream with the current underlying output position and pass the same start position to FSDataOutputStream super. getPos bypasses wrapper counters.

## State and Persistence Behavior
Stores a strong reference to the underlying fsOut. Persistent effect is encrypted bytes written to the delegate stream.

## Dependencies and Integration Points
Depends on CryptoCodec, CryptoOutputStream, FSDataOutputStream. Used by encryption layers over filesystem output streams.

## Risks and Test Signals
Risks include mismatched position when appending, close propagation when closeOutputStream=false, and getPos accuracy after buffered crypto writes. Tests should cover append offsets, flush/close, and position reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/crypto/CryptoFSDataOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPException.java

## Purpose
Runtime exception for FTP filesystem failures that occur in contexts not declaring checked IOExceptions.

## Important APIs, Types, and Functions
Constructors accept message, cause, or message plus cause.

## Control Flow
No flow; wraps FTP client state/cleanup failures.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Used by FTPFileSystem and FTPInputStream for connection and transfer-completion errors.

## Risks and Test Signals
Tests should verify close/home-directory failure paths preserve causes and messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPFileSystem.java

## Purpose
FileSystem implementation backed by Apache Commons Net FTPClient. It supports basic open, create, delete, listStatus, getFileStatus, mkdirs, and same-directory rename over FTP.

## Important APIs, Types, and Functions
Important APIs: initialize(), connect()/disconnect(), open(), create(), delete(), listStatus(), getFileStatus(), mkdirs(), rename(), getHomeDirectory(), getTransferMode(), setDataConnectionMode(), setTimeout().

## Control Flow
initialize resolves host/port/user/password from URI overriding configuration. Most operations open a new FTPClient, perform the command, then disconnect in finally. open/create are special: they change to the parent directory, obtain retrieveFileStream/storeFileStream, and return streams that hold the FTPClient until close; close must completePendingCommand then logout/disconnect. delete recurses when requested. getFileStatus lists the parent directory and converts FTPFile metadata to FileStatus. rename refuses missing sources, existing destinations, renames under self, and cross-directory moves.

## State and Persistence Behavior
The FileSystem itself stores only URI/config and no working directory; remote server state is persistent data/directories/files. Stream instances own live FTP connections until closed.

## Dependencies and Integration Points
Depends on commons-net FTPClient/FTPFile/FTPReply, Hadoop FileSystem, FileStatus, FsPermission/FsAction, IOUtils, NetUtils, and configuration keys. FtpFs delegates to it through DelegateToFileSystem.

## Risks and Test Signals
Risks are connection leaks if streams are not closed, blocking FTP commands while a transfer stream is open, path qualification bugs, recursive delete path construction, weak credential parsing with colon characters, and same-directory rename limitations. Tests should use a controllable FTP server to cover passive/active modes, transfer modes, create overwrite, failed preliminary replies, close completion failures, recursive delete, root status, and rename edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPInputStream.java

## Purpose
FSInputStream wrapper around an FTP retrieveFileStream that tracks position/statistics and completes the pending FTP command on close.

## Important APIs, Types, and Functions
getPos(), read(), read(byte[],int,int), close(), seek/seekToNewSource unsupported, mark/reset unsupported.

## Control Flow
Constructor validates non-null stream and connected client. Reads delegate to wrappedStream and increment pos/statistics for positive reads. close is synchronized/idempotent, calls completePendingCommand(), logout(), disconnect(), then fails if command completion was not positive.

## State and Persistence Behavior
Stores wrapped InputStream, FTPClient, FileSystem.Statistics, closed flag, and byte position. Remote connection remains live until close.

## Dependencies and Integration Points
Created by FTPFileSystem.open(). Depends on Commons Net FTPClient and Hadoop FSInputStream statistics.

## Risks and Test Signals
Risks are transfer completion ordering, exceptions during logout/disconnect, double close behavior, and no seek support. Tests should cover byte counts, stats increments, read after close, and failed completePendingCommand.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FTPInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpConfigKeys.java

## Purpose
Configuration defaults for the FTP filesystem server defaults surface.

## Important APIs, Types, and Functions
Constants for block size, replication, buffer size, checksum, trash interval, encryption transfer default, and key provider URI; getServerDefaults().

## Control Flow
getServerDefaults creates FsServerDefaults using FTP-specific defaults and DataChecksum.Type.CRC32.

## State and Persistence Behavior
No mutable state.

## Dependencies and Integration Points
Depends on CommonConfigurationKeys, FsServerDefaults, ChecksumFileSystem, and DataChecksum. Used by FtpFs getServerDefaults.

## Risks and Test Signals
Risk is defaults diverging from FTPFileSystem assumptions. Tests should assert default values and checksum type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpFs.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpFs.java

## Purpose
DelegateToFileSystem adapter exposing ftp:// through the AbstractFileSystem/FileContext API.

## Important APIs, Types, and Functions
Constructor creates FTPFileSystem delegate; getUriDefaultPort(); getServerDefaults() overloads.

## Control Flow
Construction passes URI, FTPFileSystem, conf, scheme ftp, authority requirements, and default port. Server defaults are returned from FtpConfigKeys.

## State and Persistence Behavior
No own persistent state beyond DelegateToFileSystem base fields. Marked deprecated/evolving.

## Dependencies and Integration Points
Depends on FTPFileSystem, DelegateToFileSystem, AbstractFileSystem, FsConstants, FtpConfigKeys.

## Risks and Test Signals
Tests should verify FileContext ftp initialization, default port, and server defaults. Deprecated status means compatibility should be preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ftp/FtpFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/AbstractHttpFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/AbstractHttpFileSystem.java

## Purpose
Minimal read-only FileSystem for http/https URLs. It opens URLConnection streams and rejects mutation/list/seek operations.

## Important APIs, Types, and Functions
initialize(), getUri(), open(), getFileStatus(), getWorkingDirectory(), mkdirs(), hasPathCapability(), nested HttpDataInputStream implementing Seekable and PositionedReadable but throwing unsupported for positional APIs.

## Control Flow
open qualifies the path, opens a URLConnection, and wraps the input in FSDataInputStream. getFileStatus returns a synthetic non-directory status with unknown length. hasPathCapability reports FS_READ_ONLY_CONNECTOR true after argument validation.

## State and Persistence Behavior
Stores initialized URI only. It reads remote HTTP data but does not persist or cache state.

## Dependencies and Integration Points
Depends on URLConnection, FileSystem, CommonPathCapabilities, PathCapabilitiesSupport. HttpFileSystem and HttpsFileSystem provide schemes.

## Risks and Test Signals
Risks are lack of seek/positioned reads despite interface implementation, unknown length metadata, no listStatus, and URLConnection error handling. Tests should cover open success/failure, read-only capability, and UnsupportedOperationException for writes/seeks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/AbstractHttpFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/HttpFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/HttpFileSystem.java

## Purpose
Concrete HTTP scheme filesystem.

## Important APIs, Types, and Functions
getScheme() returns http.

## Control Flow
All behavior inherited from AbstractHttpFileSystem.

## State and Persistence Behavior
No additional state.

## Dependencies and Integration Points
Registered/used as the http:// FileSystem implementation.

## Risks and Test Signals
Tests should verify scheme and inherited read-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/HttpFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/HttpsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/HttpsFileSystem.java

## Purpose
Concrete HTTPS scheme filesystem.

## Important APIs, Types, and Functions
getScheme() returns https.

## Control Flow
All behavior inherited from AbstractHttpFileSystem.

## State and Persistence Behavior
No additional state.

## Dependencies and Integration Points
Registered/used as the https:// FileSystem implementation.

## Risks and Test Signals
Tests should verify scheme, TLS URL opening through URLConnection, and inherited read-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/HttpsFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/package-info.java

## Purpose
Package documentation for HTTP/HTTPS filesystem connectors.

## Important APIs, Types, and Functions
No runtime APIs; package declaration only.

## Control Flow
No control flow.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Documents the org.apache.hadoop.fs.http connector package.

## Risks and Test Signals
Compile/package documentation checks are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/http/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractFSBuilderImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractFSBuilderImpl.java

## Purpose
Generic FSBuilder base class carrying either a Path or PathHandle plus optional and mandatory configuration options.

## Important APIs, Types, and Functions
Constructors for Optional<Path>/Optional<PathHandle>, Path, PathHandle; opt/must overloads for strings, primitives, arrays; getOptions(), getMandatoryKeys(), getOptionalKeys(), rejectUnknownMandatoryKeys().

## Control Flow
Construction rejects providing both path and path handle. opt removes the key from mandatory and records it optional; must records it mandatory and may remove optional for arrays. Values are stored in a non-default-loading Configuration. rejectUnknownMandatoryKeys checks all mandatory keys against known keys.

## State and Persistence Behavior
Stores immutable optional path/pathHandle and mutable option Configuration plus key sets. No persistence.

## Dependencies and Integration Points
Base for FutureDataInputStreamBuilderImpl, MultipartUploaderBuilderImpl, and filesystem-specific builders.

## Risks and Test Signals
Risks are type narrowing in float/double overloads that call optLong/mustLong, mandatory/optional set consistency, and unknown-key validation order. Tests should cover all overloads, path/pathHandle exclusivity, and mandatory rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractFSBuilderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractMultipartUploader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractMultipartUploader.java

## Purpose
Base class for MultipartUploader implementations with shared argument validation.

## Important APIs, Types, and Functions
close(), getBasePath(), checkPath(), checkUploadId(), checkPartHandles(), checkPutArguments(), abortUploadsUnderPath().

## Control Flow
checkPath requires target string to start with base path string. checkPartHandles rejects empty maps and non-positive part indexes. abortUploadsUnderPath returns a completed future with -1 after path validation.

## State and Persistence Behavior
Stores immutable basePath only. Subclasses own upload state.

## Dependencies and Integration Points
Used by FileSystemMultipartUploader and other multipart uploader implementations.

## Risks and Test Signals
Risks are string-prefix path validation accepting sibling prefixes and default abortUploadsUnderPath sentinel behavior. Tests should validate path boundaries and argument failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/AbstractMultipartUploader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/BackReference.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/BackReference.java

## Purpose
Small holder for a strong object reference attached to streams/stores to prevent premature garbage collection.

## Important APIs, Types, and Functions
Constructor accepts nullable Object; isNull(); toString().

## Control Flow
No flow beyond storing and reporting reference presence.

## State and Persistence Behavior
Stores a final reference for object lifetime; no persistence.

## Dependencies and Integration Points
Used as a lifecycle helper where only side-effect is retaining an object.

## Risks and Test Signals
Risks are accidental exposure through toString and reliance on GC behavior. Tests are simple null/non-null coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/BackReference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/CombinedFileRange.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/CombinedFileRange.java

## Purpose
FileRangeImpl subclass representing one physical read covering multiple logical FileRange requests for vectored IO.

## Important APIs, Types, and Functions
Constructor, getUnderlying(), merge(), getDataSize(), toString().

## Control Flow
Constructor sets offset/length from rounded start/end and appends the original. merge checks gap against minSeek and total size against maxSize, updates length, and appends underlying range if compatible.

## State and Persistence Behavior
Maintains mutable length, underlying list, and dataSize for optimization accounting. No persistence.

## Dependencies and Integration Points
Created by VectoredReadUtils.mergeSortedRanges and consumed by filesystem vector read implementations.

## Risks and Test Signals
Risks include int length overflow, exposing mutable underlying list, and merge threshold off-by-one. Tests should cover adjacent, overlapping, far apart, maxSize, and dataSize calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/CombinedFileRange.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/DefaultBulkDeleteOperation.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/DefaultBulkDeleteOperation.java

## Purpose
Default BulkDelete implementation that degrades bulk delete to one non-recursive FileSystem.delete call.

## Important APIs, Types, and Functions
pageSize() returns 1; basePath(); bulkDelete(Collection<Path>); close().

## Control Flow
bulkDelete validates paths with page size 1 and basePath, then deletes the sole path with recursive=false. IOException is caught and returned as a path/error pair.

## State and Persistence Behavior
Stores basePath and FileSystem delegate. Persistent effect is deletion through the delegate filesystem.

## Dependencies and Integration Points
Depends on BulkDelete, BulkDeleteUtils.validateBulkDeletePaths, FileSystem, Tuples, and SLF4J.

## Risks and Test Signals
Risks are ignoring false delete returns, non-recursive behavior, and validation assumptions. Tests should cover empty input, too many paths, outside-base paths, delete exception, and delete false return semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/DefaultBulkDeleteOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FSBuilderSupport.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FSBuilderSupport.java

## Purpose
Helper for parsing numeric options from FSBuilder option Configuration with resilient fallback logging.

## Important APIs, Types, and Functions
Constructor/getOptions(); getPositiveLong(); getLong(); static LOG_PARSE_ERROR.

## Control Flow
getLong returns default for empty key, parses with Configuration.getLong, catches NumberFormatException, logs once, and returns default. getPositiveLong additionally replaces negative values with default.

## State and Persistence Behavior
Stores the builder options Configuration. No persistence.

## Dependencies and Integration Points
Used by open/create builder implementations that accept string options.

## Risks and Test Signals
Risks are silent fallback for invalid mandatory-like options and LogExactlyOnce suppressing repeated diagnostics. Tests should cover empty, valid, invalid, and negative values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FSBuilderSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileRangeImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileRangeImpl.java

## Purpose
Default mutable implementation of FileRange with offset, length, associated future, and optional caller reference.

## Important APIs, Types, and Functions
Constructor, getOffset(), getLength(), setOffset(), setLength(), setData(), getData(), getReference(), toString().

## Control Flow
No validation in setters/constructor; validation is expected in VectoredReadUtils or callers. setData stores a CompletableFuture<ByteBuffer> returned to clients.

## State and Persistence Behavior
Stores mutable range metadata and future. No persistence.

## Dependencies and Integration Points
Used by FileRange factory paths and CombinedFileRange.

## Risks and Test Signals
Risks are invalid offset/length being set and future replacement races. Tests should cover factory validation and reference preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileRangeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploader.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploader.java

## Purpose
MultipartUploader built from basic FileSystem primitives: create a temporary collector directory, write each part as a file, concat parts, rename final output, and delete the collector.

## Important APIs, Types, and Functions
startUpload(), putPart()/innerPutPart(), complete()/innerComplete(), abort(), createCollectorPath(), getPathHandle(), totalPartsLen().

## Control Flow
startUpload creates a collector path under the target parent/name prefix and returns it as BBUploadHandle. putPart decodes uploadId to collector path, writes N.part with builder settings, copies the input stream, and closes it. complete validates handles, sorts by part number, detects duplicate part paths, creates empty file for zero total length or concats part files into a collector final file then renames over target, deletes collector, and returns a PathHandle. abort verifies collector exists and deletes it.

## State and Persistence Behavior
Remote/persistent state is the collector directory, part files, final file, and deletion/rename effects. Returned handles serialize paths as UTF-8 bytes.

## Dependencies and Integration Points
Depends on FileSystem createFile/concat/delete/getPathHandle, InternalOperations rename, BBUploadHandle/BBPartHandle, FutureIO, Commons IOUtils, and builder options.

## Risks and Test Signals
Risks include path-encoded handles being forgeable, collector path collisions/name splitting at dots, concat availability, partial cleanup on failure, empty-file overwrite semantics, and synchronous work inside completed futures. Tests should cover part ordering, duplicate handles, abort, zero-length upload, concat failure cleanup, and permission/checksum/block-size propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploaderBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploaderBuilder.java

## Purpose
Concrete builder for FileSystemMultipartUploader.

## Important APIs, Types, and Functions
Constructor; getThisBuilder(); build(); public getters exposing FS, permission, buffer size, replication, flags, checksum, block size.

## Control Flow
build instantiates FileSystemMultipartUploader with this builder and filesystem. Other methods expose protected base state to the uploader.

## State and Persistence Behavior
Stores state in MultipartUploaderBuilderImpl base only.

## Dependencies and Integration Points
Used by FileSystem multipart upload factory paths.

## Risks and Test Signals
Tests should verify builder defaults from filesystem, fluent setters, and build creates uploader with qualified base path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FileSystemMultipartUploaderBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FlagSet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FlagSet.java

## Purpose
Generic enum flag container that can be built from configuration and probed as StreamCapabilities.

## Important APIs, Types, and Functions
createFlagSet overloads, buildFlagSet(), enable/disable/set(), enabled(), flags(), hasCapability(), makeImmutable(), pathCapabilities(), copy(), toConfigurationString(), equals/hashCode.

## Control Flow
Constructor copies initial flags and maps prefixed enum names to values. Mutations check the immutable AtomicBoolean. hasCapability resolves capability strings through the prefixed map. buildFlagSet delegates parsing to Configuration.getEnumSet.

## State and Persistence Behavior
Mutable until makeImmutable; after that mutation methods throw. No persistence except configuration string serialization.

## Dependencies and Integration Points
Depends on ConfigurationHelper, Configuration, StreamCapabilities, EnumSet. Useful for filesystem feature flags and path capability exposure.

## Risks and Test Signals
Risks include no synchronization while mutable, hashCode considering only flags while equals includes enumClass/prefix, capability case conventions, and immutable copy behavior. Tests should cover parsing, unknown values, capability names, immutability, equals/hashCode contract, and concurrent read after immutable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FlagSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FsLinkResolution.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FsLinkResolution.java

## Purpose
Lambda-friendly adapter over FSLinkResolver for FileContext symlink resolution.

## Important APIs, Types, and Functions
FsLinkResolutionFunction<T>; constructor; next(AbstractFileSystem,Path); static resolve(FileContext,Path,fn).

## Control Flow
FSLinkResolver drives resolution and invokes next for each resolved AbstractFileSystem/path; next delegates to the supplied function.

## State and Persistence Behavior
Stores one function reference. No persistence.

## Dependencies and Integration Points
Depends on FSLinkResolver, FileContext, AbstractFileSystem, Path, UnresolvedLinkException.

## Risks and Test Signals
Risks are exception propagation and null function rejection. Tests should cover successful resolution, unresolved links, and IOException passthrough.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FsLinkResolution.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FunctionsRaisingIOE.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FunctionsRaisingIOE.java

## Purpose
Deprecated compatibility holder for functional interfaces that throw IOException.

## Important APIs, Types, and Functions
FunctionRaisingIOE, BiFunctionRaisingIOE, CallableRaisingIOE.

## Control Flow
No flow beyond functional method invocation by callers.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Superseded by org.apache.hadoop.util.functional equivalents, retained for binary/source compatibility.

## Risks and Test Signals
Risk is removal or signature drift breaking external filesystem implementations. Compile compatibility tests are the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FunctionsRaisingIOE.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureDataInputStreamBuilderImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureDataInputStreamBuilderImpl.java

## Purpose
Base builder for asynchronous FSDataInputStream open operations returning CompletableFuture<FSDataInputStream>.

## Important APIs, Types, and Functions
Constructors for FileContext+Path, FileSystem+Path, FileSystem+PathHandle; bufferSize(); builder(); getThisBuilder(); withFileStatus(); protected getFS/getBufferSize/getStatus.

## Control Flow
FileSystem constructors initialize buffer size from IO_FILE_BUFFER_SIZE_KEY. FileContext constructor has no FileSystem and uses default buffer size. withFileStatus stores optional status for implementations to skip metadata probes.

## State and Persistence Behavior
Stores FileSystem reference, buffer size, optional FileStatus, plus AbstractFSBuilderImpl option/path state. No persistence.

## Dependencies and Integration Points
Base for filesystem-specific openFile builders and FutureDataInputStreamBuilder API.

## Risks and Test Signals
Risks are null fileSystem for FileContext path if subclasses call getFS, stale FileStatus, and buffer size validation absent. Tests should cover constructor variants and fluent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureDataInputStreamBuilderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureIOSupport.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureIOSupport.java

## Purpose
Deprecated compatibility facade over org.apache.hadoop.util.functional.FutureIO.

## Important APIs, Types, and Functions
awaitFuture overloads, raiseInnerCause overloads, propagateOptions overloads, eval().

## Control Flow
Every method delegates to FutureIO, preserving older linkage while centralizing actual future handling in FutureIO.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by external or older filesystem implementations that imported this class.

## Risks and Test Signals
Risks are compatibility/linkage regressions and exception conversion mismatches. Tests should compare behavior with FutureIO for IO, runtime, interrupted, timeout, and completion failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/FutureIOSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/LeakReporter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/LeakReporter.java

## Purpose
Closeable leak sentinel that reports unclosed resources through a dedicated resource-leaks logger and optional cleanup action.

## Important APIs, Types, and Functions
Constructor captures resource description, BooleanSupplier isOpen, and RunnableRaisingIOE closeAction; close(); getLeakException(); isClosed(); toString(); finalize/reporting behavior through leak exception stack.

## Control Flow
An AtomicBoolean ensures close action runs once. If the object is finalized while isOpen reports true, it logs a leak with the captured allocation exception and invokes closeAction.

## State and Persistence Behavior
Stores closed flag, supplier, close action, and allocation stack exception. No persistence, but affects cleanup of leaked resources.

## Dependencies and Integration Points
Depends on SLF4J, RunnableRaisingIOE, BooleanSupplier, AtomicBoolean. Used by FS stream/store code to detect lifecycle leaks.

## Risks and Test Signals
Risks include finalizer timing, closeAction throwing, false positives from isOpen suppliers, and strong references captured in suppliers. Tests should cover idempotent close, leak exception presence, and close action invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/LeakReporter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/MultipartUploaderBuilderImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/MultipartUploaderBuilderImpl.java

## Purpose
Generic builder base for MultipartUploader implementations, carrying file creation options and filesystem defaults.

## Important APIs, Types, and Functions
Constructors for FileContext/Path and FileSystem/Path; permission(), bufferSize(), replication(), blockSize(), create(), overwrite(), append(), checksumOpt(); protected getters.

## Control Flow
FileContext constructor reads FsServerDefaults; FileSystem constructor qualifies path and reads defaults from FS/conf. Fluent setters mutate stored fields. create/overwrite/append update CreateFlag set.

## State and Persistence Behavior
Stores FileSystem, permission, buffer size, replication, block size, CreateFlag set, checksum option. Persistent effects occur only when built uploader uses these values.

## Dependencies and Integration Points
Base for FileSystemMultipartUploaderBuilder and any FS-specific multipart builder.

## Risks and Test Signals
Risks are FileContext constructor leaving fs null, no validation on numeric setters, and unused flags in some uploaders. Tests should verify defaults and propagation into created part files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/MultipartUploaderBuilderImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/OpenFileParameters.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/OpenFileParameters.java

## Purpose
Bean-style parameter carrier for openFileWithOptions implementations.

## Important APIs, Types, and Functions
withMandatoryKeys(), withOptionalKeys(), withOptions(), withBufferSize(), withStatus(); getters for all fields.

## Control Flow
Fluent setters require non-null key sets/options, assign fields, and return this. Status may be null.

## State and Persistence Behavior
Stores references to provided sets/config/status rather than defensive copies. No persistence.

## Dependencies and Integration Points
Used to pass FutureDataInputStreamBuilder state into filesystem open implementations.

## Risks and Test Signals
Risks are caller mutation of sets/config after handoff and unset fields. Tests should cover null rejection and reference semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/OpenFileParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/PathCapabilitiesSupport.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/PathCapabilitiesSupport.java

## Purpose
Shared validation/normalization helper for PathCapabilities.hasPathCapability arguments.

## Important APIs, Types, and Functions
validatePathCapabilityArgs(Path,String).

## Control Flow
Checks path and capability are non-null and capability non-empty, then lowercases capability with Locale.ENGLISH for switch-friendly matching.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by AbstractHttpFileSystem and other PathCapabilities implementations.

## Risks and Test Signals
Tests should cover null/empty inputs, locale-stable lowercasing, and capability switch matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/PathCapabilitiesSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/StoreImplementationUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/StoreImplementationUtils.java

## Purpose
Utilities for stream capability probing in filesystem store implementations.

## Important APIs, Types, and Functions
isProbeForSyncable(), hasCapability(OutputStream,String), hasCapability(InputStream,String), package-private objectHasCapability().

## Control Flow
isProbeForSyncable compares against HSYNC/HFLUSH ignoring case. hasCapability delegates only if the object implements StreamCapabilities.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by FSData streams and store code to answer hsync/hflush and other capability probes.

## Risks and Test Signals
Risks are null capability handling and case behavior. Tests should cover StreamCapabilities and plain streams, hsync/hflush probes, and unsupported capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/StoreImplementationUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/TrackingByteBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/TrackingByteBufferPool.java

## Purpose
Testing ByteBufferPool wrapper that tracks allocations/releases and throws on leaked or foreign buffers.

## Important APIs, Types, and Functions
wrap(); getBuffer(); putBuffer(); containsBuffer(); size(); close(); allocation/release/leak exception types; counters getters.

## Control Flow
getBuffer delegates allocation, records buffer identity in an IdentityHashMap with optional stack trace, and increments allocation count. putBuffer removes by identity, throws if absent, returns to delegate, clears buffer, and increments release count. close logs any unreleased buffers, clears references, and throws LeakedByteBufferException.

## State and Persistence Behavior
Stores live buffer identities, wrapped allocator, and counters. No persistence; close releases references for GC.

## Dependencies and Integration Points
Used in vector IO and buffer-pool tests. Depends on ByteBufferPool and SLF4J.

## Risks and Test Signals
Risks include unsynchronized containsBuffer/size/close against synchronized get/put, clearing after delegate release, and DEBUG stacktrace overhead. Tests should cover leak detection, double release, foreign buffer release, counters, and direct/heap buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/TrackingByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/VectorIOBufferPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/VectorIOBufferPool.java

## Purpose
Function-backed ByteBufferPool adapter for vectored IO allocation and release callbacks.

## Important APIs, Types, and Functions
Constructor takes IntFunction<ByteBuffer> allocate and Consumer<ByteBuffer> release; getBuffer(); putBuffer().

## Control Flow
getBuffer ignores the direct flag and calls allocate(length). putBuffer ignores null and otherwise calls release.

## State and Persistence Behavior
Stores two function references. No persistence.

## Dependencies and Integration Points
Used to adapt FileRange allocation/release callbacks into APIs expecting ByteBufferPool.

## Risks and Test Signals
Risks are direct flag being ignored and release callback behavior for reused buffers. Tests should verify null release, callback invocation, and length forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/VectorIOBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakRefMetricsSource.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakRefMetricsSource.java

## Purpose
MetricsSource wrapper that weakly references the real source to avoid keeping large filesystem objects alive after close.

## Important APIs, Types, and Functions
Constructor, getMetrics(), getName(), getSource(), toString().

## Control Flow
getMetrics resolves the weak reference and delegates only if still live; otherwise it emits no metrics.

## State and Persistence Behavior
Stores name and WeakReference<MetricsSource>. State may disappear after GC if no strong references remain.

## Dependencies and Integration Points
Integrates with Hadoop metrics2 registries that need a source object but should not force retention.

## Risks and Test Signals
Risks are metrics silently disappearing if no strong owner exists and unregister code needing the name. Tests should cover delegation and GC-cleared behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakRefMetricsSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakReferenceThreadMap.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakReferenceThreadMap.java

## Purpose
Thread-id keyed WeakReferenceMap convenience class for per-thread values without strong retention.

## Important APIs, Types, and Functions
getForCurrentThread(), removeForCurrentThread(), currentThreadId(), setForCurrentThread().

## Control Flow
Methods use current Thread.getId as key. setForCurrentThread avoids replacing when the existing weak reference resolves to the same object; otherwise it puts the new value and returns old.

## State and Persistence Behavior
Stores weak references in superclass; values may be GCd and referenceLost callback may run.

## Dependencies and Integration Points
Depends on org.apache.hadoop.util.WeakReferenceMap. Useful for thread-local-like caches with cleanup hooks.

## Risks and Test Signals
Risks are thread id reuse, GC timing, and non-null requirement on set. Tests should cover same-object set, replacement, remove, factory creation, and reference-lost callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WeakReferenceThreadMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WrappedIOException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WrappedIOException.java

## Purpose
Deprecated UncheckedIOException subclass for wrapping IOException in APIs that cannot throw checked exceptions.

## Important APIs, Types, and Functions
Constructor requires IOException cause.

## Control Flow
No flow beyond Preconditions.checkNotNull(cause) and superclass initialization.

## State and Persistence Behavior
No state beyond wrapped cause.

## Dependencies and Integration Points
Retained for compatibility; replaced generally by standard UncheckedIOException usage.

## Risks and Test Signals
Tests should verify null rejection and cause preservation for compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/WrappedIOException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/package-info.java

## Purpose
Package documentation for unstable internal filesystem implementation helpers.

## Important APIs, Types, and Functions
No runtime APIs; package annotated LimitedPrivate/Unstable.

## Control Flow
No control flow.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Covers org.apache.hadoop.fs.impl helper classes used by filesystem connectors.

## Risks and Test Signals
Compile/package annotation checks and documentation consistency are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockCache.java

## Purpose
Interface for local block cache implementations used by prefetching input streams.

## Important APIs, Types, and Functions
containsBlock(), blocks(), size(), get(blockNumber, ByteBuffer), put(blockNumber, ByteBuffer, Configuration, LocalDirAllocator), close().

## Control Flow
Implementations decide storage. get copies cached content into caller buffer; put persists one block into cache using configuration and local directory allocation.

## State and Persistence Behavior
Interface has no state. Implementations may persist cache files on local disk.

## Dependencies and Integration Points
Depends on ByteBuffer, Configuration, LocalDirAllocator. Used by caching/prefetch block managers.

## Risks and Test Signals
Tests for implementations should cover block presence, buffer position/limit, overwrite behavior, close cleanup, and local directory failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockData.java

## Purpose
Represents block geometry and per-block readiness state for a file read through prefetching.

## Important APIs, Types, and Functions
State enum NOT_READY/QUEUED/READY/CACHED; constructor; getBlockSize/getFileSize/getNumBlocks; isLastBlock; getBlockNumber; getSize; isValidOffset; getStartOffset; getRelativeOffset; getState/setState; getStateString().

## Control Flow
Constructor validates file/block sizes, computes numBlocks by ceiling division, and initializes every block NOT_READY. Offset/block accessors validate ranges. Last block size is shortened to remaining file bytes.

## State and Persistence Behavior
Stores immutable fileSize/blockSize/numBlocks and mutable State[] per block. No persistence.

## Dependencies and Integration Points
Used by BlockManager and caching/prefetch managers to coordinate reads.

## Risks and Test Signals
Risks include zero-length file edge cases, int truncation for huge block counts, offset end boundary validation, and unsynchronized state mutation. Tests should cover zero file, exact multiple, partial last block, invalid offsets, and state strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockManager.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockManager.java

## Purpose
Simplest block manager abstraction: reads whole blocks into fresh ByteBuffers and offers no-op hooks for prefetching/caching.

## Important APIs, Types, and Functions
Constructor; getBlockData(); get(int); abstract read(ByteBuffer,long,int); release(); requestPrefetch(); cancelPrefetches(); requestCaching(); close().

## Control Flow
get validates block number, allocates a heap buffer sized from BlockData, invokes subclass read, flips the buffer, and wraps it in BufferData. Optional hooks are no-ops in the base class.

## State and Persistence Behavior
Stores BlockData only. Persistent state depends on subclass read source; base does not cache.

## Dependencies and Integration Points
Base class for prefetch/caching block managers.

## Risks and Test Signals
Risks are short reads not checked by base get, heap allocation per block, and no-op release. Tests should simulate read implementations including short/error reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockManagerParameters.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockManagerParameters.java

## Purpose
Mutable builder-style parameter bag for constructing richer BlockManager implementations.

## Important APIs, Types, and Functions
Getters and with* setters for futurePool, blockData, bufferPoolSize, prefetchingStatistics, conf, localDirAllocator, maxBlocksCount, trackerFactory.

## Control Flow
Each with* method assigns the reference/value and returns this. No validation is performed here.

## State and Persistence Behavior
Stores references to configuration, pools, statistics, allocator, and block metadata. No persistence.

## Dependencies and Integration Points
Used by prefetching/caching block manager constructors.

## Risks and Test Signals
Risks are missing/null required parameters and invalid sizes being detected later. Tests should cover fluent assignment and constructor validation in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockManagerParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockOperations.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockOperations.java

## Purpose
Debug/analysis recorder for block-level prefetch/cache/read operations and operation durations.

## Important APIs, Types, and Functions
Kind enum with short names; Operation and End records; methods for each operation kind; end(); getSummary(); getDurationInfo(); analyze(); fromSummary().

## Control Flow
Operation methods validate non-negative block IDs where applicable and append timestamped records. end wraps a start op and computes duration. getSummary emits compact tokens or debug lines plus duration stats. analyze groups operations per block to detect missing end events, repeated operations, prefetched-not-used, and cached-not-used. fromSummary parses compact tokens back into operations.

## State and Persistence Behavior
Stores an ArrayList of operations and debugMode. No persistence except summary strings used in logs/tests.

## Dependencies and Integration Points
Used by prefetch BlockManager implementations for diagnostics; can be removed without functional effect.

## Risks and Test Signals
Risks are parser mismatch with summary format, unsynchronized static short-name map initialization, and missing end-op matching. Tests should round-trip summaries, analyze anomalies, and verify duration statistics with end records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BlockOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BoundedResourcePool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BoundedResourcePool.java

## Purpose
Fixed-size resource pool that lazily creates resources, reuses returned resources, and blocks when exhausted.

## Important APIs, Types, and Functions
acquire(), tryAcquire(), release(), close(), numCreated(), numAvailable(), toString(), abstract createNew(), protected close(T).

## Control Flow
acquire first polls available items, then creates a new item under capacity, otherwise blocks on the queue. tryAcquire follows the same path but returns null instead of blocking. release validates identity membership, ignores duplicate release already in queue, then puts the item back. close calls close(item) for all created resources and clears structures.

## State and Persistence Behavior
Stores capacity, ArrayBlockingQueue, and identity-based set of created resources. After close, fields are nulled.

## Dependencies and Integration Points
Base for buffer/cache pools in prefetching code.

## Risks and Test Signals
Risks are use-after-close NPEs, release blocking invariant, interrupted acquire returning null, and duplicate-release semantics. Tests should cover capacity, blocking/try behavior, foreign resource rejection, duplicate release, and close cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BoundedResourcePool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BufferData.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BufferData.java

## Purpose
Stateful wrapper for one block ByteBuffer used by caching/prefetching block managers. It enforces buffer lifecycle transitions and detects data mutation after readiness.

## Important APIs, Types, and Functions
State enum UNKNOWN/BLANK/PREFETCHING/CACHING/READY/DONE; constructor; getters; getChecksum(); setPrefetch(); setCaching(); setReady(); setDone(); updateState(); throwIfStateIncorrect(); stateEqualsOneOf(); toString().

## Control Flow
Buffers start BLANK. setPrefetch requires BLANK and stores a future. setCaching requires PREFETCHING or READY. setReady converts the buffer to a read-only view, computes CRC32, rewinds it, and transitions from expected states. setDone recomputes checksum if set and fails if content changed, then clears action and marks DONE.

## State and Persistence Behavior
Stores block number, ByteBuffer/read-only view, volatile state, action Future, and checksum. No persistence.

## Dependencies and Integration Points
Used by prefetch/caching block managers and tests to manage in-memory block data.

## Risks and Test Signals
Risks are checksum zero sentinel collisions, state transition strictness, read-only buffer expectations, and synchronization around state/action. Tests should cover valid/invalid transitions, checksum mutation detection, future reporting, and buffer position preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/BufferData.java -->
