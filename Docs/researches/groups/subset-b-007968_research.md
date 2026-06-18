# Research Report: subset-b-007968

Work item `subset-b-007968` covers XRootD ztn security token handling, the standard filesystem interface/native adapter, and selected SSI client/runtime support files. Each section below is source-tree-aligned and wrapped for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecProtocolztn.cc -->
# sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecProtocolztn.cc

## Purpose
Implements the `ztn` XRootD security protocol for bearer/SciTokens-style token authentication. It provides the client-side credential collector, the server-side token validator, and the plugin entry points `XrdSecProtocolztnInit` and `XrdSecProtocolztnObject`. The protocol is explicitly TLS-only and exchanges a compact private credential frame containing either a token request opcode or a token payload.

## Important APIs, Types, And Functions
- `XrdSecProtocolztn : XrdSecProtocol` implements `getCredentials()`, `Authenticate()`, `needTLS()`, and `Delete()`.
- `TokenHdr` is the on-wire header with id `"ztn"`, protocol version, opcode, and reserved bytes. Opcodes are `SndAI` for authorized issuer requests and `IsTkn` for token responses.
- `TokenResp` extends `TokenHdr` with a network-order token length and a null-terminated token payload.
- `XrdSecProtocolztnInit()` parses server configuration and returns the client parameter string `TLS:<opts>:<maxtsz>:` after optional token library linkage.
- `XrdSecProtocolztnObject()` constructs client or server protocol objects and rejects non-TLS endpoints.
- `getLinkage()` uses `XrdOucPinLoader` to resolve the external `SciTokensHelper` symbol from `libXrdAccSciTokens.so` or a configured token library.
- `findToken()`, `readToken()`, `Strip()`, and `retToken()` implement client-side token discovery and response framing.

## Control Flow
Server initialization parses `-maxsz`, `-expiry`, and `-tokenlib`. Unless `-tokenlib none` is supplied, it loads the token helper plugin and records the helper linkage pointer. `XrdSecProtocolztnObject()` later dereferences that linkage for server instances, while client instances parse server parameters to learn the maximum token size and option/version field.

Client credential creation first handles continuation state. On the first call it searches default token locations in order: `BEARER_TOKEN`, `BEARER_TOKEN_FILE`, `XDG_RUNTIME_DIR/bt_u<uid>`, `/tmp/bt_u<uid>`, and the `xrd.ztn` URL/environment value. File paths are read, permission-checked, stripped of surrounding whitespace, optionally JWT-header-validated, and packed into `TokenResp`. Runtime token fetch support is advertised in the structure but currently ends in `ENOTSUP` if continuation reaches `getToken()`.

Server authentication validates frame size, protocol id, opcode, version, token length, and null termination. It handles `SndAI` through `SendAI()`, which is currently unsupported. For token frames, it optionally calls `XrdSciTokensHelper::Validate()` to populate `Entity`. Depending on expiry mode it rejects missing or expired expiry values. If token validation is disabled or succeeds, it stores the token in `Entity.creds`, ensures `Entity.name` exists, and returns success.

## State And Persistence
Process-global state includes `MaxTokSize`, `expiry`, `tokenlib`, `sth_Linkage`, and `sth_piName`. Protocol instances hold endpoint identity, token-search state, feature options, continuation state, and the `XrdSciTokensHelper` pointer. No token cache is persisted by this file. On the client, token contents are read from environment variables, token files, or URL environment and sent per authentication attempt. Server-side token bytes are copied into `Entity.creds` for downstream authorization.

## Dependencies And Integration Points
Depends on XRootD security interfaces, `XrdOucErrInfo`, `XrdOucTokenizer`, `XrdOucPinLoader`, `XrdNetAddrInfo`, and `XrdSciTokensHelper`. It integrates as an XRootD security plugin through version metadata and C entry points. It relies on `XrdSecztn::isJWT()` from `XrdSecztn.cc` for lightweight JWT header filtering when enabled. It requires TLS via `endPoint.isUsingTLS()`.

## Risks And Edge Cases
- The expiry check compares `monotonic_time()` to token expiry, but token expiry is normally wall-clock epoch time. This should be audited because monotonic time and epoch time are different domains.
- `-expiry` parsing uses `strcmp(val, "ignore")` style tests in a way that appears inverted: nonzero `strcmp` selects the branch. Tests should catch intended values.
- The protocol says runtime token creation may be requested, but `getToken()` and `SendAI()` are unsupported.
- Token file permission checks happen after reading. That limits use of the returned token, but still reads overly permissive files.
- `Strip()` rejects one-character tokens due to `k <= j`, likely acceptable for real JWTs but notable for generic bearer tokens.
- `retToken()` allocates `sizeof(TokenResp) + tsz + 1`; since `TokenResp` already contains `tkn[1]`, this over-allocates by one, which is safe but imprecise.

## Test Signals
Useful tests include plugin init parameter parsing for all `-expiry` modes, TLS rejection, oversized token rejection, token discovery order, unreadable/missing file behavior, permission failure, JWT header filtering, malformed frame rejection, tokenlib-disabled success path, tokenlib validation failure propagation, and server behavior when the helper linkage has not been initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecProtocolztn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecztn.cc -->
# sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecztn.cc

## Purpose
Provides a local helper for deciding whether a bearer token string looks like a JWT. It decodes the base64url header segment and checks for a JSON header containing `"typ":"JWT"`.

## Important APIs, Types, And Functions
- `XrdSecztn::isJWT(const char *b64data)` is the exported helper used by `XrdSecProtocolztn.cc`.
- Anonymous namespace `DecodeBytesNeeded()` sizes a decode buffer.
- Anonymous namespace `DecodeUrl()` performs a base64url-compatible decode using `b64Table`.
- `b64Table` maps ASCII byte values to base64 values or invalid markers.

## Control Flow
`isJWT()` strips a leading `Bearer%20` prefix, finds the first dot, copies only the header segment into a stack buffer, allocates stack decode space, and decodes the segment. The decoded header must start with `{`, end with `}`, contain `"typ"`, then a colon and optional spaces, then `"JWT"`. A failure at any point returns false.

## State And Persistence
The file has only constant lookup-table state. It allocates temporary stack memory with `alloca()` and has no persistent state.

## Dependencies And Integration Points
Uses C/C++ runtime headers and platform-specific `alloca.h`. The only visible integration is the `XrdSecztn` namespace symbol consumed by the ztn security protocol implementation.

## Risks And Edge Cases
- `b64Table[ch]` indexes with `uint8_t`, so high-byte input stays in range, but the table is shorter than 256 entries by inspection risk should be verified at compile time.
- The JSON test is deliberately shallow and whitespace-limited. It does not parse JSON and may reject valid JWT headers with formatting differences or lowercase/alternate typ conventions.
- It accepts `Bearer%20` but not plain `Bearer `.
- It only inspects the header, not signature or claims, which is appropriate for filtering but not validation.

## Test Signals
Exercise JWTs with and without `Bearer%20`, invalid base64url characters, missing dot, long header segment, decoded non-JSON, typ value absent, spaces around the colon, and valid headers with additional fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecztn/XrdSecztn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSfs/CMakeLists.txt

## Purpose
Declares the Standard File System sources that are compiled directly into the `XrdServer` target.

## Important APIs, Types, And Functions
The file contributes `XrdSfsNative.cc`, `XrdSfsInterface.cc`, `XrdSfsXio.cc`, and their public headers to `target_sources(XrdServer PRIVATE ...)`. It does not define runtime APIs itself.

## Control Flow
CMake appends the SFS implementation files to the server target during configuration. Headers are listed as private source entries for IDE visibility and dependency tracking.

## State And Persistence
No runtime state. Build state is limited to target source membership.

## Dependencies And Integration Points
Integrates the SFS native adapter and base interface with the XRootD server build. Because the files are `PRIVATE`, consumers include installed/exported headers through other packaging rules rather than inheriting these target sources.

## Risks And Edge Cases
Missing a header or implementation here can break server builds or hide a changed file from IDE/source package expectations. The file does not list `XrdSfsDio.hh`, although that header is part of the API and included elsewhere; packaging rules should be checked if header installation depends on this list.

## Test Signals
Configure and build `XrdServer`, then verify source-file dependency tracking after touching `XrdSfsInterface.hh`, `XrdSfsNative.cc`, and `XrdSfsXio.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsAio.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsAio.hh

## Purpose
Defines the abstract asynchronous I/O completion object used by SFS file implementations. It wraps a POSIX `aiocb` or a compatibility fallback and adds XRootD-specific completion callbacks and checksum-vector support.

## Important APIs, Types, And Functions
- `XrdSfsAio` contains `sfsAio`, `cksVec`, `Result`, and `TIdent`.
- `doneRead()`, `doneWrite()`, and `Recycle()` are pure virtual callbacks implemented by users of the interface.
- A minimal local `struct aiocb` is supplied when `_POSIX_ASYNCHRONOUS_IO` is unavailable.

## Control Flow
Constructing `XrdSfsAio` initializes the POSIX signal event payload to point back to the object, sets `SIGEV_SIGNAL`, zeroes the request priority, clears the checksum vector pointer, and sets an empty trace identifier. File implementations fill `sfsAio`, execute or schedule work, store the result, and invoke the relevant completion callback.

## State And Persistence
Instances carry request-local state only. `Result` uses nonnegative byte/result values and negative errno-style failures by convention. The class does not own buffers or persist data.

## Dependencies And Integration Points
Included by SFS file implementations and used by `XrdSfsInterface.cc` page I/O defaults and `XrdSfsNative.cc` synchronous AIO emulation. Depends on POSIX signal/AIO headers where available.

## Risks And Edge Cases
- The fallback `aiocb` is only a compile-time compatibility structure; it does not imply real OS AIO support.
- Callback ownership is external. Incorrect `Recycle()` behavior or buffer lifetime can corrupt async completions.
- Platform-specific `sigval_ptr` versus `sival_ptr` handling is guarded for older Apple SDKs.

## Test Signals
Compile on platforms with and without `_POSIX_ASYNCHRONOUS_IO`. Unit-test implementations should verify callback invocation, `Result` propagation, checksum vector use for page I/O, and object recycle ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsAio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsDio.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsDio.hh

## Purpose
Defines the direct I/O/sendfile interface that an SFS file implementation can use to transfer file data to a client without normal read-buffer copying.

## Important APIs, Types, And Functions
- `XrdSfsDio::SendFile(int fildes)` sends the requested data from one descriptor.
- `XrdSfsDio::SendFile(XrdOucSFVec *sfvec, int sfvnum)` sends a vector of sendfile descriptors, reserving the first vector element for framing.
- `XrdSfsDio::SetFD(int fildes)` switches future processing between read path, fast sendfile path, and descriptor-disabled mode.

## Control Flow
The server learns whether direct I/O should be used through `XrdSfsFile::fctl()` and then passes an `XrdSfsDio` object to `SendData()`. A filesystem either delegates to `SendFile()` once or returns `SFS_OK` without sending so the caller falls back to normal reads.

## State And Persistence
This is an abstract interface. Concrete implementations track whether data has already been sent and which descriptor mode is active. No persistence is defined here.

## Dependencies And Integration Points
Depends on `XrdOucSFVec` for vectorized sendfile operations and integrates with `XrdSfsFile::SendData()` and `SFS_FCTL_GETFD`/`SFS_SFIO_FDVAL` conventions.

## Risks And Edge Cases
The API treats multiple sends for a single request and oversized vectors as logic errors signaled by positive returns. Implementations must return negative values for fatal transport errors so callers close the connection. Descriptor lifetime remains the filesystem's responsibility.

## Test Signals
Mock `XrdSfsDio` implementations should verify single-descriptor sends, vector sends with reserved first element, duplicate-send error handling, negative transport failures, and `SetFD()` mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsDio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFAttr.hh

## Purpose
Defines request and result structures for SFS extended file attribute operations routed through `XrdSfsFileSystem::FAttr()`.

## Important APIs, Types, And Functions
- `XrdSfsFAInfo` describes one attribute name, value, aligned value length, name length, and per-entry return code.
- `XrdSfsFABuff` is a linked buffer used for additional allocated attribute data.
- `XrdSfsFACtl` is the main control block, carrying logical/physical paths, CGI, environment pointer, namespace prefix, request type, options, and an array of `XrdSfsFAInfo`.
- `XrdSfsFACtl::RQST` values are `faDel`, `faGet`, `faLst`, `faSet`, and `faFence`.
- Options include `accChk`, `newAtr`, `xplode`, `retvsz`, and `retval`.

## Control Flow
Callers construct `XrdSfsFACtl` with a path, opaque CGI, and attribute count, then a filesystem implementation interprets `rqst` and `opts`. The destructor frees linked buffers and deletes the `info` array, making it the ownership boundary for allocations recorded in the control block.

## State And Persistence
The structure is request-scoped. It can point at logical and physical paths and may carry allocated buffers for returned attribute lists or values. Actual xattr persistence is delegated to filesystem implementations.

## Dependencies And Integration Points
Forward-depends on `XrdOucEnv`. Included by the SFS interface where `FAttr()` is declared. It bridges protocol-level xattr commands and physical filesystem/plugin-specific xattr operations.

## Risks And Edge Cases
Ownership is mixed: `XrdSfsFACtl` frees `fabP` and `info`, but not path strings, values, or environment pointers unless stored in those buffers. Implementations must set `VLen`, `NLen`, and `faRC` consistently for list expansion and return-value modes.

## Test Signals
Tests should cover construction/destruction with zero and multiple attributes, list expansion with `xplode`, return-size versus return-value modes, per-attribute error codes, and namespace-prefix handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFlags.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFlags.hh

## Purpose
Defines SFS feature bits and stat-mode/device markers that plugins use to advertise capabilities and special file states.

## Important APIs, Types, And Functions
- Feature bits in namespace `XrdSfs`: `hasAUTZ`, `hasCHKP`, `hasGPF`, `hasGPFA`, `hasPGRW`, `hasPOSC`, `hasPRP2`, `hasPRXY`, `hasSXIO`, `hasNOSF`, `hasCACH`, `hasNAIO`, and `hasFICL`.
- `XRDSFS_POSCPEND` maps close-pending POSC state to `S_ISUID` on Solaris and `S_ISVTX` elsewhere.
- `XRDSFS_OFFLINE`, `XRDSFS_HASBKUP`, and `XRDSFS_RDVMASK` encode special regular-file attributes in the high byte of `st_rdev`.

## Control Flow
There is no executable control flow. Filesystems set feature bits in `XrdSfsFileSystem::FeatureSet`, and callers inspect `Features()` to decide optional behavior. Stat consumers inspect `st_rdev` markers only when the remaining `XRDSFS_RDVMASK` bits are zero.

## State And Persistence
Feature constants are compile-time values. POSC and offline/backup markers may be persisted indirectly through filesystem mode/stat metadata when implementations choose to encode them.

## Dependencies And Integration Points
Included by `XrdSfsInterface.cc` and filesystem plugins. It ties optional SFS capabilities to server behavior, including page read/write, checkpointing, third-party transfers, sendfile disabling, and exchange-buffer I/O.

## Risks And Edge Cases
Feature-bit compatibility depends on stable numeric values. Device-bit encoding assumes enough width in `dev_t` and may interact poorly with real device values if mask checks are wrong. POSC mode-bit choice is platform-specific.

## Test Signals
Verify feature negotiation from `XrdSfsFileSystem::Features()`, offline/backup stat interpretation with masked and unmasked `st_rdev`, and POSC marker behavior on Solaris and non-Solaris builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsFlags.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsGPFile.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsGPFile.hh

## Purpose
Defines the request object and callback contract for third-party file movement through `XrdSfsFileSystem::gpFile()`.

## Important APIs, Types, And Functions
- `XrdSfsGPFile` carries transfer options, source/destination, local CGI, checksum type/value, trace id, parallelism hints, and an implementation-private union `gpfInfo`/`gpfID`.
- Option bits include `replace`, `mkPath`, `keepErr`, `delegate`, `verCKS`, and `useTLS`.
- `Finished(int rc, const char *emsg)` completes and deletes the request object by contract.
- `Status(GPFState state, uint32_t cpct, uint64_t bytes)` reports progress in pending, transfer, or checksum-validation states.

## Control Flow
Callers fill the object and invoke `gpFile()` with get, put, or cancel. Implementations either accept the request and report progress asynchronously or fail synchronously. On final completion they must call `Finished()` and stop referencing the object.

## State And Persistence
The object is request-scoped and stores both immutable request fields and implementation-private state. Actual file persistence and transfer checkpoints are implementation-defined.

## Dependencies And Integration Points
Included by `XrdSfsInterface.hh`. Integrates with third-party copy support, checksum validation, TLS/delegation policy, and status callbacks to clients.

## Risks And Edge Cases
`Finished()` deletes the object by API contract, so use-after-finish is a primary risk. Cancel handling must coordinate with in-flight async transfers. Implementations must honor `keepErr`, `replace`, and checksum verification semantics to avoid data loss.

## Test Signals
Cover get/put/cancel, option bit combinations, progress callback cadence via `pingsec`, checksum validation success/failure, failure cleanup with `keepErr`, and object lifetime after `Finished()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsGPFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.cc -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.cc

## Purpose
Provides default method implementations for the SFS abstract interfaces. These defaults give conservative behavior for optional features, fallback page I/O, vector I/O, and base filesystem feature initialization.

## Important APIs, Types, And Functions
- `XrdSfsDirectory::autoStat()` defaults to `ENOTSUP`.
- `XrdSfsFile::checkpoint()`, `Clone()`, `fctl(v2)`, `pgRead()`, `pgWrite()`, `read(range list)`, `readv()`, `SendData()`, and `writev()` define fallback behavior for optional methods.
- `XrdSfsFileSystem::XrdSfsFileSystem()` initializes `FeatureSet`.
- `XrdSfsFileSystem::chksum()`, `FAttr()`, `FSctl()`, and `gpFile()` provide defaults.

## Control Flow
Most unsupported optional features set `XrdOucErrInfo` to `ENOTSUP` and return `SFS_ERROR`. Page reads call scalar `read()` then compute CRCs with `XrdOucPgrwUtils::csCalc()`. Page writes optionally verify CRCs with `csVer()` when `Verify` is set, then call scalar `write()`. AIO page operations execute synchronously through the scalar page methods, set `aioparm->Result`, and invoke completion callbacks. Vector reads/writes loop over each `XrdOucIOVec` and fail if any scalar operation transfers less than requested.

## State And Persistence
No persistent data is stored here. The filesystem constructor sets `FeatureSet` to `hasPGRW` and adds `hasCHKP` if `getChkPSize()` reports a positive value. File methods use each object's shared `error` reference for error state.

## Dependencies And Integration Points
Depends on `XrdOucPgrwUtils`, `XrdOucCloneSeg`, `XrdSfsAio`, `XrdSfsFlags`, and the SFS interface declarations. These defaults are inherited by all SFS plugins unless overridden, so they are central compatibility behavior for older plugins.

## Risks And Edge Cases
- Default `FSctl()` returns `SFS_OK` without doing anything, unlike many other unsupported operations. Callers must know command-specific semantics.
- Vector I/O treats short reads/writes as `ESPIPE`, which can mask EOF versus storage errors.
- AIO defaults are synchronous despite the async signature.
- Page write verification assumes the checksum vector layout matches offset and length exactly.

## Test Signals
Tests should assert default errors and return codes, page CRC calculation/verification, AIO callback invocation, vector short-transfer failures, `FeatureSet` initialization when checkpoint size is overridden, and no-op `FSctl()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.hh

## Purpose
Defines the core Standard File System plugin ABI for XRootD. It specifies open flags, return codes, request structures, directory/file object interfaces, filesystem-wide operations, and plugin entry-point typedefs.

## Important APIs, Types, And Functions
- Open flags such as `SFS_O_RDONLY`, `SFS_O_CREAT`, `SFS_O_POSC`, `SFS_O_RAWIO`, `SFS_O_REPLICA`, and `SFS_O_MKPTH`.
- Return codes `SFS_OK`, `SFS_ERROR`, `SFS_REDIRECT`, `SFS_STALL`, `SFS_STARTED`, `SFS_DATA`, and `SFS_DATAVEC`.
- `XrdSfsDirectory` declares directory `open()`, `nextEntry()`, `close()`, `FName()`, and optional `autoStat()`.
- `XrdSfsFile` declares file open/close, fctl, mmap, page I/O, scalar/vector read/write, sendfile hook, stat, sync, truncate, compression info, and optional exchange-buffer setup.
- `XrdSfsFileSystem` declares object factories and namespace/filesystem operations such as checksum, chmod, exists, FAttr, FSctl/fsctl, stats, gpFile, mkdir, prepare, remove, rename, stat, and truncate.
- `XrdSfsFileSystem2_t` and `XrdSfsFileSystem_t` define new and legacy plugin factory signatures.

## Control Flow
The server obtains an `XrdSfsFileSystem` implementation through a plugin entry point, creates per-request file/directory objects through `newFile()` and `newDir()`, and invokes virtual methods using the return-code and `XrdOucErrInfo` contract. Optional capabilities are discovered through `Features()` and through default virtual implementations. Wrapping guidance in the header defines how wrappers should share the same `XrdOucErrInfo` across chains.

## State And Persistence
`XrdSfsDirectory` and `XrdSfsFile` own or borrow an `XrdOucErrInfo` reference depending on constructor choice. `XrdSfsFileSystem` owns a protected `FeatureSet`. Actual namespace, file data, caching, checkpoints, and transfer persistence are delegated to implementations.

## Dependencies And Integration Points
Depends on XRootD OUC range/IO/error types, `XrdSfsGPFile`, and system stat types. It is the ABI boundary used by native SFS, SSI SFS wrappers, authorization/cache layers, and third-party filesystem plugins.

## Risks And Edge Cases
- ABI stability is critical because plugins compile against this header.
- Return-code semantics overload `XrdOucErrInfo.code` for errors, redirects, stalls, data lengths, and async estimates.
- Wrapper constructors require careful error-object propagation; mixed ownership can cause stale pointers or duplicate deletes.
- Some flags intentionally share numeric ranges for different contexts, so callers must mask appropriately.

## Test Signals
ABI/compile tests for plugins, wrapper-chain tests verifying a shared error object, return-code contract tests for redirect/stall/data responses, feature negotiation tests, and compatibility tests for both plugin factory signatures are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.cc -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.cc

## Purpose
Implements the native POSIX-backed SFS filesystem used as the basic local filesystem adapter. It maps SFS directory, file, and namespace operations onto Unix system calls and exposes an `XrdSfsGetFileSystem()` factory.

## Important APIs, Types, And Functions
- `XrdSfsUFS` wraps POSIX `chmod`, `close`, `mkdir`, `open`, `unlink`, `rmdir`, `rename`, `fstat`, `stat`, and `truncate`.
- `XrdSfsNativeDirectory` implements `open()`, `nextEntry()`, and `close()`.
- `XrdSfsNativeFile` implements `open()`, `close()`, `fctl(SFS_FCTL_GETFD)`, scalar/vector reads and writes, synchronous AIO callbacks, `stat()`, `sync()`, and `truncate()`.
- `XrdSfsNative` implements filesystem-level `chmod`, `exists`, `fsctl`, `mkdir`, `Mkpath`, `rem`, `remdir`, `rename`, `stat`, `truncate`, and `Emsg`.
- `XrdSfsGetFileSystem()` returns a static `XrdSfsNative` instance.

## Control Flow
Directory open rejects reuse, stores the directory name, and calls `opendir()`. `nextEntry()` checks open state, preserves EOF once reached, and uses `readdir()` on Linux/GNU/FreeBSD-glibc or `readdir_r()` elsewhere. Close releases the directory handle and path string.

File open rejects reuse, translates SFS access/create/truncate flags to POSIX open flags, optionally creates parent directories with `Mkpath()`, opens the file, verifies it is a regular file, and maps directory/non-regular cases to errors. Reads and writes use `pread()`/`pwrite()` loops retrying `EINTR`. Vector reads require every element to transfer exactly the requested size. AIO methods execute synchronously, set `Result`, and call completion methods. Filesystem namespace methods call the corresponding POSIX operation and centralize error formatting through `Emsg()`.

## State And Persistence
The filesystem object is static and stores a static logger/error destination pointer. Directory instances hold `DIR *`, EOF state, and copied path. File instances hold a file descriptor and copied path. Persistence is entirely the underlying POSIX filesystem: creates, writes, truncates, renames, chmods, and removals affect local storage immediately, subject to `fsync()` when `sync()` is called.

## Dependencies And Integration Points
Depends on POSIX directory/file APIs, `XrdSysError`, `XrdSysE2T`, `XrdSysLogger`, `XrdSecInterface`, and SFS headers. Integrates as the native filesystem passed to higher-level filesystem plugins and as a fallback server filesystem implementation.

## Risks And Edge Cases
- `XrdSfsNativeFile::~XrdSfsNativeFile()` checks `if (oh) close();`; descriptor `0` would not be closed, while `-1` is truthy and calls `close()` harmlessly. Normally `open()` may return fd 0 in unusual environments, so this is worth auditing.
- `open()` stores `fname = strdup(path)` before all failure paths; failures before `close()` may leak `fname`.
- `mkdir()` calls `Mkpath()` for `SFS_O_MKPTH` but ignores its return before attempting the final `mkdir()`.
- `getMmap()` uses `if (Addr) Addr = 0`, which does not clear `*Addr`.
- `exists()` maps non-directory/non-regular existing objects to `XrdSfsFileExistNo` rather than `XrdSfsFileExistIsOther`.

## Test Signals
Run filesystem contract tests for create/open/truncate/read/write/sync/stat/rename/remove, directory iteration EOF and error reporting, path creation, large-offset guards on 32-bit builds, descriptor-return `fctl`, non-regular file open rejection, and failure cleanup after open errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.hh

## Purpose
Declares the native POSIX SFS implementation classes used by `XrdSfsNative.cc`.

## Important APIs, Types, And Functions
- `XrdSfsNativeDirectory : XrdSfsDirectory` declares directory open, iteration, close, and `FName()`.
- `XrdSfsNativeFile : XrdSfsFile` declares file open/close, descriptor fctl, mmap/compression stubs, preread no-op, scalar/vector read/write, sync, stat, and truncate.
- `XrdSfsNative : XrdSfsFileSystem` declares object factories and namespace operations plus static `Mkpath()` and `Emsg()`.

## Control Flow
Factories allocate concrete native directory/file objects. Inline stubs return success for preread, zero stats, default prepare, no compression, and mode-stat forwarding. The implementation file supplies all real POSIX calls.

## State And Persistence
Directory state consists of `DIR *`, EOF flag, path string, and a portable `dirent` buffer. File state consists of descriptor `oh` and path string. Filesystem state consists of static `eDest` for logging. Persistent behavior is delegated to POSIX storage.

## Dependencies And Integration Points
Depends on `XrdSfsInterface.hh`, `dirent.h`, and `XrdSysError`/`XrdSysLogger` forward declarations. This header is used by the server-native SFS module and potentially by wrappers that need native-specific declarations.

## Risks And Edge Cases
Inline methods mirror implementation risks: `getMmap()` does not clear `*Addr`; `getCXinfo()` returns assignment value `0` instead of an SFS return code; destructor descriptor handling depends on `oh` truthiness. API signatures use `XrdSecClientName` aliases from the security interface, so type compatibility must be preserved.

## Test Signals
Compile native SFS against the current interface, instantiate file/directory factories, verify inline mode-stat forwarding and stub return values, and run destructor/close tests for unopened and descriptor-zero cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.cc -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.cc

## Purpose
Implements the static portions of the SFS exchange-buffer I/O interface by forwarding `XrdSfsXio::Buffer()` and `XrdSfsXio::Reclaim()` to a process-global implementation object.

## Important APIs, Types, And Functions
- Anonymous `Impl` stores static `XrdSfsXioImpl *xio`.
- `XrdSfsXio::XrdSfsXio(XrdSfsXioImpl &xioimpl)` initializes the global implementation through a function-local static `Impl`.
- `XrdSfsXio::Buffer()` and `Reclaim()` forward to function pointers in `XrdSfsXioImpl`.

## Control Flow
The first construction of an `XrdSfsXio` object initializes the static `Impl dummy` with the supplied implementation. Subsequent constructions do not replace it. Static calls dereference the stored implementation and invoke the configured buffer/reclaim functions.

## State And Persistence
Maintains one process-global implementation pointer for all exchange-buffer static methods. It does not persist buffer contents; ownership is handled by the implementation.

## Dependencies And Integration Points
Depends on `XrdSfsXio.hh` and `XrdSfsXioImpl.hh`. Integrates with file implementations that opt into exchange-buffer I/O via `XrdSfsFile::setXio()`.

## Risks And Edge Cases
- Static methods crash if called before any `XrdSfsXio` instance initializes `Impl::xio`.
- Only the first implementation wins. Mixed implementations in one process are unsupported.
- Thread-safe initialization relies on C++ function-local static semantics.

## Test Signals
Construct an implementation and verify static forwarding, call ordering before initialization, repeated construction with different implementations, and concurrent first-use behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.hh

## Purpose
Defines the exchange-buffer I/O interface that lets SFS file implementations claim or swap server I/O buffers to reduce data copying on writes.

## Important APIs, Types, And Functions
- `XrdSfsXioHandle` is an `XrdBuffer *` handle.
- Static `Buffer(handle, size*)` obtains a buffer address and size.
- `Claim(curBuff, datasz, minasz)` transfers ownership of the current buffer when efficient.
- Static `Reclaim(handle)` returns a claimed/swapped buffer.
- `Swap(curBuff, oldHand)` atomically takes ownership of the current buffer and optionally returns a previous one.

## Control Flow
When a file supports exchange I/O, the server calls `setXio()` on the `XrdSfsFile`. During write handling, the filesystem can `Claim()` the current buffer or `Swap()` it with a previous handle. Later it calls static `Reclaim()` when ownership should return to the framework.

## State And Persistence
The abstract object itself has no state beyond the static implementation installed by construction. Handles represent transient buffer ownership, not persistent file data.

## Dependencies And Integration Points
Forward-depends on `XrdBuffer` and `XrdSfsXioImpl`. Tied to `XrdSfs::hasSXIO` feature advertisement and `XrdSfsFile::setXio()`.

## Risks And Edge Cases
Incorrect `curBuff` matching returns `EINVAL`, memory pressure can return `ENOBUFS`, and unsupported contexts return `ENOTSUP`. Failure to reclaim handles leaks buffers. This API is write-oriented and not a general read-buffer exchange mechanism.

## Test Signals
Mock implementations should cover successful claim/swap/reclaim, stale current-buffer pointers, old-handle replacement, memory-waste rejection with `errno == 0`, and file close cleanup of outstanding handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXioImpl.hh -->
# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXioImpl.hh

## Purpose
Defines the private implementation hook used by `XrdSfsXio` static methods.

## Important APIs, Types, And Functions
- `XrdSfsXioImpl::Buffer_t` and `Reclaim_t` are function-pointer types.
- Members `Buffer` and `Reclaim` hold the active implementations.
- Constructor stores the two function pointers.

## Control Flow
An `XrdSfsXio` subclass constructs an `XrdSfsXioImpl` with concrete static functions and passes it to the `XrdSfsXio` base constructor. `XrdSfsXio.cc` then forwards static calls through these pointers.

## State And Persistence
Only stores function pointers. It owns no buffers and has no persistence.

## Dependencies And Integration Points
Includes `XrdSfsXio.hh` for handle types. It is intended as a private interface for exchange-buffer implementations, not as an end-user plugin API.

## Risks And Edge Cases
Null function pointers are not guarded in the constructor or callers. Lifetime must exceed all static forwarding calls because `XrdSfsXio.cc` stores the pointer globally.

## Test Signals
Verify construction with valid functions, static forwarding through `XrdSfsXio`, and failure behavior if a null or short-lived implementation is supplied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXioImpl.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSsi/CMakeLists.txt

## Purpose
Builds the SSI libraries and server modules: the reusable SSI client/server support library, shared-memory map library, SSI filesystem module, and SSI logging module.

## Important APIs, Types, And Functions
- `XrdSsiLib` is a shared library containing alerting, atomics, client provider, request/response, service/session/task, logging, stats, and utilities.
- `XrdSsiShMap` is a shared library for shared-memory map support and links `ZLIB::ZLIB`.
- `${XrdSsi}` is a module containing SFS-facing SSI files, stat hooks, and configuration.
- `${XrdSsiLog}` is a module for logging integration.

## Control Flow
CMake creates targets, links them to `XrdCl`, `XrdUtils`, `XrdServer`, and zlib as needed, sets shared-library version properties on libraries, and installs all four runtime targets to the library directory.

## State And Persistence
No runtime state. Build outputs include shared libraries/modules whose names include `${PLUGIN_VERSION}` for modules.

## Dependencies And Integration Points
Integrates SSI with both XRootD client (`XrdCl`) and server (`XrdServer`) components. The SFS module links against `XrdSsiLib`, making the target files in this subset part of the core SSI runtime used by server plugins and client applications.

## Risks And Edge Cases
Target membership controls symbol availability across modules. Moving a source between `XrdSsiLib` and `${XrdSsi}` can change exported/loaded behavior. Missing version properties on modules may be intentional due plugin naming, but packaging should verify installed ABI expectations.

## Test Signals
Configure/build/install tests should validate all four targets, link dependencies, module names with plugin version, shared-library SONAME/version, and zlib availability for `XrdSsiShMap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.cc

## Purpose
Implements pooled SSI alert callback objects used to return asynchronous attention/alert metadata to requestors.

## Important APIs, Types, And Functions
- Static pool members `aMutex`, `free`, `fNum`, and `fMax`.
- `XrdSsiAlert::Alloc()` obtains an alert object from the pool or allocates a new one and binds it to an `XrdSsiRespInfoMsg`.
- `Done()` deletes callback error info and recycles the alert.
- `Recycle()` releases the response message and returns the alert object to the bounded pool.
- `SetInfo()` formats an alert response into an `XrdOucErrInfo` message buffer as an iovec response containing `XrdSsiRRInfoAttn`.

## Control Flow
Allocation locks the pool, pops a free object if available, unlocks, clears `next`, and records `theMsg`. When the async callback completes, `Done()` deletes the callback-owned `XrdOucErrInfo` and calls `Recycle()`. Recycle calls `theMsg->RecycleMsg()` if present, then either deletes the alert if the pool is full or pushes it onto the free list. `SetInfo()` uses the existing error-info message buffer to build an iovec array: one slot for framework framing, one for the attention header, and one for alert payload.

## State And Persistence
Maintains a process-local bounded free list of alert objects, default max 100. Alert payload ownership belongs to `XrdSsiRespInfoMsg` and is released via `RecycleMsg()`. No alert data is persisted.

## Dependencies And Integration Points
Depends on `XrdOucErrInfo`, `XrdSsiAlert.hh`, and `XrdSsiRRInfo.hh`. Implements `XrdOucEICB` callback behavior used by SSI request/response paths.

## Risks And Edge Cases
- `SetInfo()` copies debug bytes with `sizeof(aMsg)`, but `aMsg` is a pointer, so this is pointer-size rather than caller-buffer-size based.
- `SetInfo()` assumes the error-info message buffer is large enough for `AlrtResp`.
- Pool state is protected by `XrdSysMutex`, but `theMsg` is not cleared before pooling, so reuse depends on `Alloc()` always resetting it.
- `Done()` always deletes `eiP`; callers must allocate it accordingly.

## Test Signals
Test pool reuse and max-size trimming, `RecycleMsg()` invocation, iovec/header formatting including network byte order, callback ownership of `XrdOucErrInfo`, and alert payload lengths including zero and large messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.hh

## Purpose
Declares the SSI alert callback object that bridges response alert messages into XRootD error-info callback delivery.

## Important APIs, Types, And Functions
- `XrdSsiAlert : XrdOucEICB` with public `next` for free-list linking.
- Static `Alloc()`, `SetMax()`, and instance `Recycle()`.
- `SetInfo()` populates `XrdOucErrInfo` with metadata for alert transmission.
- `Done()` and `Same()` implement `XrdOucEICB`; `Same()` always returns false.

## Control Flow
Users allocate alerts through `Alloc()` rather than constructing directly, pass them as callbacks, then `Done()` recycles them after the underlying query/response signal completes. Pool sizing is controlled with `SetMax()`.

## State And Persistence
The class owns static pool state and per-object pointer `theMsg` to the response message currently being delivered. It persists only reusable callback objects in memory.

## Dependencies And Integration Points
Includes `XrdOucErrInfo`, `XrdSsiRequest.hh`, and `XrdSysPthread.hh`. The callback inheritance connects it to OUC async response machinery.

## Risks And Edge Cases
Because `next` is public and used for pooling, external misuse could corrupt the free list. The header does not document ownership expectations for `theMsg` or callback error info; the implementation assumes `Done()` owns `eiP`.

## Test Signals
Compile tests for `XrdOucEICB` compatibility, allocation/recycle lifecycle tests, pool size changes via `SetMax()`, and callback dispatch tests through SSI request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.cc

## Purpose
Provides the out-of-line error text helper for `XrdSsiMutex` construction failures.

## Important APIs, Types, And Functions
- `XrdSsiMutex::Errno2Text(int ecode)` returns `XrdSysE2T(ecode)`.

## Control Flow
When `XrdSsiMutex` construction fails in the header-defined constructor, it throws the result of `Errno2Text(rc)`. This file supplies the private member implementation.

## State And Persistence
No local state or persistence.

## Dependencies And Integration Points
Includes `XrdSsiAtomics.hh` and `XrdSysE2T.hh`. It links the header-only mutex wrapper to XRootD errno-to-text formatting.

## Risks And Edge Cases
The thrown pointer references text owned by `XrdSysE2T()` semantics. Callers catching exceptions should treat it as a message pointer, not owned storage.

## Test Signals
Compile/link tests should ensure `XrdSsiMutex` construction references resolve. Fault-injection tests can force `pthread_mutex_init` failures and verify a non-null message is thrown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.hh

## Purpose
Provides SSI portability macros for atomic counters/flags and lightweight mutex RAII helpers.

## Important APIs, Types, And Functions
- `Atomic(type)` and operations `Atomic_INC`, `Atomic_DEC`, `Atomic_GET`, `Atomic_GET_STRICT`, `Atomic_SET`, `Atomic_SET_STRICT`, and `Atomic_ZAP`.
- Implementation selector `Atomic_IMP` chooses C++11 atomics, GCC `__atomic`, GCC `__sync`, or a mutex-required fallback.
- `XrdSsiMutex` wraps `pthread_mutex_t` with simple or recursive construction.
- `XrdSsiMutexMon` is an RAII monitor that can lock, switch, reset, and unlock an `XrdSsiMutex`.

## Control Flow
At compile time the header selects one atomic implementation. C++11 uses relaxed operations by default and acquire/release for strict get/set. Legacy GCC paths use builtin atomics. The fallback defines `NEED_ATOMIC_MUTEX` and wraps ordinary operations in caller-provided mutex lock/unlock macros. `XrdSsiMutexMon` locks on construction when provided a mutex and unlocks on destruction.

## State And Persistence
Macros operate on caller-owned variables. Mutex classes own a `pthread_mutex_t` and release it in the destructor. No persistence beyond process synchronization state.

## Dependencies And Integration Points
Used throughout SSI for global counters and init flags, including `XrdSsiClient.cc`. Depends on pthreads and optionally C++ `<atomic>`. `XrdSsiAtomics.cc` supplies error text conversion.

## Risks And Edge Cases
- Relaxed memory order is used for most operations; only strict variants carry acquire/release semantics.
- Fallback macro set lacks `Atomic_GET_STRICT` and `Atomic_SET_STRICT` definitions, which can break code if fallback is active.
- `Atomic_DEC` and `Atomic_INC` return the pre-operation value for C++ and GCC builtins, not the new value; callers must know the convention.
- The mutex constructor throws a `const char *`, which is unusual for C++ exception handling.

## Test Signals
Build tests across C++11 and legacy atomic configurations, concurrency tests for init flags and counters, recursive mutex behavior, RAII lock switching in `XrdSsiMutexMon`, and fallback build validation if atomics are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiBVec.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiBVec.hh

## Purpose
Defines a compact bit-vector helper optimized for small integer values while supporting arbitrary larger values through a set.

## Important APIs, Types, And Functions
- `Set(uint32_t bval)` records a value.
- `IsSet(uint32_t bval)` checks membership.
- `UnSet(uint32_t bval)` removes a value.
- `Reset()` clears all values.

## Control Flow
Values below 64 are stored in a `uint64_t` bit mask. Values 64 and above are stored in `std::set<uint32_t>`. Each operation branches on the threshold and updates or queries the appropriate backing store.

## State And Persistence
Instances hold an in-memory bit mask and set. No synchronization or persistence is provided.

## Dependencies And Integration Points
Depends on `<set>` and `<cstdint>`. It is a utility for SSI components that need sparse/mostly-small membership tracking.

## Risks And Edge Cases
Not thread-safe without external locking. The expression `1LL << bval` is safe only because `bval < 64`, but uses a signed literal; `1ULL` would avoid signed-shift concerns at bit 63.

## Test Signals
Test set/check/unset for values 0, 1, 63, 64, large values, repeated operations, reset behavior, and independence between bit-mask and set-backed ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiBVec.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiClient.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiClient.cc

## Purpose
Implements the global SSI client provider (`XrdSsiProviderClient`) used by applications to obtain `XrdSsiService` instances for contact endpoints. It lazily initializes logging, scheduling, XrdCl environment defaults, and contact dispatch policy.

## Important APIs, Types, And Functions
- Namespace globals include `clMutex`, `schedP`, `clEnvP`, `contactN`, `maxTCB`, `maxCLW`, `maxPEL`, `initDone`, timeout-set flags, `hiResTime`, and request-dispatch mode `rDisp`.
- `XrdSsiClientProvider : XrdSsiProvider` implements `GetService()`, `SetCBThreads()`, `SetConfig()`, `SetSpread()`, and `SetTimeout()`.
- Private helpers `SetLogger()` and `SetScheduler()` create `XrdSysLogger`, configure trace/log callbacks, allocate `XrdScheduler`, and start it.
- Global `XrdSsiProvider *XrdSsiProviderClient` points to a static provider instance.

## Control Flow
`GetService()` performs first-use initialization under `clMutex`: create logger, scheduler, XrdCl default environment, install effectively infinite defaults for data server TTL, request timeout, and stream timeout unless explicitly set, configure poller count, and optionally disable IP shuffling for none/round-robin dispatch. It then validates the contact string. Multi-contact or non-singleton contacts are registered in `XrdNetRegistry` under generated `contact-N` names with optional rotation. Singleton contacts are validated and formatted through `XrdNetAddr`. On success, it returns a new `XrdSsiServReal` with the resolved contact and hold value.

Configuration calls update globals under the same mutex where needed. `SetCBThreads()` caps callback threads and derives network worker count from callback count when not supplied. `SetConfig()` accepts `cbThreads`, `hiResTime`, `netThreads`, `pollers`, and `reqDispatch`. `SetTimeout()` writes XrdCl environment keys for connection retry/window, idle close, request timeout, and stream timeout, marking user-set timeouts to prevent first-use defaults from overriding them.

## State And Persistence
The provider is process-global. It persists scheduler, logger, XrdCl environment settings, contact registry entries, dispatch policy, and thread-count configuration for the process lifetime. It does not persist service state across process restarts.

## Dependencies And Integration Points
Depends on XRootD scheduler/trace, XrdCl default environment, XrdNet address/registry utilities, SSI logger/provider/service classes, scale utilities, and atomic/mutex wrappers. It is the client-side entry point for SSI services and returns `XrdSsiServReal` objects.

## Risks And Edge Cases
- `initDone = true` uses direct assignment rather than `Atomic_SET`; with C++11 `std::atomic<bool>` this is valid, but legacy macro modes may differ.
- `SetScheduler()` checks `clEnvP` before setting worker threads, but first-use initialization calls `SetScheduler()` before assigning `clEnvP`, causing it to fetch the default environment inside the helper.
- Contact registry names use an atomic post-increment counter; overflow is unlikely but not handled.
- Empty contact fails early, but malformed multi-contact errors depend on `XrdNetRegistry::Register()`.
- Global settings after first service creation may not retroactively affect already-created scheduler/environment behavior.

## Test Signals
Tests should cover first-use lazy initialization, empty contact failure, singleton contact validation, multi-contact registry creation with round-robin/random/no dispatch, callback/network thread settings, timeout settings before and after initialization, high-resolution logging via option and environment, and concurrent `GetService()` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCluster.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCluster.hh

## Purpose
Defines the server-cluster management interface passed to SSI server providers so they can report endpoint names, service availability, resource capacity, managers, and utilization.

## Important APIs, Types, And Functions
- `Added(name, pend)` and `Removed(name)` publish logical resource availability.
- `DataContext()` distinguishes data-server context from metadata-manager context.
- `Managers(int &mNum)` returns the permanent manager-node list.
- `Suspend(perm)` and `Resume(perm)` control service availability.
- `Resource(n)`, `Reserve(n)`, and `Release(n)` manage resource units and dispatch suspension/resume.
- `Utilization(util, alert)` reports server utilization to managers.

## Control Flow
Implementations track cluster-visible names and resource levels. Reserving resources can temporarily suspend dispatch when capacity becomes non-positive; releasing resources can resume dispatch when capacity becomes positive. Utilization reports may be throttled unless `alert` is true.

## State And Persistence
This header defines no state, but implementations are expected to persist permanent suspend/resume decisions across server restarts when `perm` is true and to maintain current resource counters and advertised names during runtime.

## Dependencies And Integration Points
Pure abstract interface with no includes. It is consumed by SSI server/provider startup and lets application-level SSI services interact with XRootD clustering and manager selection.

## Risks And Edge Cases
Resource accounting must be thread-safe in implementations. Permanent versus temporary suspend semantics must be clear to avoid unintentionally draining a server after restart. Manager-list lifetime is specified as permanent and must not be freed by callers.

## Test Signals
Implementation tests should verify added/removed name propagation, data/meta context reporting, permanent manager-list lifetime, suspend/resume persistence flags, resource counter bounds, reserve/release transitions around zero, and utilization alert throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiCluster.hh -->
