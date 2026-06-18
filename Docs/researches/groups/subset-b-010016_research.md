# Research Group subset-b-010016

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/DFSPathResolver.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/DFSPathResolver.java

Purpose: Decorates another PathResolver with Microsoft DFS namespace resolution for tree connects and file creates. It follows the MS-DFSC step model, uses ReferralCache and DomainCache, and issues FSCTL_DFS_GET_REFERRALS over IPC$ when local or cached path data is insufficient.

Important APIs/types/functions: resolve(Session, SMB2Packet, SmbPath, ResolveAction) reacts to STATUS_PATH_NOT_COVERED and failed root share connects; resolve(Session, SmbPath, ResolveAction) proactively resolves before create; statusHandler() accepts STATUS_PATH_NOT_COVERED in addition to the wrapped resolver. The private step1 through step14 methods encode the DFS state machine. sendDfsReferralRequest(), getReferral(), handleReferralResponse(), handleRootOrLinkReferralResponse(), and handleDCReferralResponse() bridge to SMB2 IOCTL and cache updates. ResolveState carries current DFSPath, action, hostName, and flags; ReferralResult carries status and cache entries.

Control flow: A request starts by converting SmbPath to DFSPath, then checks simple/IPC paths, referral cache, domain cache, root referrals, link referrals, sysvol referrals, and interlinks. A successful cache/referral hit rewrites the matching prefix with the target hint and invokes the caller action with a parsed SmbPath. Target failures can retry hints or throw DFSException for domain/root/link failure.

State and persistence behavior: ReferralCache and DomainCache are in-memory per resolver instance and can persist between operations on the same SMBClient configuration. DFS referral sessions to other hosts may be opened and authenticated with the original AuthenticationContext; IPC$ shares are intentionally not closed to reuse cached shares. No disk persistence is used.

Dependencies and integration points: Depends on com.hierynomus.msdfsc cache/path/message types, SMB2IoctlResponse, Share.ioctlAsync(), Session.connectShare(), Connection.getClient().connect(), and the wrapped resolver, commonly SymlinkPathResolver or PathResolver.LOCAL. DiskShare and Session call this resolver around TREE_CONNECT and CREATE.

Risks: The code is recursive and can loop if referrals form cycles or caches are inconsistent. DFS cross-host authentication opens nested connections that must be cleaned by Session.logoff. getReferral uses a fixed transact timeout; slow DFS servers surface as TransportException wrappers. DOMAIN referral type is declared but unsupported. Retry in step3 uses lookup.getTargetHint() while iterating target, so target-hint advancement deserves tests. Cache TTL and interlink behavior are correctness-critical.

Test signals: Cover unsupported DFS short-circuit, STATUS_PATH_NOT_COVERED create reroute, root referral miss, expired root vs link TTL, SYSVOL/NETLOGON domain path, interlink recursion, IPC$ short-circuit, referral response with no entries, cross-host nested session reuse, and timeout/error conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/DFSPathResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolveException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolveException.java

Purpose: Checked exception used by path resolvers to return an NT status and optional message/cause when symlink or DFS resolution cannot produce a target path.

Important APIs/types/functions: Constructors accept a raw status, status plus message, or a Throwable. getStatusCode() returns the stored long; getStatus() maps it through NtStatus.valueOf().

Control flow: Resolvers throw this when response error data is missing or referral processing fails. DiskShare catches it and converts it into SMBApiException for SMB2_CREATE. Session.connectTree catches and ignores it for TREE_CONNECT fallback.

State and persistence behavior: Immutable status field only; no persistent state.

Dependencies and integration points: Depends on NtStatus and is consumed by PathResolver, SymlinkPathResolver, DFSPathResolver, DiskShare, and Session.

Risks: The Throwable constructor collapses all causes to STATUS_OTHER, which can hide protocol-specific failure semantics. getStatus() assumes NtStatus.valueOf can represent the stored value.

Test signals: Construct each form and verify status preservation, message/cause propagation, and DiskShare conversion to SMBApiException status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolveException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolver.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolver.java

Purpose: Defines the strategy interface for translating an SMB path before or after an SMB response, allowing the client to compose local, symlink, and DFS resolution without hard-wiring it into share operations.

Important APIs/types/functions: LOCAL resolver simply applies the action to the original SmbPath and accepts only StatusHandler.SUCCESS. The reactive resolve variant receives an SMB2Packet response; the proactive variant receives only a path. ResolveAction<T> is the callback invoked with the resolved target.

Control flow: Callers pass an action that performs the real tree connect or create on the resolved target. Decorators decide whether to call the action, delegate to wrapped resolver, or throw PathResolveException.

State and persistence behavior: Interface has no state. LOCAL is a singleton stateless implementation.

Dependencies and integration points: Depends on SMB2Packet, SmbPath, Session, and StatusHandler. Used by Session.connectTree and DiskShare.create/open flows.

Risks: Callback may return null by convention to mean no reroute, so callers must handle null carefully. Resolver chains must expose a compatible statusHandler or initial SMB requests will reject expected symlink/DFS statuses.

Test signals: Verify LOCAL behavior, decorator ordering, null-return handling, and status handler composition for DFS plus symlink chains.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/PathResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/SymlinkPathResolver.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/SymlinkPathResolver.java

Purpose: Decorates a PathResolver with SMB2 symbolic-link resolution for CREATE responses that stop on a symlink.

Important APIs/types/functions: statusHandler() treats STATUS_STOPPED_ON_SYMLINK as successful enough for CREATE response processing. resolve(Session, SMB2Packet, SmbPath, ResolveAction) extracts SMB2Error.SymbolicLinkError, computes a substitute target, normalizes dot and dot-dot path segments, and invokes the action with a new SmbPath. resolve(Session, SmbPath, ResolveAction) delegates proactive resolution to the wrapped resolver.

Control flow: On STATUS_STOPPED_ON_SYMLINK, missing symbolic link error data becomes PathResolveException. Absolute symlink data concatenates substitute name and unparsed tail. Relative symlink data replaces the parsed file name portion with substitute name plus unparsed tail. Non-symlink responses delegate to the wrapped resolver.

State and persistence behavior: Holds only wrapped resolver and composed StatusHandler. No caches.

Dependencies and integration points: Uses SMB2Error.SymbolicLinkError, SMB2Functions.unicode for unparsed byte lengths, UTF_16LE decoding, SmbPath, and Strings.split/join. DiskShare relies on it through PathResolver chains.

Risks: UnparsedPathLength is byte-based and must remain aligned with UTF-16LE path encoding. normalizePath mutates path components and can be sensitive to leading empty UNC-style components. Only same-host/share SmbPath is produced; cross-share symlink semantics are not broadened here.

Test signals: Absolute symlink, relative symlink, dot and dot-dot normalization, missing error data, multibyte UTF-16 names, trailing unparsed path, and composition with DFS status handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/paths/SymlinkPathResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/Server.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/Server.java

Purpose: Mutable model of negotiated server identity and capabilities for a remote SMB server.

Important APIs/types/functions: Constructor records serverName and port. init(UUID, SMB2Dialect, int, Set<SMB2GlobalCapability>) one-time initializes negotiated identity. Getters expose serverGUID, dialectRevision, securityMode, and capabilities. validate(Server other) compares another server against this initialized identity.

Control flow: Created before negotiation, initialized once after negotiation, then used as a consistency record. validate returns true only when GUID, dialect, security mode, and capabilities match.

State and persistence behavior: In-memory fields only. initialized prevents duplicate init but getters do not guard against uninitialized access.

Dependencies and integration points: Depends on SMB2Dialect and SMB2GlobalCapability. Stored by ServerList and likely connection/session setup code.

Risks: validate assumes other fields are non-null; comparing uninitialized servers can throw NullPointerException. capabilities set is stored by reference and can be externally mutated if caller passes a mutable set.

Test signals: One-time init enforcement, validation success/failure per field, uninitialized behavior, and mutation of capability set after init.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/Server.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/ServerList.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/ServerList.java

Purpose: Thread-safe registry mapping SMB server names to Server objects.

Important APIs/types/functions: lookup(String), registerServer(Server), and unregister(String) all take a ReentrantLock around a HashMap.

Control flow: Callers register negotiated Server instances by getServerName(), later lookup by name, and remove on unregister.

State and persistence behavior: In-memory map only; lifetime is the owning client/connection context.

Dependencies and integration points: Depends on Server and Java locking collections. Used as shared registry around SMB connection management.

Risks: Name normalization is not performed, so case, FQDN vs short name, and aliases can produce duplicate entries. registerServer overwrites silently.

Test signals: Concurrent register/lookup/unregister, overwrite behavior, missing lookup, and case/alias expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/server/ServerList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SMB2GuestSigningRequiredException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SMB2GuestSigningRequiredException.java

Purpose: Domain-specific runtime exception thrown when configuration requires SMB message signing but authentication yielded a guest account, which cannot satisfy that requirement.

Important APIs/types/functions: No extra API beyond the default constructor message.

Control flow: Authentication/session setup code can throw it after session flags identify guest access while signing is required.

State and persistence behavior: Stateless exception.

Dependencies and integration points: Extends SMBRuntimeException and relates to SessionContext.isGuest()/isSigningRequired().

Risks: Only meaningful if raised at the exact point guest state is known; otherwise later send() failures may be less explanatory.

Test signals: Verify message, type, and authentication path behavior for guest plus required signing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SMB2GuestSigningRequiredException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/Session.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/Session.java

Purpose: Represents an authenticated SMB session and owns share connections, nested DFS sessions, signing/encryption, logoff, and packet send behavior.

Important APIs/types/functions: connectShare() validates share names and returns cached or newly connected Share. connectTree() sends SMB2 TREE_CONNECT, lets PathResolver reroute DFS shares, builds TreeConnect, and instantiates DiskShare, PipeShare, or PrinterShare. getNestedSession() caches cross-host sessions under a read/write lock. logoff() closes open shares, logs off nested sessions, sends SMB2_LOGOFF, and publishes SessionLoggedOff. send() signs or encrypts packets. getSigningKey() selects SMB2/SMB3 signing keys. shouldEncryptData() enforces encryption key availability and client preference.

Control flow: A tree connect first sends to the current host/share, then the resolver may return a remote share by creating/reusing a nested session or alternate share. Successful responses reject asymmetric shares, create the correct Share subtype, register it in TreeConnectTable, and return it. TreeDisconnected events remove cached tree connects.

State and persistence behavior: Maintains sessionId, SessionContext keys/flags, TreeConnectTable, nestedSessionsByHost, AuthenticationContext, bus subscription, Signatory, and PacketEncryptor. All state is memory-only but owns live network resources until logoff/close.

Dependencies and integration points: Depends on Connection, SmbConfig, SMBEventBus, PathResolver, Share hierarchy, TreeConnect, PacketEncryptor, Signatory, Futures, and SMB2 messages.

Risks: connectTree ignores PathResolveException during tree connect fallback, so resolver failures can be masked until SMBApiException. nestedSessionsByHost is never cleared after nested logoff. bus.publish is called in finally and bus is assumed non-null. Encryption/signing decisions are security-sensitive; missing keys become TransportException. Share cache keys by raw share name without normalization.

Test signals: Share cache hits, DFS reroute to another host/share, nested session race, asymmetric share rejection, disk/pipe/printer selection, logoff closes shares and nested sessions, TreeDisconnected event removal, signing required without key, encryption preference with key, and null bus behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/Session.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SessionContext.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SessionContext.java

Purpose: Holds negotiated per-session security state, session flags, and SMB3 derived keys.

Important APIs/types/functions: established(SMB2SessionSetup) stores session flags. isSigningRequired(), isEncryptData(), setters, isAnonymous(), isGuest(), session/signing/decryption/encryption/application key getters and setters, and preauth hash copy setter/getter.

Control flow: Authentication populates flags and keys, then Session.send(), Session.shouldEncryptData(), and higher-level code query the context for signing/encryption decisions and identity flags.

State and persistence behavior: In-memory security state only. setPreauthIntegrityHashValue copies the input array, but getPreauthIntegrityHashValue returns the internal array directly.

Dependencies and integration points: Depends on SMB2SessionSetup flags and javax.crypto SecretKey/SecretKeySpec. Integrated with Session, Signatory, PacketEncryptor, and SMB 3.1.1 preauth hashing.

Risks: isAnonymous()/isGuest() will throw if established() has not initialized sessionFlags. Preauth hash getter leaks mutable internal state. Key setters accept nullable values and later send paths must enforce requirements.

Test signals: Established guest/null flags, signing/encryption toggles, key propagation, preauth defensive-copy input behavior, and unestablished access behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/SessionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/TreeConnectTable.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/TreeConnectTable.java

Purpose: Per-session table of open tree connects, indexed by tree id and share name.

Important APIs/types/functions: register(Share), getOpenTreeConnects(), getTreeConnect(long), getTreeConnect(String), and closed(long) use a ReentrantReadWriteLock around two HashMaps.

Control flow: Session registers shares after successful TREE_CONNECT, uses share-name lookup for connectShare cache hits, iterates open tree connects during logoff, and removes entries when TreeDisconnected events arrive.

State and persistence behavior: In-memory mapping only. getOpenTreeConnects returns a snapshot copy so callers can close without holding locks.

Dependencies and integration points: Depends on Share and TreeConnect metadata.

Risks: Share-name lookup is exact string matching and may miss case-insensitive SMB equivalence. register overwrites silently by id or name. closed removes by id and then by the removed share's name, so inconsistent maps can leave stale entries.

Test signals: Register and lookup both keys, close event removal, snapshot semantics during concurrent close, duplicate share name/id behavior, and concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/session/TreeConnectTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Directory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Directory.java

Purpose: Represents an open directory handle and provides directory enumeration plus change notification.

Important APIs/types/functions: list() and generic list(Class, String) collect iterator results. iterator(Class, String) returns DirectoryIterator. watchAsync(Set<SMB2CompletionFilter>, boolean) issues SMB2 CHANGE_NOTIFY through Share. getFileId() exposes the handle id.

Control flow: DirectoryIterator decodes using FileInformationFactory, sends an initial QUERY_DIRECTORY with SMB2_RESTART_SCANS, then repeatedly issues follow-up queries until STATUS_NO_MORE_FILES, STATUS_NO_SUCH_FILE, or an identical buffer is returned. next() consumes decoded information records from the current response buffer before requesting more.

State and persistence behavior: Directory handle state lives in Open/DiskEntry. Iterator keeps currentBuffer, currentIterator, decoder, searchPattern, and next item. No disk persistence.

Dependencies and integration points: Uses Share.queryDirectory(), FileInformationFactory decoders, SMB2QueryDirectory flags/statuses, and change notify APIs.

Risks: The identical-buffer macOS workaround can hide legitimate repeated directory pages if a server returns identical bytes with distinct semantic position. The iterator is not thread-safe and remove() is unsupported. Search pattern semantics depend on server implementation.

Test signals: Empty directory, no-match search pattern, multi-page listing, macOS duplicate-buffer EOF workaround, generic information classes, change notify watchTree flag, and close behavior inherited from DiskEntry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Directory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskEntry.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskEntry.java

Purpose: Abstract base for disk file system opens, shared by File and Directory, adding metadata, security, rename, hardlink, IOCTL, flush, and delete-on-close helpers.

Important APIs/types/functions: getUncPath(), getPath(), getDiskShare(), getFileInformation(), setFileInformation(), get/setSecurityInformation(), rename(), createHardlink(), ioctl overloads, flush(), deleteOnClose(), equals/hashCode.

Control flow: Methods mostly delegate to DiskShare with this fileId. setSecurityInformation(SecurityDescriptor) derives SecurityInformation flags from descriptor owner/group/control bits. rename and hardlink use FileRenameInformation and FileLinkInformation via setInfo.

State and persistence behavior: Inherits fileId, name, and share from Open. Operations mutate remote file system metadata, not local persistent state.

Dependencies and integration points: Depends on msfscc file information structures, msdtyp SecurityDescriptor/SecurityInformation, SMB2FileId, DiskShare, and SmbPath.

Risks: setSecurityInformation infers flags and can omit an intended empty DACL/SACL if descriptor control bits are not set. equals uses class, path, and share, not fileId, so renamed handles and reopen behavior can be subtle. closeNoWait does not expose completion/failure.

Test signals: Metadata query/set for file and directory, security descriptor flag inference, rename replace/rootDirectory variants, hardlink replace variants, IOCTL overloads, flush, delete-on-close, equality after rename/reopen.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskShare.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskShare.java

Purpose: High-level disk-share API for opening files/directories, path-aware DFS/symlink resolution, existence checks, listing, mkdir/rm/rmdir, file/security/share/volume information, and deletion.

Important APIs/types/functions: open(), openDirectory(), openFile(), fileExists(), folderExists(), list() overloads, mkdir(), get/setFileInformation() by path or fileId, getShareInformation(), getVolumeInfo(), rmdir(), rm(), deleteOnClose(), get/setSecurityInfo(). createFileAndResolve() and resolveAndCreateFile() connect PathResolver to SMB2 CREATE and reroute to nested sessions/shares.

Control flow: Public open builds SmbPath then proactively resolves and creates. CREATE responses can trigger reactive resolver flow; rerouteIfNeeded switches session/share for DFS targets. getDiskEntry chooses Directory when FILE_ATTRIBUTE_DIRECTORY is set. Recursive rmdir lists children, skips dot entries, recurses directories, removes files, then marks directory delete-on-close.

State and persistence behavior: Holds a PathResolver. All data operations mutate remote SMB filesystem state. No local persistence.

Dependencies and integration points: Extends Share, uses Session.getNestedSession(), PathResolver, SmbPath, file information factories, security descriptors, and SMB2 create/query/set constants.

Risks: Recursive rmdir has no cycle protection for reparse points or DFS/symlink paths. exists() returns false for several status codes but rethrows others. Casting rerouted share to DiskShare assumes target share type. Root path deletion is rejected only for null/empty rmdir. Open resolution recursion needs tests for loops.

Test signals: DFS and symlink create reroute, openFile/openDirectory option normalization, existence status handling, list generic classes, mkdir, share/volume info parsing, recursive delete with mixed entries, delete pending idempotence, security SACL access mask, and file info codecs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/DiskShare.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/File.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/File.java

Purpose: Represents an open regular file and exposes read, write, stream, remote server-side copy, length, truncate, and file-id operations.

Important APIs/types/functions: write() overloads delegate to SMB2Writer. writeAsync() returns aggregate Future<Long>. getOutputStream() supports append by reading FileStandardInformation. read() overloads fill byte arrays or ByteBuffers and map STATUS_END_OF_FILE to -1. read(OutputStream) streams through FileInputStream. remoteCopyTo() and remoteCopyTo(offset, destination, destinationOffset, length) implement FSCTL_SRV_COPYCHUNK. getLength(), setLength(), getInputStream().

Control flow: Reads send SMB2 READ through Share; writes use ByteChunkProvider chunks through SMB2Writer. Remote copy obtains a resume key, sends copy chunk requests, adapts chunk limits if STATUS_INVALID_PARAMETER returns server maxima, and advances offsets by TotalBytesWritten.

State and persistence behavior: Holds SMB2Writer tied to fileId/share/name. Operations mutate remote file data and metadata.

Dependencies and integration points: Extends DiskEntry, depends on Share.read/write/ioctl, CopyChunkRequest/Response, FileStandardInformation, FileEndOfFileInformation, ByteChunkProvider implementations, ProgressListener, and FileInputStream/FileOutputStream.

Risks: remoteCopyTo requires object-identity same share, not equivalent share path. The copy loop can stall if a server returns success with zero TotalBytesWritten. Async writes detect short writes but synchronous writes just accumulates response bytes. Append fetches end-of-file once, so concurrent appenders can race.

Test signals: Byte array and ByteBuffer EOF behavior, stream read/write with progress, async short-write corruption detection, append offset, remote copy limit renegotiation, same-share enforcement, get/set length, and large transfer chunking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/File.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileInputStream.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileInputStream.java

Purpose: InputStream adapter for reading an SMB file with asynchronous read-ahead.

Important APIs/types/functions: read(), read(byte[], int, int), close(), available(), skip(), loadBuffer(), sendRequest().

Control flow: On first read it sends or awaits nextResponse. A successful read stores response data in buf, advances offset by data length, notifies ProgressListener, and immediately sends the next async read for read-ahead. STATUS_END_OF_FILE or zero-length data marks the stream closed and subsequent reads return -1.

State and persistence behavior: Maintains remote file handle reference, logical offset, current buffer index, current buffer, progress listener, isClosed, and nextResponse. No persistence.

Dependencies and integration points: Uses File.readAsync(), Futures.get(timeout), SMB2ReadResponse, NtStatus, ProgressListener, and TransportException wrapping.

Risks: close() does not cancel an outstanding nextResponse. available() always returns zero. skip() can advance beyond EOF and does not validate negative n. Not thread-safe. If read(byte[], off, len) is called with len zero on a closed stream it returns -1 rather than Java InputStream's usual zero.

Test signals: Single-byte and bulk reads, EOF from status and zero-length data, progress offsets, read-ahead issuance, timeout conversion, skip within buffer and beyond buffer, close-before-response, and zero-length read semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileOutputStream.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileOutputStream.java

Purpose: OutputStream adapter that buffers bytes into a RingBuffer and writes them to an SMB file through SMB2Writer.

Important APIs/types/functions: write(int), write(byte[], int, int), flush(), close(), verifyConnectionNotClosed(), and ByteArrayProvider extending ByteChunkProvider.

Control flow: Writes fill the provider's ring buffer. If the buffer is full or would overflow, flush sends the current provider through SMB2Writer.write(), which consumes chunks and advances provider offset. close drains all available bytes, resets the provider buffer, marks closed, and drops writer reference.

State and persistence behavior: Holds SMB2Writer, ProgressListener, closed flag, and ByteArrayProvider with RingBuffer and current offset. Mutates remote file data when flushed/closed.

Dependencies and integration points: Used by SMB2Writer.getOutputStream() and File.getOutputStream(). Relies on RingBuffer and ByteChunkProvider offset management.

Risks: close() calls provider.reset() before logging provider.getOffset(), but provider still exists while buf is null; getOffset comes from ByteChunkProvider and should be safe. close() does not call flush() through the public method after closed. Not thread-safe. Large writes split by provider.maxSize() and depend on RingBuffer correctness.

Test signals: Buffer boundary writes, close drains remaining bytes, write after close IOException, progress callbacks, append offset propagation, and exact offset advancement after multiple flushes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/FileOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/NamedPipe.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/NamedPipe.java

Purpose: Represents an open SMB named pipe and exposes pipe read/write, transceive, peek, and IOCTL helpers.

Important APIs/types/functions: write(byte[]), write(byte[], int, int), read(byte[]), read(byte[], int, int), transact(), peek(), ioctl overloads, and getName().

Control flow: Writes wrap input in ArrayByteChunkProvider and call Share.write at offset zero. Reads call Share.read at offset zero and copy response data into caller buffer. transact uses FSCTL_PIPE_TRANSCEIVE. peek uses FSCTL_PIPE_PEEK and decodes FsCtlPipePeekResponse from SMBBuffer.

State and persistence behavior: Inherits fileId/name/share from Open; pipe operations affect server pipe state but no local persistent state.

Dependencies and integration points: Used by PipeShare.open(). Depends on fsctl pipe structures, Share read/write/ioctl, SMBBuffer, and SMBRuntimeException.

Risks: read ignores STATUS_END_OF_FILE special semantics and returns zero if server returns no data. transact(byte[]) allocates output from IOCTL response size, while fixed-buffer overload truncates to caller length. No stream facade or async pipe APIs here.

Test signals: Pipe open/read/write, partial buffer offsets, FSCTL_PIPE_TRANSCEIVE with variable/fixed output, peek maxDataSize parsing, and IOCTL error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/NamedPipe.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Open.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Open.java

Purpose: Generic base for an open SMB handle, including close, lock/unlock builder support, and file id exposure.

Important APIs/types/functions: requestLock(), lockRequest(List<SMB2LockElement>), getFileId(), close(), closeSilently(), and LockBuilder methods exclusiveLock(), sharedLock(), unlock(), send().

Control flow: LockBuilder accumulates SMB2LockElement records and send() delegates to Open.lockRequest. For dialects newer than SMB 2.0.2, lockRequest takes an OperationBucket for sequence number/index, sends the lock request through Share, then frees the bucket.

State and persistence behavior: Stores share, fileId, name, and OperationBuckets. Lock operations mutate remote byte-range lock state.

Dependencies and integration points: Base class for DiskEntry and NamedPipe. Depends on Share.sendLockRequest(), SMB2LockFlag, SMB2LockElement, SMB2Dialect, and SmbPath.

Risks: OperationBucket is freed only after successful send; exceptions can leak buckets. close() throws runtime SMBApiException from Share without checked signature. LockBuilder can send an empty lock list.

Test signals: Exclusive/shared/unlock flag encoding, failImmediately flag, dialect SMB_2_0_2 sequence zero behavior, exception path bucket leak, closeSilently logging, and empty lock list behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Open.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/OperationBuckets.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/OperationBuckets.java

Purpose: Allocates up to 64 operation buckets for SMB lock sequence numbers and indexes.

Important APIs/types/functions: takeFreeBucket() returns an existing free bucket or creates a new one up to 64. freeBucket(int) marks by one-based index free and increments sequenceNumber. OperationBucket exposes getIndex() and getSequenceNumber().

Control flow: Open.lockRequest takes a bucket before sending a lock for newer dialects, passes bucket sequence number/index, then frees it.

State and persistence behavior: In-memory list of buckets protected by ReentrantReadWriteLock write lock.

Dependencies and integration points: Package-private helper for Open.

Risks: freeBucket uses `sequenceNumber += 1 % 16`, which increments by one because modulo binds first; it likely intended `(sequenceNumber + 1) % 16`. Sequence numbers will not wrap at 16. Exceptions between take and free in Open can exhaust buckets. No validation for invalid free index.

Test signals: Allocate 64 buckets, exhaustion error, reuse freed bucket, sequence wrap expectation, invalid index, and exception path from Open.lockRequest.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/OperationBuckets.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PipeShare.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PipeShare.java

Purpose: Share subtype for IPC$ named-pipe operations, including waiting for pipe instances and opening NamedPipe handles.

Important APIs/types/functions: waitForPipe(String), waitForPipe(String, long, TimeUnit), open(), openFileId(), and public closeFileId().

Control flow: waitForPipe encodes FsCtlPipeWaitRequest, sends FSCTL_PIPE_WAIT through ioctlAsync, waits slightly longer than requested timeout so the server can return STATUS_IO_TIMEOUT, then returns true for success, false for timeout, or throws SMBApiException. open builds a path under the pipe share and uses Share.openFileId, returning NamedPipe.

State and persistence behavior: No additional state beyond Share; operations interact with remote pipe namespace.

Dependencies and integration points: Extends Share, uses SMBBuffer, FsCtlPipeWaitRequest, ArrayByteChunkProvider, SMB2 IOCTL response status, and NamedPipe.

Risks: timeoutMs adds only 20 ms margin and can be flaky under latency. Indefinite waits use receive with timeout zero. Name must exclude `\pipe\` but method does not validate it.

Test signals: Available pipe, timeout pipe, error status, indefinite wait, name encoding, open with access masks/options, and closeFileId exposure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PipeShare.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PrinterShare.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PrinterShare.java

Purpose: Share subtype for printer shares, turning InputStream or ByteChunkProvider data into a temporary SMB open and writes.

Important APIs/types/functions: print(InputStream), print(InputStream, ProgressListener), print(ByteChunkProvider), and print(ByteChunkProvider, ProgressListener).

Control flow: print opens the printer share path with FILE_WRITE_DATA, FILE_ATTRIBUTE_NORMAL, FILE_SHARE_WRITE, FILE_CREATE, FILE_NON_DIRECTORY_FILE, and FILE_WRITE_THROUGH. It writes provider data using SMB2Writer and closes the file id in finally.

State and persistence behavior: No extra state beyond Share. Remote printer spool state changes as bytes are written.

Dependencies and integration points: Extends Share and uses InputStreamByteChunkProvider, SMB2Writer, AccessMask, create disposition/options, and ProgressListener.

Risks: FILE_CREATE may fail if the server expects a generated spool file name or if an entry exists. closeFileId in finally can throw and mask write failure. InputStreamByteChunkProvider ownership of closing the input is external.

Test signals: Input stream print, provider print, progress, close on write failure, access/create option expectations against a printer-capable server or mock share.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/PrinterShare.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/RingBuffer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/RingBuffer.java

Purpose: Fixed-size circular byte buffer used by FileOutputStream's ByteChunkProvider.

Important APIs/types/functions: write(byte[], int, int), write(int), read(byte[]), maxSize(), size(), isFull(), isFull(int), and isEmpty().

Control flow: write validates source length and available capacity, copies bytes either contiguously or wrapped around the end, advances writeIndex modulo buffer length, and increments size. read copies up to requested chunk length from readIndex with wrap support, advances readIndex, and decrements size.

State and persistence behavior: Maintains byte array, writeIndex, readIndex, and size only in memory.

Dependencies and integration points: Package-private helper for FileOutputStream.ByteArrayProvider.

Risks: Not thread-safe. Error message says accomodate misspelled but harmless. No constructor validation for zero/negative maxSize; modulo by zero would fail later. read(byte[0]) returns zero.

Test signals: Write/read exact capacity, wraparound write/read, overflow write exception, source bounds exception, isFull(len) exception for too-large len, and zero-size construction behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/RingBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/SMB2Writer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/SMB2Writer.java

Purpose: Generic writer for any Share entry addressed by SMB2FileId, used by regular files and printer shares.

Important APIs/types/functions: write(byte[], long), write(byte[], long, int, int), write(ByteChunkProvider), write(ByteChunkProvider, ProgressListener), writeAsync(byte[], long, int, int), writeAsync(ByteChunkProvider), and getOutputStream().

Control flow: Synchronous write loops while provider.isAvailable(), calls Share.write(), accumulates bytes written, and emits progress. Async write loops providers into Share.writeAsync futures, records the provider's last prepared write size, transforms each response to verify the server wrote the full chunk, then sequences and sums the futures.

State and persistence behavior: Holds Share, SMB2FileId, and entryName. Provider offset state is mutated as chunks are prepared/written. Remote entry contents are mutated.

Dependencies and integration points: Used by File and PrinterShare. Depends on ByteChunkProvider, ArrayByteChunkProvider, FileOutputStream, Futures transforms/sequence, SMB2WriteResponse, and ProgressListener.

Risks: Synchronous path does not validate short writes as strictly as async path. Async path queues all chunks immediately, which can create many outstanding requests for large providers. Progress uses provider.getOffset(), which must already reflect consumed bytes.

Test signals: Multi-chunk sync write, short-write async exception, async aggregate sum, progress counts/offsets, output stream creation with offset, and provider exception propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/SMB2Writer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Share.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Share.java

Purpose: Base implementation for SMB tree-connected shares and low-level SMB2 operations used by disk, pipe, and printer share subclasses.

Important APIs/types/functions: close(), isConnected(), createFile/openFileId(), queryInfo(), setInfo(), queryDirectory(), read/readAsync(), write/writeAsync(), ioctl overloads/ioctlAsync(), sendLockRequest(), changeNotifyAsync(), receive(), equals/hashCode. Status handlers allow symlink, EOF, no-more-files/no-such-file, and already-closed statuses where appropriate.

Control flow: Constructor derives negotiated dialect and buffer sizes from TreeConnect, SmbConfig, and NegotiatedProtocol. Public and package methods build SMB2 request messages with sessionId/treeId/fileId, send through Session, wait with operation-specific timeouts, and validate statuses with supplied StatusHandler. close atomically disconnects once through TreeConnect.close().

State and persistence behavior: Holds SmbPath, TreeConnect, Session, dialect, buffer/timeout limits, sessionId/treeId, and disconnected AtomicBoolean. No persistence, but owns remote tree connection lifetime.

Dependencies and integration points: Used by DiskShare, PipeShare, PrinterShare, Open subclasses, Session, TreeConnect, SMB2 message classes, Futures, ByteChunkProvider, and SmbConfig.

Risks: send() throws if disconnected, but outstanding futures may still complete after close. IOCTL input/output sizes are strictly bounded by negotiated transact buffer. equals/hashCode ignore treeId/session, so reconnects to same SmbPath compare equal. receive wraps TransportException in SMBRuntimeException.

Test signals: Buffer-size negotiation, close idempotence, read EOF status, query directory terminal statuses, IOCTL max buffer checks, disconnected send failure, equals across reconnects, lock/change notify forwarding, and timeout paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/Share.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/StatusHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/StatusHandler.java

Purpose: Small status-policy interface used to decide whether an SMB2 response status is acceptable for a particular operation.

Important APIs/types/functions: SUCCESS singleton returns true only for NtStatus.STATUS_SUCCESS. Implementations provide isSuccess(long).

Control flow: Share.receive checks a response header status with a supplied StatusHandler and throws SMBApiException if false. PathResolver decorators expose handlers that accept resolution-triggering statuses.

State and persistence behavior: Stateless strategy objects.

Dependencies and integration points: Uses NtStatus. Implemented anonymously in Share, DiskShare, DFSPathResolver, SymlinkPathResolver, and PipeShare handling.

Risks: Incorrect handlers can cause either premature exceptions or accidental acceptance of real errors. Because it sees only status code, it cannot inspect response-specific error payloads.

Test signals: SUCCESS policy, composed DFS/symlink policies, and per-operation handlers rejecting unexpected statuses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/StatusHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/TreeConnect.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/TreeConnect.java

Purpose: Represents an SMB tree connect and owns tree disconnect plus share capabilities and negotiated tree-level metadata.

Important APIs/types/functions: close(), getShareName(), getTreeId(), getSession(), getMaximalAccess(), isDfsShare(), isCAShare(), isScaleoutShare(), getConfig(), getNegotiatedProtocol(), and toString().

Control flow: close sends SMB2_TREE_DISCONNECT via Session.send, waits for transact timeout, throws SMBApiException on non-success, and publishes TreeDisconnected in finally so Session can remove cache entries.

State and persistence behavior: Holds treeId, SmbPath, Session, capabilities, negotiated protocol, config, event bus, maximalAccess, and encryptData flag derived from share flags and encryption support. No persistence.

Dependencies and integration points: Created by Session.connectTree and embedded in Share. Uses SMBEventBus and TreeDisconnected events.

Risks: encryptData is computed but not exposed or used in this file; actual per-share encryption may be incomplete elsewhere. bus is assumed non-null. Publishing disconnect in finally happens even if disconnect send fails.

Test signals: Tree disconnect success/failure, event publication on failure, capability predicates, maximal access exposure, share flag encryption calculation expectations, and toString shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/TreeConnect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/PacketReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/PacketReader.java

Purpose: Base runnable for blocking transport packet-reader threads.

Important APIs/types/functions: Constructor wraps input in BufferedInputStream and creates a daemon thread. start() starts it. stop() marks stopped and interrupts. run() repeatedly calls doRead(), logs packets, and passes them to PacketReceiver.handle(); errors go to handleError().

Control flow: Subclasses implement doRead() for framing/protocol. The read loop exits on interruption, stopped flag, or transport error. If stopped triggered the error path, it suppresses handleError.

State and persistence behavior: Holds input stream, packet receiver, stopped AtomicBoolean, and daemon Thread. No persistence.

Dependencies and integration points: Extended by DirectTcpPacketReader. Depends on PacketData, PacketReceiver, and TransportException.

Risks: stop interrupts but blocking InputStream.read may not unblock until socket close. handle(packet) exceptions are not caught unless they are TransportException from doRead. Thread name captures original current thread name.

Test signals: Start/stop lifecycle, EOF error delivery, stopped suppression, buffered input wrapping, daemon flag, and subclass doRead exception behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/PacketReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/TransportLayerFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/TransportLayerFactory.java

Purpose: Factory interface for creating a configured protocol TransportLayer from packet handlers and SMB config.

Important APIs/types/functions: createTransportLayer(PacketHandlers<D, P>, SmbConfig).

Control flow: Connection/client code selects an implementation such as DirectTcpTransportFactory, AsyncDirectTcpTransportFactory, or TunnelTransportFactory and calls createTransportLayer before connecting.

State and persistence behavior: Interface only; implementations may hold socket factories, channel groups, or tunnel addresses.

Dependencies and integration points: Depends on protocol Packet/PacketData/PacketHandlers/TransportLayer and SmbConfig.

Risks: Factory implementations must honor config timeouts and socket settings consistently or behavior differs by transport.

Test signals: Each implementation returns a transport with expected config propagation and can be substituted through common interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/TransportLayerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransport.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransport.java

Purpose: Asynchronous direct TCP transport for SMB over port 445 using AsynchronousSocketChannel and a serialized write queue.

Important APIs/types/functions: write(P), connect(InetSocketAddress), disconnect(), isConnected(), setSoTimeout(), prepareBufferToSend(), writeOrEnqueue(), and startAsyncWrite().

Control flow: write serializes a packet to a ByteBuffer with a 4-byte direct TCP header, queues it, and starts an async write if none is active. Completion handler continues writing the current buffer until exhausted, removes completed buffers, and advances the queue. connect waits up to a fixed 5000 ms for socket connect, marks connected, and starts AsyncPacketReader. disconnect marks disconnected and closes the channel.

State and persistence behavior: Holds handlers, socketChannel, AsyncPacketReader, connected AtomicBoolean, soTimeout, LinkedBlockingQueue of ByteBuffers, and writingNow AtomicBoolean.

Dependencies and integration points: Created by AsyncDirectTcpTransportFactory. Uses PacketHandlers serializer/factory/receiver and AsyncPacketReader/PacketBufferReader.

Risks: startAsyncWrite throws IllegalStateException from async path if disconnected. Failed writes on non-closed exceptions call startNextWriteIfWaiting then handleError, so subsequent writes may continue despite error. No explicit backpressure limit on writeQueue. Connect timeout is fixed, not from config.

Test signals: Header encoding, partial async writes, queue ordering, connect timeout, write before connect, disconnect during write, receiver error on failure, and large packet serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportFactory.java

Purpose: Transport factory that creates AsyncDirectTcpTransport instances, optionally bound to a caller-provided asynchronous channel group.

Important APIs/types/functions: createTransportLayer(), constructors for default group, ExecutorService, or AsynchronousChannelGroup, and createGroup(ExecutorService).

Control flow: createTransportLayer constructs AsyncDirectTcpTransport with config soTimeout and packet handlers, wrapping IOException in SMBRuntimeException. Executor constructor builds an AsynchronousChannelGroup from the executor.

State and persistence behavior: Holds an AsynchronousChannelGroup reference; default null delegates to system default group.

Dependencies and integration points: Implements TransportLayerFactory and integrates with SmbConfig transport selection.

Risks: createGroup wraps IOException in RuntimeException rather than SMBRuntimeException. The factory does not own shutdown of executor/channel group. Null group behavior depends on JDK AsynchronousSocketChannel.open(null).

Test signals: Default group creation, executor group creation, IOException wrapping, soTimeout propagation, and lifecycle/shutdown ownership.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncPacketReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncPacketReader.java

Purpose: Asynchronous packet reader that continuously reads direct TCP framed bytes from an AsynchronousSocketChannel and dispatches decoded packets.

Important APIs/types/functions: start(String, int), stop(), initiateNextRead(PacketBufferReader), readAndHandlePacket(), handleAsyncFailure(), isChannelClosedByOtherParty(), closeChannelQuietly().

Control flow: start stores remote host/timeout and initiates a read using PacketBufferReader's ByteBuffer. Completion processes as many complete packets as readNext() can produce, then issues another read. Negative bytes mean EOF and produce failure unless stopped. Decode errors or async failures close the channel.

State and persistence behavior: Holds packetFactory, handler, channel, remoteHost, soTimeout, and stopped AtomicBoolean.

Dependencies and integration points: Used by AsyncDirectTcpTransport. Depends on PacketBufferReader, PacketFactory, PacketReceiver, ASN-independent packet decoding, and NIO completion handlers.

Risks: handleAsyncFailure closes channel but does not call handler.handleError for read failures; unlike write failures, receiver may not learn why reads stopped. stop only flips flag, it does not close channel. Timeout failures are treated as async failures and close channel.

Test signals: Complete packet dispatch, fragmented packet assembly across reads, multiple packets per read, EOF handling, decode error handling, stop suppressing next reads, and receiver error expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/AsyncPacketReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/PacketBufferReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/PacketBufferReader.java

Purpose: Stateful parser for direct TCP packet framing over an async ByteBuffer stream.

Important APIs/types/functions: readNext(), getBuffer(), readPacketHeader(), readPacketBody(), and internal header/body state checks.

Control flow: readNext flips the read buffer, reads a 4-byte header when available, masks the big-endian int to 24-bit length, allocates currentPacketBytes, copies as much body data as available, compacts the buffer, and returns a full packet only when all bytes are accumulated. It resets packet state after a full packet.

State and persistence behavior: Holds a 9000-byte ByteBuffer, currentPacketBytes, currentPacketLength, and currentPacketOffset.

Dependencies and integration points: Used exclusively by AsyncPacketReader for direct TCP framing.

Risks: Packet length is trusted and can allocate very large arrays if a peer sends a malformed header. Fixed read buffer handles jumbo frame reads but packets may be larger through accumulation. Zero-length packet is possible and should be considered. Not thread-safe.

Test signals: Header split across reads, body split across reads, multiple packets in one buffer, 24-bit masking, zero-length packet, malformed huge length, and buffer compact position handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/async/PacketBufferReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpPacketReader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpPacketReader.java

Purpose: Blocking direct TCP packet reader that reads SMB direct TCP headers and packet bodies from an InputStream.

Important APIs/types/functions: doRead(), readTcpHeader(), readPacket(int), and readFully(byte[]).

Control flow: doRead reads the 4-byte direct TCP header, parses the first byte plus 24-bit length, reads exactly that many body bytes, and delegates to PacketFactory.read(). readFully loops until buffer filled or EOF, throwing TransportException wrapping EOFException.

State and persistence behavior: Holds PacketFactory in addition to PacketReader base state.

Dependencies and integration points: Used by DirectTcpTransport. Depends on Buffer.PlainBuffer big-endian parsing and PacketFactory.

Risks: Packet length is trusted and can allocate large arrays. readFully can block until socket timeout/close. A zero-length packet is passed to packetFactory. EOF becomes TransportException.

Test signals: Header parsing, partial stream reads, EOF during header/body, malformed length, packetFactory BufferException wrapping, and socket timeout behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpPacketReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransport.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransport.java

Purpose: Blocking direct TCP transport implementation for SMB packets over sockets.

Important APIs/types/functions: write(P), connect(InetSocketAddress), disconnect(), isConnected(), setSocketFactory(), setSoTimeout(), writePacketData(), and writeDirectTcpPacketHeader().

Control flow: connect creates a socket through SocketFactory, sets SO_TIMEOUT, opens buffered output, starts DirectTcpPacketReader on the input. write first checks connected, takes write lock, rechecks connected, serializes packet, writes 4-byte direct TCP header, writes packet bytes, and flushes. disconnect takes write lock, stops reader, closes input/output/socket, and nulls resources.

State and persistence behavior: Holds PacketHandlers, ReentrantReadWriteLock, SocketFactory, soTimeout, Socket, BufferedOutputStream, and PacketReader.

Dependencies and integration points: Created by DirectTcpTransportFactory. Uses ProxySocketFactory by default unless config supplies another factory.

Risks: isConnected relies on socket flags and may return true after remote half-close until read detects EOF. disconnect closes socket.getInputStream() after stop; getInputStream can throw. PacketData buffer rpos is not advanced after write, which is usually fine for a serialized temporary buffer. No write timeout beyond socket behavior.

Test signals: Config socket factory, write header bytes, concurrent write/disconnect race, reader start, EOF error propagation, disconnect idempotence, and write after disconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransportFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransportFactory.java

Purpose: Factory for blocking direct TCP transports.

Important APIs/types/functions: createTransportLayer(PacketHandlers, SmbConfig) returns DirectTcpTransport configured with config socket factory and SO timeout.

Control flow: Connection code calls the factory before connect; the created transport handles actual socket lifecycle.

State and persistence behavior: Stateless factory.

Dependencies and integration points: Implements TransportLayerFactory and uses SmbConfig.getSocketFactory()/getSoTimeout().

Risks: Any config socket factory misconfiguration surfaces later at connect time. No additional validation.

Test signals: Factory returns DirectTcpTransport, propagates socket factory and timeout, and works through TransportLayerFactory interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/direct/DirectTcpTransportFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransport.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransport.java

Purpose: Transport wrapper that ignores the requested remote address and connects an underlying transport to a fixed tunnel host/port, typically for SSH tunnels.

Important APIs/types/functions: write(), connect(), disconnect(), and isConnected().

Control flow: connect constructs InetSocketAddress(tunnelHost, tunnelPort) and calls the wrapped transport connect. All other operations delegate unchanged.

State and persistence behavior: Holds wrapped transport and tunnel endpoint. No persistence.

Dependencies and integration points: Created by TunnelTransportFactory around another TransportLayerFactory.

Risks: SMB higher layers still believe they are connecting to the original host while TCP goes to tunnel endpoint; name validation, signing, and server identity must tolerate that. RemoteAddress is fully ignored except for the caller's surrounding context.

Test signals: Connect uses tunnel address, write/disconnect/isConnected delegate, and behavior with direct and async underlying transports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransportFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransportFactory.java

Purpose: Factory that wraps another transport factory in TunnelTransport with a fixed host/port endpoint.

Important APIs/types/functions: Constructor stores tunnelFactory, tunnelHost, and tunnelPort. createTransportLayer() creates the underlying transport and wraps it.

Control flow: Used in config to layer tunnel address rewriting around any packet transport implementation.

State and persistence behavior: Holds tunnel factory and endpoint only.

Dependencies and integration points: Implements TransportLayerFactory and composes DirectTcpTransportFactory or AsyncDirectTcpTransportFactory.

Risks: Does not validate port range or host. Underlying factory exceptions propagate directly.

Test signals: Underlying factory invocation, wrapper endpoint propagation, delegate transport behavior, and invalid endpoint handling at connect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/transport/tcp/tunnel/TunnelTransportFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/DigestUtil.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/DigestUtil.java

Purpose: Utility for chained message digest computation, especially SMB 3.1.1 preauthentication integrity hashing.

Important APIs/types/functions: digest(MessageDigest digest, byte[] previous, byte[] extra) resets the digest, updates with previous then extra, and returns digest.digest().

Control flow: Callers provide an already selected MessageDigest implementation and the two byte arrays to concatenate logically.

State and persistence behavior: Stateless utility, but it mutates the passed MessageDigest state by reset/update/digest.

Dependencies and integration points: Depends on com.hierynomus.security.MessageDigest; used by authentication/connection security code outside this subset.

Risks: Null previous/extra handling depends on MessageDigest.update behavior and can throw. Callers sharing a MessageDigest across threads would race.

Test signals: Known-vector digest of previous plus extra, reset behavior between calls, null input behavior, and thread confinement expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/DigestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/SmbFiles.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/SmbFiles.java

Purpose: Convenience utilities for copying local data to an SMB DiskShare and recursively creating remote directories.

Important APIs/types/functions: static copy(File, DiskShare, String, boolean), static write(InputStream, DiskShare, String, boolean), mkdirs(DiskShare, String), and mkdirs(DiskShare, SmbPath).

Control flow: copy validates source exists/readable/isFile, opens a FileInputStream, and delegates to write. write opens the destination with GENERIC_WRITE, FILE_ATTRIBUTE_NORMAL, FILE_SHARE_WRITE, create disposition FILE_OVERWRITE_IF or FILE_CREATE, then writes an InputStreamByteChunkProvider. mkdirs checks folderExists for the path, recurses to parent, then mkdirs the current path.

State and persistence behavior: Stateless local utility; mutates remote share filesystem. copy closes local input and remote file through try-with-resources.

Dependencies and integration points: Uses DiskShare.openFile(), File.write(), SmbPath parents, and SMB2 create constants.

Risks: copy silently returns 0 for missing/unreadable/non-file source. write silently returns 0 for null source or destPath. mkdirs recursion depends on SmbPath.getParent() terminating; root/empty path behavior needs coverage. Access/share flags may be too restrictive for concurrent readers.

Test signals: Copy success byte count, missing source returns zero, overwrite true/false dispositions, write null arguments, mkdirs nested creation, mkdirs existing path, and root parent termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/utils/SmbFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit.java

Purpose: Encoder/decoder for SPNEGO NegTokenInit tokens with GSS-API application framing and mechanism list/token fields.

Important APIs/types/functions: write(Buffer), read(byte[]), parseTagged(), readMechToken(), readMechTypeList(), addSupportedMech(), setMechToken(), getSupportedMechTypes(). Constants include ADS_IGNORE_PRINCIPAL.

Control flow: write builds a NegTokenInit sequence with optional mechTypes and mechToken, then SpnegoToken.writeGss wraps it with SPNEGO OID and [APPLICATION 0]. read parses DER from a little-endian Buffer stream, validates application class and SPNEGO OID object type, then delegates to parseSpnegoToken. parseTagged accepts tags 0 mechTypes, 1 reqFlags ignored, 2 mechToken, 3 mechListMIC ignored, and ignores ADS compatibility hints.

State and persistence behavior: Stores mutable mechTypes list and mechToken byte array in memory.

Dependencies and integration points: Uses hierynomus ASN.1 DER encoder/decoder, ASN1Sequence/TaggedObject/ObjectIdentifier/OctetString, Buffer, ObjectIdentifiers.SPNEGO, and SpnegoToken.

Risks: read validates OID type but not equality to SPNEGO. getSupportedMechTypes returns mutable internal list. setMechToken stores caller array by reference. reqFlags and MIC are ignored.

Test signals: Write/read roundtrip with multiple mechs and token, invalid application tag, non-OID first sequence element, unknown tagged field, ADS ignore principal input, mutable getter/setter aliasing, and empty optional fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit2.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit2.java

Purpose: Microsoft NegTokenInit2 parser extension that understands tag layout with negHints before mechListMIC.

Important APIs/types/functions: Overrides parseTagged(ASN1TaggedObject) from NegTokenInit. Tags 0 mechTypes, 1 reqFlags ignored, 2 mechToken, 3 negHints ignored, and 4 mechListMIC ignored.

Control flow: The inherited read path invokes this parseTagged so Init2 tokens can be accepted without treating negHints tag 3 as MIC. ADS_IGNORE_PRINCIPAL strings are ignored.

State and persistence behavior: Inherits mechTypes and mechToken state from NegTokenInit; no new fields are stored.

Dependencies and integration points: Used wherever an SPNEGO initiator token may include Microsoft negHints. Depends on ASN1TaggedObject and NegTokenInit parsing helpers.

Risks: negHints and MIC are ignored entirely, so callers cannot use server hints or MIC validation. It inherits write behavior from NegTokenInit, so it does not emit Init2-specific negHints.

Test signals: Parse Init2 with negHints tag 3, parse MIC tag 4, inherited mech list/token parsing, unknown tag failure, and ADS ignore behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenInit2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenTarg.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenTarg.java

Purpose: Encoder/decoder for SPNEGO NegTokenTarg response tokens, including negotiation result, selected mechanism, response token, and MIC.

Important APIs/types/functions: write(Buffer), read(byte[]), parseTagged(), readNegResult(), readSupportedMech(), readResponseToken(), readMechListMIC(), getters/setters for negotiationResult, supportedMech, responseToken, and mechListMic. Overrides writeGss() to emit only the [1] negotiation token without outer SPNEGO OID framing for Samba compatibility.

Control flow: write conditionally adds tagged ASN.1 fields for non-null values, wraps them in a sequence, and writes DER. read parses a DER object and delegates to SpnegoToken.parseSpnegoToken. parseTagged validates expected ASN.1 types for tags 0 through 3 and stores values.

State and persistence behavior: Mutable token fields are stored in memory; byte arrays are stored and returned by reference.

Dependencies and integration points: Uses ASN.1 DER streams/types, Buffer, SpnegoToken, and is part of authentication token exchange.

Risks: Overridden writeGss uses context-specific tag 1 directly and may not match all peers that expect full GSS framing. Byte array setters/getters alias caller/internal arrays. Error message in readNegResult references supportedMech rather than object. No enum abstraction for negotiation result values.

Test signals: Encode/decode all optional fields, absent fields, invalid ASN.1 types per tag, unknown tag, Samba-compatible output form, and mutable array aliasing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/NegTokenTarg.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/ObjectIdentifiers.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/ObjectIdentifiers.java

Purpose: Central holder for the SPNEGO object identifier constant.

Important APIs/types/functions: public static final ASN1ObjectIdentifier SPNEGO with value 1.3.6.1.5.5.2.

Control flow: SpnegoToken.writeGss inserts this OID into the GSS application sequence, and NegTokenInit.read uses it in validation messages.

State and persistence behavior: Immutable constant only.

Dependencies and integration points: Depends on ASN1ObjectIdentifier and is imported by SPNEGO token classes.

Risks: Class is not final and has implicit public constructor, though it only contains constants. Equality validation is left to callers.

Test signals: Constant value, identity use in encoded NegTokenInit, and no accidental mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/ObjectIdentifiers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/RawToken.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/RawToken.java

Purpose: SpnegoToken implementation that writes prebuilt raw token bytes without parsing or ASN.1 reconstruction.

Important APIs/types/functions: Constructor RawToken(byte[]), write(Buffer), and parseTagged() which throws UnsupportedOperationException.

Control flow: write copies rawToken into the output buffer if non-null. No validation, framing, or decoding is performed.

State and persistence behavior: Stores caller-provided byte array by reference. Stateless after write except for the array.

Dependencies and integration points: Useful when an authentication mechanism already produced a complete token. Extends SpnegoToken only to share write contract.

Risks: Caller can mutate rawToken after construction. Null token silently writes nothing. parseTagged throws unchecked UnsupportedOperationException rather than SpnegoException.

Test signals: Raw bytes emitted unchanged, null token no-op, mutation aliasing, and parseTagged unsupported behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/RawToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoException.java

Purpose: Checked exception for SPNEGO encode/decode failures.

Important APIs/types/functions: Constructors for message and message plus IOException cause.

Control flow: SPNEGO token read/write methods wrap IOException and structural ASN.1 mismatches in SpnegoException so authentication code can distinguish token errors.

State and persistence behavior: Exception state only.

Dependencies and integration points: Used by NegTokenInit, NegTokenInit2, NegTokenTarg, RawToken, and SpnegoToken.

Risks: Only IOException cause constructor exists; non-IO causes must be wrapped differently or lost. No status/code field for protocol error category.

Test signals: Message preservation, cause preservation, and propagation from invalid DER/token shapes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoToken.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoToken.java

Purpose: Abstract base for SPNEGO token classes, providing common GSS-API wrapper writing and CHOICE/SEQUENCE parsing.

Important APIs/types/functions: Constructor takes tokenTagNo and tokenName. writeGss(Buffer, ASN1Object) emits [APPLICATION 0] sequence of SPNEGO OID plus context-specific negotiation token. parseSpnegoToken(ASN1Object) validates expected CHOICE tag and inner sequence, then dispatches each tagged field to parseTagged(). Abstract write() and parseTagged().

Control flow: Subclasses build or parse token-specific fields; this base handles outer SPNEGO/GSS structure and shared validation. NegTokenTarg overrides writeGss for a special output form but still uses parseSpnegoToken.

State and persistence behavior: Holds token tag number and human-readable token name. No persistence.

Dependencies and integration points: Depends on ASN.1 DER output types, ObjectIdentifiers.SPNEGO, Buffer, and subclass implementations.

Risks: tokenName can be null for RawToken, producing weak error messages if parsing were invoked. parseSpnegoToken demands all sequence elements are tagged objects and rejects extensions not modeled by subclasses. writeGss uses explicit/implicit constructor flags that must match ASN.1 library semantics.

Test signals: Outer GSS encoding, CHOICE tag validation, non-sequence rejection, non-tagged child rejection, subclass dispatch order, and NegTokenTarg override compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/spnego/SpnegoToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/utils/Strings.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/utils/Strings.java

Purpose: Small string utility class for delimiter splitting/joining, ASCII null-terminated bytes, and nonblank checks.

Important APIs/types/functions: split(String, char), join(List<String>, char), nullTerminatedBytes(String), and isNotBlank(String).

Control flow: split uses indexOf loop preserving empty segments; join appends delimiter between list entries; nullTerminatedBytes allocates length plus one and copies US-ASCII bytes, leaving final zero; isNotBlank trims and checks empty.

State and persistence behavior: Stateless utility.

Dependencies and integration points: SymlinkPathResolver uses split/join for path normalization. SPNEGO and other SMB helpers can use nullTerminatedBytes.

Risks: nullTerminatedBytes allocates by char length, which can mismatch encoded byte length for non-ASCII input; it uses US_ASCII and may replace characters. split does not handle null input. join does not handle null list elements specially.

Test signals: Empty segments in split, leading/trailing delimiter, join roundtrip, ASCII null terminator, non-ASCII nullTerminatedBytes behavior, null input failure, and isNotBlank trim behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/utils/Strings.java -->
