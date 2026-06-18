<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TreeConnectHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TreeConnectHelper.cs

## Purpose
SMB1 tree-connect command handling for disk shares and the special `IPC$` named-pipe share. It validates the requested service type, resolves the UNC share name, checks share-level access for disk roots, allocates a SMB1 tree ID, and builds normal or extended `TreeConnectAndX` responses.

## APIs, Types, and Functions
The main entry points are `TreeConnectHelper.GetTreeConnectResponse()` and `GetTreeDisconnectResponse()`. Private helpers map `CachingPolicy` to SMB1 `OptionalSupportFlags` and build `TreeConnectAndXResponse` or `TreeConnectAndXResponseExtended` with maximal access masks.

## Control Flow, State, and Persistence
The helper reads the active `SMB1Session` from `SMB1ConnectionState`, parses `request.Path` with `ServerPathUtils.GetShareName()`, chooses either `NamedPipeShare` or `SMBShareCollection.GetShareFromName()`, and stores successful connections in the session with `AddConnectedTree()`. Disconnect removes the tree from the session. No durable persistence is used; state is per connection/session.

## Dependencies and Integration
Integrated from `SMBServer.SMB1.cs` after UID validation. It depends on SMB1 command models, `NamedPipeShare`, `FileSystemShare`, `SMBShareCollection`, access checks driven by `AccessRequested`, and server logging.

## Risks and Test Signals
Risks include casts to `FileSystemShare` for non-IPC shares, share-root access checks that may not reflect path-specific policy, and extended response access masks that advertise broad rights independent of the backing store. Test SMB1 tree connect to missing shares, wrong service type, denied root access, `IPC$`, caching-policy variants, tree ID exhaustion, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TreeConnectHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CancelHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CancelHelper.cs

## Purpose
SMB2 cancel handling for asynchronous operations. It locates an async context by `AsyncID`, asks the backing file store to cancel the captured I/O request, and returns the required async `STATUS_CANCELLED` error response only when cancellation is accepted.

## APIs, Types, and Functions
`CancelHelper.GetCancelResponse(CancelRequest, SMB2ConnectionState)` is the only entry point. It uses `SMB2AsyncContext`, `SMB2Session`, `OpenFileObject`, `ISMBShare.FileStore.Cancel()`, and `ErrorResponse`.

## Control Flow, State, and Persistence
Only async-header cancel requests are processed. The helper resolves the async context, tree, and open file, calls `Cancel()`, removes the async context on success, `STATUS_CANCELLED`, or `STATUS_NOT_SUPPORTED`, then returns an async-header error response for the target request. Missing contexts, non-async cancel requests, or failed cancels produce no response. State is the in-memory async-context table.

## Dependencies and Integration
Called by `SMBServer.SMB2.cs` for async cancel requests and for regular cancel commands after tree lookup. It assumes async contexts were created by helpers such as change notify.

## Risks and Test Signals
Risks include null-session assumptions, no response on failed cancel causing client request-expiration behavior, and treating `STATUS_NOT_SUPPORTED` as a successful cleanup path to support change notify behavior. Test async change-notify cancellation, unknown `AsyncID`, non-async cancel, backing-store cancel failures, and async context removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CancelHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ChangeNotifyHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ChangeNotifyHelper.cs

## Purpose
SMB2 change-notify handling. It starts asynchronous file-store notification monitoring, returns the interim async response, and later queues a final notify or error response when the callback fires.

## APIs, Types, and Functions
`GetChangeNotifyInterimResponse()` creates the async context and calls `IFileStore.NotifyChange()`. `OnNotifyChangeCompleted()` is the callback that removes the context and enqueues `ChangeNotifyResponse` or `ErrorResponse`.

## Control Flow, State, and Persistence
The helper resolves the session and open file, builds an `SMB2AsyncContext`, locks it to avoid final-before-interim races, and handles `STATUS_PENDING` as async. `STATUS_NOT_SUPPORTED` is deliberately converted to pending to avoid repeated Windows client retries. Completion removes the context and uses session signing state for final responses. State lives in the connection async-context collection and queued SMB responses.

## Dependencies and Integration
Called by SMB2 dispatch after tree/share validation. It depends on `IFileStore.NotifyChange()`, `SMBServer.EnqueueResponse()`, `SMB2AsyncContext`, session open-file tables, and signing metadata.

## Risks and Test Signals
Risks include null `openFile` if an invalid `FileId` reaches the helper, indefinite pending responses for stores that do not support notifications, callback races with cancel, and missing `SessionID` on error responses. Test pending notify, cancel, successful buffer delivery, cleanup/enumeration statuses, invalid file IDs, unsupported stores, and signed sessions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ChangeNotifyHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CloseHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CloseHelper.cs

## Purpose
SMB2 close handling for open file objects. It validates the `FileId`, closes the backing store handle, removes the open-file table entry, and optionally returns post-close attributes.

## APIs, Types, and Functions
`CloseHelper.GetCloseResponse()` is the entry point. It uses `SMB2Session.GetOpenFileObject()`, `IFileStore.CloseFile()`, `NTFileStoreHelper.GetNetworkOpenInformation()`, and `CloseResponse`.

## Control Flow, State, and Persistence
The helper rejects unknown file IDs with `STATUS_FILE_CLOSED`. On successful store close, it removes the file from the session and, if `PostQueryAttributes` is set, queries path-based network-open information and copies timestamps, allocation size, EOF, and attributes to the response. State is per-session open-handle metadata; no persistent state is written here.

## Dependencies and Integration
Called from SMB2 dispatch after session/tree lookup. It integrates with any `ISMBShare` whose `FileStore` implements close and network-open information helpers.

## Risks and Test Signals
Risks include querying post-close attributes by path after the handle is closed, failure to remove the open-file object when `CloseFile()` returns an error, and stale metadata if the file was renamed or deleted. Test invalid file IDs, store close failures, post-query on existing and deleted files, and session table cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CloseHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CreateHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CreateHelper.cs

## Purpose
SMB2 create/open command handling. It normalizes paths, checks share access for file-system shares, opens or creates the object in the backing store, allocates a SMB2 `FileID`, and returns create metadata.

## APIs, Types, and Functions
`CreateHelper.GetCreateResponse()` is the main entry. Private helpers build pipe and file-system `CreateResponse` instances. It uses `NTFileStoreHelper.ToCreateFileAccess()`, `IFileStore.CreateFile()`, `SMB2Session.AddOpenFile()`, and `NTFileStoreHelper.GetNetworkOpenInformation()`.

## Control Flow, State, and Persistence
The request name is forced to a leading backslash. Desired access is augmented with `FILE_READ_ATTRIBUTES` so metadata can be returned. On access denial or file-store error an SMB2 error is returned. On success, the backing handle and computed `FileAccess` are stored in the session open-file table; allocation failure closes the store handle. Named pipes get a minimal normal-file-attributes response.

## Dependencies and Integration
Called by `SMBServer.SMB2.cs` and feeds compounding support because create responses generate file IDs for related operations. It integrates with `FileSystemShare`, `NamedPipeShare`, security contexts, and `INTFileStore`.

## Risks and Test Signals
Risks include broadening desired access with read-attributes, path-normalization edge cases, no create-context handling, and assuming file info is non-null for file-system stores. Test create/open dispositions, denied reads/writes, named-pipe opens, too-many-open-files cleanup, compounded create/read/close, and returned metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CreateHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/EchoHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/EchoHelper.cs

## Purpose
Provides an unsolicited SMB2 echo response used by the server keepalive path. It sets the special all-ones message ID so clients do not match the packet to an outstanding request.

## APIs, Types, and Functions
`EchoHelper.GetUnsolicitedEchoResponse()` returns an `EchoResponse` with `Header.MessageID = 0xFFFFFFFFFFFFFFFF`.

## Control Flow, State, and Persistence
There is no mutable state. The helper only constructs a response object; queuing and transport are handled by the connection manager/server.

## Dependencies and Integration
Used by inactivity keepalive logic in the server/connection layer rather than normal request dispatch, where regular echo handling directly returns `new EchoResponse()`.

## Risks and Test Signals
Risks are limited to client compatibility: the SMB2 comment notes clients discard non-oplock-break unsolicited packets by spec, so this is a connection liveness nudge rather than a semantic echo. Test that keepalive packets serialize with the special message ID and do not disrupt outstanding SMB2 request tracking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/EchoHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/IOCtlHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/IOCtlHelper.cs

## Purpose
SMB2 IOCTL/FSCTL handling. It validates FSCTL-only support, handles special control-code preconditions, resolves file handles when needed, delegates to `IFileStore.DeviceIOControl()`, and returns output buffers.

## APIs, Types, and Functions
`IOCtlHelper.GetIOCtlResponse()` is the only entry point. It recognizes DFS referral requests, `FSCTL_PIPE_WAIT`, `FSCTL_VALIDATE_NEGOTIATE_INFO`, and `FSCTL_QUERY_NETWORK_INTERFACE_INFO`, and returns `IOCtlResponse` or `ErrorResponse`.

## Control Flow, State, and Persistence
Non-FSCTL requests fail with `STATUS_NOT_SUPPORTED`. DFS referral controls fail with `STATUS_FS_DRIVER_REQUIRED`. Certain global FSCTLs must use all-ones `FileId`; other controls require a valid session open-file object. Successful or buffer-overflow store results become `IOCtlResponse` with the same control code and output. No durable state is modified.

## Dependencies and Integration
Called by SMB2 dispatch. It relies on `SMB2Session` open-file tables and backing stores implementing `DeviceIOControl()`.

## Risks and Test Signals
Risks include limited built-in FSCTL semantics, possible mismatch around global FSCTLs and share selection, returning buffer overflow as a normal response, and no validation of input shape per control code. Test global FSCTL file IDs, invalid file IDs, DFS referral failure, store success/error/buffer-overflow, and named-pipe controls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/IOCtlHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/LockHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/LockHelper.cs

## Purpose
SMB2 byte-range lock and unlock handling. It validates SMB2 lock-array rules, applies locks or unlocks through the backing store, and rolls back previously acquired locks if a later lock in the request fails.

## APIs, Types, and Functions
`LockHelper.GetLockResponse()` is the entry point. It uses `LockRequest.Locks`, `LockElement` flags, `IFileStore.LockFile()`, `UnlockFile()`, and `LockResponse`.

## Control Flow, State, and Persistence
The helper resolves the open file, rejects empty lock arrays, determines whether the array is an unlock series from the first element, validates mixed lock/unlock and shared/exclusive flags, then processes elements in order. Multi-lock requests require `FailImmediately`. On a lock failure, earlier ranges from the same request are unlocked. State lives in the backing store's lock table.

## Dependencies and Integration
Called by SMB2 dispatch after tree lookup and session validation. It depends on `INTFileStore` lock semantics and session open-file tracking.

## Risks and Test Signals
Risks include no overflow checks when casting unsigned offsets/lengths to signed longs, rollback unlock failures being ignored, and limited async lock-wait support. Test invalid flag mixes, multi-lock rollback, unlock failures, boundary offsets, shared versus exclusive behavior, and invalid file IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/LockHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/NegotiateHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/NegotiateHelper.cs

## Purpose
SMB2 negotiate response construction for direct SMB2 negotiation and the SMB1-negotiation upgrade path. It selects the dialect, advertises signing and size limits, optionally enables Large MTU, grows receive buffers, and returns the initial SPNEGO token.

## APIs, Types, and Functions
Main APIs are `GetNegotiateResponse(List<string> smb2Dialects, ...)`, `GetNegotiateResponse(NegotiateRequest, ...)`, and `FindSMB2Dialects()` overloads for SMB1 negotiate messages. Constants define SMB2 dialect strings and normal/LargeMTU read/write/transact sizes.

## Control Flow, State, and Persistence
For SMB1 upgrade, `SMB 2.???` yields wildcard revision while `SMB 2.002` sets `SMBDialect.SMB202`. Direct SMB2 negotiation prefers SMB3.0 only when enabled, otherwise SMB2.1 then SMB2.0.2. Direct TCP plus non-2.0.2 enables Large MTU and may increase `state.ReceiveBuffer`. The response includes current time, server start time, server GUID, signing enabled, and security token. State change is the connection dialect and possible buffer size.

## Dependencies and Integration
Used by `SMBServer.cs` for SMB1-to-SMB2 upgrade and by `SMBServer.SMB2.cs` for initial SMB2 requests. It depends on `GSSProvider`, NetBIOS session packet sizing, and SMB dialect enums.

## Risks and Test Signals
Risks include limited SMB3 support despite selecting SMB3.0, no encryption/preauth capabilities, wildcard dialect handling that leaves `state.Dialect` unset, and receive-buffer growth tied only to LargeMTU. Test dialect preference, SMB1 upgrade, disabled SMB3, DirectTCP versus NetBIOS sizes, unsupported dialects, and returned SPNEGO tokens.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/NegotiateHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryDirectoryHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryDirectoryHelper.cs

## Purpose
SMB2 directory enumeration. It validates the open directory handle, enforces read access for file-system shares, starts or resumes an `OpenSearch`, pages results into the requested output buffer, and returns directory information records.

## APIs, Types, and Functions
`QueryDirectoryHelper.GetQueryDirectoryResponse()` is the entry point. It uses `SMB2Session.GetOpenFileObject()`, `GetOpenSearch()`, `AddOpenSearch()`, `IFileStore.QueryDirectory()`, and `QueryDirectoryResponse.SetFileInformationList()`.

## Control Flow, State, and Persistence
Unknown file IDs fail as closed. A new or reopened search calls the backing store and caches all matching entries in session state. `Restart` and `Reopen` reset enumeration. Empty result sets return `STATUS_NO_SUCH_FILE`; exhausted searches return `STATUS_NO_MORE_FILES`. Pagination accounts for eight-byte padded entry lengths and supports `ReturnSingleEntry`.

## Dependencies and Integration
Called by SMB2 dispatch after tree lookup. It assumes directory requests target `FileSystemShare` because it casts the share before access checks.

## Risks and Test Signals
Risks include the hard cast to `FileSystemShare`, storing full directory result lists in memory, returning an empty success if the first entry cannot fit, and rejecting file-information-class changes mid-search. Test reopen/restart/single-entry flags, tiny buffers, no matches, exhausted searches, access denial, large directories, and invalid file IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryDirectoryHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryInfoHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryInfoHelper.cs

## Purpose
SMB2 query-info handling for file, file-system, and security information. It validates handles and access, delegates to file-store query APIs, maps unsupported levels to SMB statuses, and trims or errors on oversized output.

## APIs, Types, and Functions
`QueryInfoHelper.GetQueryInfoResponse()` branches by `InfoType.File`, `FileSystem`, or `Security`. It uses `GetFileInformation()`, `GetFileSystemInformation()`, `GetSecurityInformation()`, `QueryInfoResponse` setters, and `ErrorResponse`.

## Control Flow, State, and Persistence
File and security queries require an open file object; file-system queries use the share root. File-system shares are checked for read access. File information catches `UnsupportedInformationLevelException` as `STATUS_INVALID_INFO_CLASS` and `NotImplementedException` as `STATUS_NOT_IMPLEMENTED`. File/file-system output larger than the client buffer is truncated with `STATUS_BUFFER_OVERFLOW`; security output larger than the buffer returns `STATUS_BUFFER_TOO_SMALL` with required size data.

## Dependencies and Integration
Called by SMB2 dispatch. It depends on SMB information-class parsers, security descriptor classes, `ByteReader`, `LittleEndianConverter`, and `FileSystemShare` access policy.

## Risks and Test Signals
Risks include inconsistent overflow behavior between info types, path-based access checks separate from actual handle access, and store exceptions beyond the caught types propagating. Test supported and unsupported info classes, access denial, security descriptor size errors, truncation, named-pipe query behavior, and invalid file IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryInfoHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ReadWriteResponseHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ReadWriteResponseHelper.cs

## Purpose
SMB2 read, write, and flush command handling. It validates open file IDs, enforces read/write share access for file-system shares, delegates byte I/O to the backing store, and returns SMB2 count/data responses.

## APIs, Types, and Functions
The public helpers are `GetReadResponse()`, `GetWriteResponse()`, and `GetFlushResponse()`. They use `IFileStore.ReadFile()`, `WriteFile()`, `FlushFileBuffers()`, `ReadResponse`, `WriteResponse`, and `FlushResponse`.

## Control Flow, State, and Persistence
Read and write resolve `OpenFileObject` from the session. File-system shares invoke `HasReadAccess()` or `HasWriteAccess()` using the stored path before calling the file store. Successful reads copy returned bytes into `ReadResponse.Data`; writes return the number of bytes written. Flush only validates the file ID and calls the store. Persistent effects are in the backing store for writes and flushes.

## Dependencies and Integration
Called by SMB2 dispatch. It uses session open-file state and `FileSystemShare` access events.

## Risks and Test Signals
Risks include offset/read-length casts from unsigned protocol values to `long`/`int`, no enforcement of negotiated max read/write sizes here, and write authorization based on current path metadata that may change after rename. Test invalid IDs, denied access, EOF reads, partial writes, large offsets/lengths, flush errors, and named-pipe read/write paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ReadWriteResponseHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SessionSetupHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SessionSetupHelper.cs

## Purpose
SMB2 session setup and authentication. It feeds client security tokens to the configured GSS provider, allocates session IDs, handles multi-leg authentication, creates authenticated or guest sessions, and derives SMB2 signing keys.

## APIs, Types, and Functions
`SessionSetupHelper.GetSessionSetupResponse()` is the entry point. It uses `GSSProvider.AcceptSecurityContext()`, context attributes such as user/domain/machine/session key/access token/guest flag, `SMB2Cryptography.GenerateSigningKey()`, and `SMB2ConnectionState.CreateSession()`.

## Control Flow, State, and Persistence
The helper returns an error for authentication failures. Output security tokens are included when present. If the request has no session ID it allocates one even for `STATUS_MORE_PROCESSING_REQUIRED`; if the supplied ID already maps to an established session it rejects the request. On success it truncates long GSS session keys to 16 bytes, honors client signing-required mode, and stores the session in connection state. Guest sessions disable signing and mark `SessionFlags.IsGuest`.

## Dependencies and Integration
Called before tree access by `SMBServer.SMB2.cs`. It integrates with NTLM/Kerberos-capable GSS providers and SMB2 dialect conversion.

## Risks and Test Signals
Risks include shared `state.AuthenticationContext` behavior across simultaneous session setups, null session keys for signing, no SMB3-specific signing/encryption key derivation, and rejecting reauth on existing sessions. Test multi-leg NTLM, bad credentials, guest fallback, signing required, long session keys, too-many-sessions, and duplicate session IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SessionSetupHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SetInfoHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SetInfoHelper.cs

## Purpose
SMB2 set-info handling for file metadata, file-system metadata, and security descriptors. It parses client buffers into typed information objects, enforces write access, calls backing-store setters, and updates server-side open-file paths after renames.

## APIs, Types, and Functions
`SetInfoHelper.GetSetInfoResponse()` handles all branches. It uses `FileInformation.GetFileInformation()`, `FileSystemInformation.GetFileSystemInformation()`, `SecurityDescriptor`, `IFileStore.SetFileInformation()`, `SetFileSystemInformation()`, and `SetSecurityInformation()`.

## Control Flow, State, and Persistence
File/security operations require a valid open file. File-system operations check root write access. Unsupported information levels map to invalid-info-class or not-supported statuses; parse failures map to invalid-parameter. Rename requests get an extra write-access check on the target path and update `openFile.Path` after store success. Store mutations persist in the backing file store.

## Dependencies and Integration
Called by SMB2 dispatch. It depends on SMB information parsers, security descriptor parsing, `FileSystemShare` access events, and `INTFileStore` setter implementations.

## Risks and Test Signals
Risks include broad catch blocks hiding parse specifics, path-only authorization that may not match ACL semantics, rename target normalization issues, and possible bug-prone `SetSecurityInformation(openFile, ...)` call shape depending on file-store expectations. Test invalid buffers, unsupported classes, denied target rename, successful rename path update, security descriptor set, and file-system set failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/SetInfoHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/TreeConnectHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/TreeConnectHelper.cs

## Purpose
SMB2 tree-connect and tree-disconnect handling for disk shares and `IPC$`. It resolves the requested share, checks initial access, allocates a tree ID, and returns share type, caching flags, and maximal access.

## APIs, Types, and Functions
`GetTreeConnectResponse()` and `GetTreeDisconnectResponse()` are the entry points. `GetShareCachingFlags()` maps `CachingPolicy` to SMB2 `ShareFlags`.

## Control Flow, State, and Persistence
The helper extracts the share name from the UNC path. `IPC$` maps to `NamedPipeShare` with pipe type and no caching. Disk shares are resolved from `SMBShareCollection`, cast to `FileSystemShare`, checked for read access at root, then added to the session connected-tree table. Disconnect removes the tree ID from the session. State is per-session tree mapping.

## Dependencies and Integration
Called by `SMBServer.SMB2.cs` after session setup. It integrates with share collections, named-pipe services, access events, and SMB2 response header filling in the server.

## Risks and Test Signals
Risks include broad advertised maximal access, hard `FileSystemShare` assumption for disk shares, no DFS/share capability details beyond caching, and root-only authorization. Test `IPC$`, missing shares, denied root access, all caching policies, tree ID exhaustion, disconnect, and compounded tree-connect/create behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/TreeConnectHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB1.cs

## Purpose
SMB1 request dispatch for the server. It handles negotiation, session setup, tree validation, command routing, SMB1 AndX batching, response header preparation, and send-queue enqueueing.

## APIs, Types, and Functions
Key methods are `ProcessSMB1Message()`, the two `ProcessSMB1Command()` overloads, `EnqueueMessage()`, and `PrepareResponseHeader()`. It dispatches to helpers for negotiate, session setup, tree connect, file store operations, transactions, NT create, locking, read/write, cancel, and close.

## Control Flow, State, and Persistence
Before negotiation, only `NegotiateRequest` is accepted; supported NT LM 0.12 negotiation transitions the base connection to `SMB1ConnectionState` and registers it with `ConnectionManager`. After negotiation, duplicate negotiate is rejected. Most commands require a valid UID, and file/tree commands require a valid TID. Responses are batched into AndX chains when possible. State changes include session creation/removal, tree mappings, open files, searches, transaction state, and queued packets.

## Dependencies and Integration
Called from `SMBServer.ProcessPacket()` after SMB1 parsing. It depends on SMB1 command classes, protocol helper classes, `GSSProvider`, `SMBShareCollection`, `NamedPipeShare`, and NetBIOS session packet serialization.

## Risks and Test Signals
Risks include a long type-check dispatch chain, shared response header mutation across batched commands, incomplete SMB1 command coverage, and security/session cleanup correctness on logoff. Test negotiate-only enforcement, extended and non-extended session setup, invalid UID/TID, AndX batching, every routed command family, no-response NT cancel, and logoff context deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB1.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB2.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB2.cs

## Purpose
SMB2 request-chain dispatch and response-chain construction. It enforces negotiate/session/tree sequencing, supports compounded related operations with file ID propagation, routes commands to SMB2 helpers, signs responses when needed, and queues serialized SMB2 packets.

## APIs, Types, and Functions
Main methods are `ProcessSMB2RequestChain()`, two `ProcessSMB2Command()` overloads, `EnqueueResponse()`, `EnqueueResponseChain()`, `ToSMB2Dialect()`, `UpdateSMB2Header()`, and file-ID helper methods for request/response objects.

## Control Flow, State, and Persistence
Initial SMB2 requests must be negotiate; successful negotiate converts the base connection into `SMB2ConnectionState`. Later duplicate negotiate closes the socket. Session setup and echo are handled before session lookup; other commands require a valid session and, unless async cancel, a valid tree. Related compounded requests reuse generated file IDs from prior create/IOCTL responses and propagate failures. Response headers inherit message IDs, credits, session/tree IDs, and signing flags. State changes include sessions, trees, open files, async contexts, and send queue entries.

## Dependencies and Integration
Called by `SMBServer.cs` after SMB2 chain parsing. It integrates all SMB2 helper files, `ConnectionManager`, `SMB2Cryptography`, `NetBios.SessionMessagePacket`, and session signing keys.

## Risks and Test Signals
Risks include type-check dispatch maintenance, limited dialect mapping, compounding edge cases around failed or missing file IDs, signing-key selection from the first response session, and no explicit credit accounting beyond echoing request credits. Test negotiation enforcement, compounded create/read/close, unrelated compounding, async cancel, invalid tree/session, signed requests, and unsupported command errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.SMB2.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.cs

## Purpose
Core SMB server transport and connection lifecycle. It listens on NetBIOS-over-TCP or Direct TCP, accepts sockets, receives NetBIOS session packets, detects SMB1 versus SMB2 payloads, dispatches protocol handlers, sends queued responses, manages keepalive/inactivity behavior, and exposes session information.

## APIs, Types, and Functions
Public API includes constructor, `Start()` overloads, `Stop()`, `GetSessionsInformation()`, `TerminateConnection()`, and events `ConnectionRequested` and `LogEntryAdded`. Internal callbacks include `ConnectRequestCallback()`, `ReceiveCallback()`, `ProcessConnectionBuffer()`, `ProcessPacket()`, `ProcessSendQueue()`, and `Log()`.

## Control Flow, State, and Persistence
`Start()` binds/listens, records enabled dialects, and optionally starts an inactivity keepalive thread. Accept creates `ConnectionState`, applies TCP keepalive and no-delay, lets subscribers reject clients, starts a send thread, and begins async receive. Receive buffers are locked while packets are dequeued and dispatched. SMB1 negotiate can upgrade to SMB2 when SMB2 dialect strings are present. `Stop()` stops listening, cancels keepalive, releases sockets, and releases all connections. State is in fields for shares, security provider, named-pipe services, server GUID, connection manager, listener socket, dialect flags, and start time.

## Dependencies and Integration
This partial class is extended by SMB1/SMB2 dispatch files. It depends on sockets, NetBIOS packet classes, connection state classes, `SMBShareCollection`, `NamedPipeShare`, `GSSProvider`, `SocketUtils`, and logging.

## Risks and Test Signals
Risks include async callback races during shutdown, connection-state replacement while receive callback continues, per-connection send threads, listener accept errors that may stop accepting for non-reset errors, and large packet handling tied to negotiate paths. Test start/stop idempotence, connection rejection, SMB1-disabled upgrade behavior, DirectTCP and NetBIOS packets, invalid packets closing sockets, keepalive thread cancellation, and concurrent clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMBServer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/AccessRequestArgs.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/AccessRequestArgs.cs

## Purpose
Event argument object for share-level access decisions. It carries user, path, requested access, machine, and client endpoint details to `FileSystemShare.AccessRequested` subscribers.

## APIs, Types, and Functions
`AccessRequestArgs` derives from `EventArgs` and exposes public fields `UserName`, `Path`, `RequestedAccess`, `MachineName`, `ClientEndPoint`, and mutable `Allow` defaulting to true. The constructor initializes all request context fields.

## Control Flow, State, and Persistence
There is no control flow beyond construction. The mutable `Allow` field is the event response channel; subscribers set it to deny access. No persistence is used.

## Dependencies and Integration
Created by `FileSystemShare.HasAccess()` and consumed by applications such as `SMBServer.ServerUI.InitializeShare()`.

## Risks and Test Signals
Risks include public mutable fields, default-allow behavior when handlers do not set `Allow`, and coarse `FileAccess` categories. Test event subscribers for read/write/read-write requests, null or wildcard account policies, and propagation of machine/end-point values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/AccessRequestArgs.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/Enums/CachingPolicy.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/Enums/CachingPolicy.cs

## Purpose
Defines share client-side caching policy values used when advertising SMB1 optional support flags and SMB2 share flags.

## APIs, Types, and Functions
`CachingPolicy` enum values are `ManualCaching`, `AutoCaching`, `VideoCaching`, and `NoCaching`.

## Control Flow, State, and Persistence
No runtime flow or state. Values are stored in `FileSystemShare` and translated by SMB1/SMB2 tree-connect helpers.

## Dependencies and Integration
Integrated with `FileSystemShare.CachingPolicy`, `SMB1.TreeConnectHelper.GetCachingSupportFlags()`, and `SMB2.TreeConnectHelper.GetShareCachingFlags()`.

## Risks and Test Signals
Risk is semantic mismatch between enum names and protocol flag mappings, especially offline-file reintegration behavior. Test tree-connect responses for each policy in SMB1 and SMB2 and default behavior for unknown values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/Enums/CachingPolicy.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/FileSystemShare.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/FileSystemShare.cs

## Purpose
Concrete disk-share implementation that binds a share name, an `INTFileStore`, and a caching policy, with event-driven authorization hooks.

## APIs, Types, and Functions
Constructors accept share name, file store, and optional `CachingPolicy`. Public methods `HasReadAccess()`, `HasWriteAccess()`, and `HasAccess()` raise `AccessRequested`. Properties expose `Name`, `FileStore`, and `CachingPolicy`.

## Control Flow, State, and Persistence
`HasAccess()` captures the event delegate, creates `AccessRequestArgs`, invokes subscribers, and returns `args.Allow`; without subscribers it returns true. The object stores the backing file store reference and policy but does not persist configuration.

## Dependencies and Integration
Used by tree-connect helpers, SMB2 file helpers, `SMBShareCollection`, and the sample UI. The backing store performs actual file operations and persistence.

## Risks and Test Signals
Risks include default-allow security, authorization decoupled from actual NTFS ACLs unless the backing store enforces them, public event handler ordering, and share-name immutability only by convention. Test no-handler access, denial handlers, read/write/read-write distinction, and use with different `INTFileStore` implementations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/FileSystemShare.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/ISMBShare.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/ISMBShare.cs

## Purpose
Minimal common interface for SMB shares, allowing disk shares and named-pipe shares to be used by protocol handlers through a shared name and file-store contract.

## APIs, Types, and Functions
`ISMBShare` declares read-only `Name` and `INTFileStore FileStore` properties.

## Control Flow, State, and Persistence
The interface has no implementation state. Implementations decide whether the file store maps to a file system or named-pipe service store.

## Dependencies and Integration
Implemented by `FileSystemShare` and `NamedPipeShare`; consumed throughout SMB1/SMB2 helpers after tree lookup.

## Risks and Test Signals
Risks are mainly type narrowing: many helpers cast to `FileSystemShare`, so the abstraction is only partial. Test custom share implementations against helpers that do and do not require disk-specific access behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/ISMBShare.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/NamedPipeShare.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/NamedPipeShare.cs

## Purpose
Represents the SMB `IPC$` share and exposes named-pipe-backed RPC services through an `INTFileStore`.

## APIs, Types, and Functions
`NamedPipeShare.NamedPipeShareName` is `IPC$`. The constructor builds a `NamedPipeStore` from `ServerService` and `WorkstationService`. Properties expose `Name` and `FileStore`.

## Control Flow, State, and Persistence
Construction snapshots the supplied share-name list for `ServerService` enumeration and uses machine name for server/workstation service identity. Runtime file operations are delegated to `NamedPipeStore`; there is no durable persistence.

## Dependencies and Integration
Used automatically by `SMBServer` constructor and tree-connect helpers when clients connect to `IPC$`. It integrates with RPC service classes and named-pipe file-store support.

## Risks and Test Signals
Risks include share list staleness after server construction, limited service coverage, and machine-name based identity that may not match configured NetBIOS names. Test `IPC$` tree connect, opening `srvsvc` and `wkssvc`, share enumeration matching configured shares, and unsupported pipe/service behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/NamedPipeShare.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/SMBShareCollection.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/SMBShareCollection.cs

## Purpose
Typed list of `FileSystemShare` objects with case-aware lookup helpers and share-name listing.

## APIs, Types, and Functions
Extends `List<FileSystemShare>`. Methods are `Contains(string, StringComparison)`, `IndexOf(string, StringComparison)`, `ListShares()`, and `GetShareFromName()`.

## Control Flow, State, and Persistence
Lookups linearly scan the list by `FileSystemShare.Name`. `GetShareFromName()` uses ordinal-ignore-case comparison and returns null when absent. State is the inherited in-memory list.

## Dependencies and Integration
Consumed by `SMBServer`, tree-connect helpers, and `NamedPipeShare` construction.

## Risks and Test Signals
Risks include duplicate share names, mutable list operations from callers without synchronization, and linear lookup cost. Test case-insensitive lookup, duplicate behavior, empty lists, and share-list snapshots used by RPC services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Shares/SMBShareCollection.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Enums/PlatformName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Enums/PlatformName.cs

## Purpose
Defines platform identifiers used by server and workstation RPC information structures.

## APIs, Types, and Functions
`PlatformName : uint` includes DOS, OS2, NT, OSF, and VMS numeric values matching MS-SRVS platform IDs.

## Control Flow, State, and Persistence
No runtime control flow or state. Values are serialized into NDR structures such as `ServerInfo100` and `ServerInfo101`.

## Dependencies and Integration
Used by `ServerService` and workstation/server info structures to advertise NT-compatible platform identity.

## Risks and Test Signals
Risk is limited to protocol value drift. Test NDR serialization of server/workstation info responses and client display of platform values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Enums/PlatformName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/InvalidLevelException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/InvalidLevelException.cs

## Purpose
Exception used by RPC/NDR union parsers to signal an invalid information level rather than a merely unsupported valid level.

## APIs, Types, and Functions
`InvalidLevelException : Exception` stores a private `uint m_level`, initializes it in the constructor, and exposes it via `Level`.

## Control Flow, State, and Persistence
The exception is thrown during parsing of union discriminants and caught by service handlers such as share enumeration to return `ERROR_INVALID_LEVEL`. State is only the level value.

## Dependencies and Integration
Used by server-service share/server info structures and service response construction.

## Risks and Test Signals
Risks include no message/base constructor and inconsistent namespace usage with related exceptions. Test invalid-level requests produce the intended Win32 result and preserve the requested level in the response union.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/InvalidLevelException.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedLevelException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedLevelException.cs

## Purpose
Exception used when an RPC information level is recognized by the protocol but not implemented by this server.

## APIs, Types, and Functions
`UnsupportedLevelException : Exception` stores and exposes a `uint Level` through a constructor and read-only property.

## Control Flow, State, and Persistence
Thrown by NDR structures such as `ShareEnum` for known-but-unsupported levels and caught by `ServerService` to produce `ERROR_NOT_SUPPORTED`. No persistence.

## Dependencies and Integration
Integrated with server-service request parsing and response union construction.

## Risks and Test Signals
Risks mirror invalid-level handling: no message, limited stack context, and callers must catch it distinctly. Test levels 2/501/502/503 in share enumeration and confirm `ERROR_NOT_SUPPORTED` rather than invalid-level.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedLevelException.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedOpNumException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedOpNumException.cs

## Purpose
Exception used by RPC service implementations to indicate an unsupported operation number.

## APIs, Types, and Functions
`UnsupportedOpNumException : Exception` has a default constructor and no additional fields.

## Control Flow, State, and Persistence
Thrown by `RemoteService.GetResponseBytes()` implementations for unknown opnums and caught by `RemoteServiceHelper.GetRPCResponse()` to emit an RPC fault with `OpRangeError`.

## Dependencies and Integration
Used by `ServerService`, `WorkstationService`, and RPC response framing. It is declared in namespace `SMBLibrary`, which is imported by services.

## Risks and Test Signals
Risks include lack of opnum detail and namespace inconsistency with other service exceptions. Test unsupported srvsvc/wkssvc opnums produce fault PDUs with `DidNotExecute` and op-range status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/Exceptions/UnsupportedOpNumException.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RPCPipeStream.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/RPCPipeStream.cs

## Purpose
Stream implementation for message-mode named pipes carrying DCE/RPC traffic to a single `RemoteService`. It parses incoming RPC PDUs, generates bind or request responses, and queues response messages for pipe reads.

## APIs, Types, and Functions
`RPCPipeStream : Stream` overrides `Read()`, `Write()`, `Flush()`, `Close()`, `Seek()`, `SetLength()`, and stream capability properties. `ProcessRPCRequest()` handles bind, request, and protocol-error cases. `MessageLength` exposes the first queued message length.

## Control Flow, State, and Persistence
`Write()` treats each write as one pipe message and parses one `RPCPDU`. Bind requests produce a `BindAckPDU` and set `m_maxTransmitFragmentSize`. Later request PDUs are dispatched through `RemoteServiceHelper.GetRPCResponse()` and may append multiple fragmented responses. Reads drain the first queued `MemoryStream` and remove it at EOF. State is per-stream service reference, output queue, and negotiated transmit fragment size.

## Dependencies and Integration
Used by named-pipe file-store plumbing for services such as `srvsvc` and `wkssvc`. Depends on RPC PDU classes and `RemoteServiceHelper`.

## Risks and Test Signals
Risks include no handling for fragmented incoming request PDUs, no synchronization on the output queue, empty `Close()`, and protocol-error behavior when a request arrives before bind. Test bind negotiation, request after bind, unsupported op fault, fragmented response reads, read-empty returning 0, and invalid PDU ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RPCPipeStream.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteService.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteService.cs

## Purpose
Abstract base contract for RPC services exposed over SMB named pipes.

## APIs, Types, and Functions
Subclasses implement `GetResponseBytes(ushort opNum, byte[] requestBytes)`, `Guid InterfaceGuid`, and `string PipeName`.

## Control Flow, State, and Persistence
The base class has no state. Service-specific subclasses parse request bytes, dispatch opnums, and serialize response bytes.

## Dependencies and Integration
Consumed by `NamedPipeShare`, `NamedPipeStore`, `RPCPipeStream`, and `RemoteServiceHelper`.

## Risks and Test Signals
Risks include raw byte APIs that push parsing validation into each service and no explicit service version property despite constants in subclasses. Test service binding by interface GUID and request dispatch through concrete services.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteService.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteServiceHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteServiceHelper.cs

## Purpose
DCE/RPC helper for bind negotiation and response PDU fragmentation around `RemoteService` implementations.

## APIs, Types, and Functions
Public members include NDR transfer syntax constants, bind-time feature constants, `GetRPCBindResponse()`, and `GetRPCResponse()`. Private `IndexOfSupportedTransferSyntax()` selects NDR v1/v2 transfer syntax.

## Control Flow, State, and Persistence
Bind responses allocate or echo association group IDs, set the secondary pipe address, swap max transmit/receive fragment sizes, and build one result per context element. Matching service interface plus supported syntax is accepted; bind-time feature syntax can receive negotiate-ack; otherwise provider rejection is returned. Request responses call the service, convert unsupported opnums into fault PDUs, and split response bytes across `ResponsePDU`s based on negotiated max fragment size. Static association group ID is process state.

## Dependencies and Integration
Used by `RPCPipeStream` for all named-pipe RPC traffic. Depends on RPC PDU, syntax, NDR, byte-reader, and fault status types.

## Risks and Test Signals
Risks include non-thread-safe static association ID increments, no guard for too-small max fragment sizes, only NDR transfer syntaxes, and unsupported-op faults only for one exception type. Test bind with accepted/rejected contexts, feature negotiation, association ID rollover, fragmented large responses, and unsupported opnum faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/RemoteServiceHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/EnumStructures/ShareTypeExtended.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/EnumStructures/ShareTypeExtended.cs

## Purpose
Represents MS-SRVS share type values plus special and temporary high-bit flags for share information structures.

## APIs, Types, and Functions
Defines `ShareType : uint` values such as disk, print, device, IPC, and cluster variants. `ShareTypeExtended` stores `ShareType`, `IsSpecial`, and `IsTemporary`, with constructors from enum, flags, `NDRParser`, or raw `uint`, plus `Write()` and `ToUInt32()`.

## Control Flow, State, and Persistence
Raw values mask low 28 bits into `ShareType` and read high bits `0x80000000` and `0x40000000`. Writing recomposes the flags into a uint. No persistent state beyond struct fields.

## Dependencies and Integration
Used by `ShareInfo1Entry`, `ShareInfo2Entry`, and server service responses.

## Risks and Test Signals
Risks include silently accepting unknown low-bit share types and not preserving unrecognized high bits. Test round-trip serialization for disk, IPC, special, temporary, and cluster values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/EnumStructures/ShareTypeExtended.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/Permissions.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/Permissions.cs

## Purpose
Flags enum for legacy share permissions in server-service share info level 2.

## APIs, Types, and Functions
`Permissions : uint` defines read, write, create, execute, delete, attribute, and permission bits.

## Control Flow, State, and Persistence
No logic. `ShareInfo2Entry` serializes/deserializes the enum as a uint, and the sample responses leave it at zero.

## Dependencies and Integration
Integrated with `ShareInfo2Entry` and MS-SRVS-compatible NDR serialization.

## Risks and Test Signals
Risk is low, but current service responses do not derive permissions from actual share access policy. Test level-2 share info serialization and client handling of zero permissions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/Permissions.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerServiceOpName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerServiceOpName.cs

## Purpose
Enumerates MS-SRVS RPC operation numbers for the server service interface.

## APIs, Types, and Functions
`ServerServiceOpName : ushort` maps opnums such as `NetrShareEnum = 15`, `NetrShareGetInfo = 16`, and `NetrServerGetInfo = 21`, plus many unsupported operations.

## Control Flow, State, and Persistence
No logic. `ServerService.GetResponseBytes()` casts incoming opnums to this enum and switches on implemented values.

## Dependencies and Integration
Used by `ServerService` dispatch and RPC fault handling for unsupported operations.

## Risks and Test Signals
Risks include typos in rarely used names and false sense of support for enum members not implemented. Test implemented opnums return responses and unsupported enum values return RPC op-range faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerServiceOpName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerType.cs

## Purpose
Flags enum for MS-SRVS server software type values advertised in server information responses.

## APIs, Types, and Functions
`ServerType : uint` includes workstation, server, domain roles, browser roles, NT/windows flags, terminal/cluster flags, local-list-only, primary-domain, and `All`.

## Control Flow, State, and Persistence
No logic. `ServerService` combines selected flags for level-101 server info.

## Dependencies and Integration
Used by `ServerInfo101` and `ServerService`.

## Risks and Test Signals
Risks include duplicate/ambiguous cluster comments and service identity that may not reflect deployment role. Test level-101 serialization and client interpretation of advertised type flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Enums/ServerType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoRequest.cs

## Purpose
NDR model for the MS-SRVS `NetrServerGetInfo` request.

## APIs, Types, and Functions
Fields are `ServerName` and `Level`. Constructors support empty creation and parsing from a byte buffer. `GetBytes()` serializes the top-level Unicode string pointer and level.

## Control Flow, State, and Persistence
Parsing constructs an `NDRParser`, reads the server-name pointer, then the info level. Serialization mirrors that order with `NDRWriter`. No persistence.

## Dependencies and Integration
Used by `ServerService.GetResponseBytes()` for opnum 21.

## Risks and Test Signals
Risks include no validation of server name or trailing bytes. Test parse/serialize round trips for null and non-null server names and supported/unsupported levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoResponse.cs

## Purpose
NDR model for `NetrServerGetInfo` responses, carrying a server-info union and Win32 result code.

## APIs, Types, and Functions
Fields are `ServerInfo InfoStruct` and `Win32Error Result`. Constructors parse from bytes or create empty responses. `GetBytes()` writes the structure and result.

## Control Flow, State, and Persistence
Parsing reads `ServerInfo` then the trailing result code. Writing serializes `InfoStruct` then result. No persistence.

## Dependencies and Integration
Produced by `ServerService.GetNetrWkstaGetInfoResponse()` despite the method name typo.

## Risks and Test Signals
Risks include null `InfoStruct` causing serialization failure and invalid-level parser exceptions if response bytes contain unsupported unions. Test level 100/101 success and unsupported/invalid levels carrying empty union pointers with correct Win32 codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrServerGetInfoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumRequest.cs

## Purpose
NDR model for MS-SRVS `NetrShareEnum` requests.

## APIs, Types, and Functions
Fields are `ServerName`, `ShareEnum InfoStruct`, `PreferedMaximumLength`, and `ResumeHandle`. Constructors parse from bytes or create empty instances; `GetBytes()` serializes all fields.

## Control Flow, State, and Persistence
Parsing reads a top-level server-name pointer, embedded `ShareEnum`, preferred maximum length, and resume handle. The service currently ignores preferred length and resume handle when responding.

## Dependencies and Integration
Used by `ServerService.GetNetrShareEnumResponse()`.

## Risks and Test Signals
Risks include misspelled field name, no resume support, and exceptions for unsupported levels during `ShareEnum` parse. Test level 0/1 requests, unsupported levels, invalid levels, nonzero resume handle, and max-preferred-length behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumResponse.cs

## Purpose
NDR model for MS-SRVS `NetrShareEnum` responses.

## APIs, Types, and Functions
Fields are `ShareEnum InfoStruct`, `TotalEntries`, `ResumeHandle`, and `Win32Error Result`. It can parse from bytes and serialize through `GetBytes()`.

## Control Flow, State, and Persistence
Read/write order is share enum structure, total entries, resume handle, result code. No persistent state.

## Dependencies and Integration
Created by `ServerService` share enumeration logic.

## Risks and Test Signals
Risks include null `InfoStruct`, resume handle not used for paging, and total entries always full share count. Test empty share list, level 0/1 arrays, unsupported/invalid-level responses, and client unmarshalling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareEnumResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoRequest.cs

## Purpose
NDR request model for MS-SRVS `NetrShareGetInfo`.

## APIs, Types, and Functions
Fields are `ServerName`, `NetName`, and `Level`. The byte constructor parses those fields; `GetBytes()` serializes them.

## Control Flow, State, and Persistence
Parsing reads a top-level Unicode server-name pointer, an inline Unicode share name, and the requested info level. No validation or persistence.

## Dependencies and Integration
Used by `ServerService.GetResponseBytes()` for opnum 16 and by `GetNetrShareGetInfoResponse()`.

## Risks and Test Signals
Risks include no null/empty share-name validation and no default constructor despite response classes having one. Test case-insensitive share lookup, missing shares, and level 0/1/2/unsupported/invalid requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoResponse.cs

## Purpose
NDR response model for MS-SRVS `NetrShareGetInfo`.

## APIs, Types, and Functions
Fields are `ShareInfo InfoStruct` and `Win32Error Result`. The class supports empty construction, parsing, and `GetBytes()` serialization.

## Control Flow, State, and Persistence
Parsing reads the share-info union followed by the result code. Writing emits the union then result. No persistence.

## Dependencies and Integration
Produced by `ServerService.GetNetrShareGetInfoResponse()`.

## Risks and Test Signals
Risks include null info structs and a `ShareInfo` parser that recognizes levels 100/101 even though service writes 0/1/2, making round-trip parsing suspect. Test serialized responses with Windows clients for each supported level.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/NetrShareGetInfoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/ServerService.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/ServerService.cs

## Purpose
Implementation of the `srvsvc` named-pipe RPC service subset. It supports share enumeration, share get-info, and server get-info responses for SMB clients browsing shares through `IPC$`.

## APIs, Types, and Functions
`ServerService : RemoteService` exposes constants for pipe name, interface GUID, version, and max preferred length. It implements `GetResponseBytes()`, `GetNetrShareEnumResponse()`, `GetNetrShareGetInfoResponse()`, `GetNetrWkstaGetInfoResponse()` for server info, `IndexOfShare()`, `InterfaceGuid`, and `PipeName`.

## Control Flow, State, and Persistence
Constructor stores platform/server/version/type values and an in-memory share list. Dispatch switches on `ServerServiceOpName`, parses request bytes, and serializes responses. Share enum supports levels 0 and 1, rejects levels 2/501/502/503 as not supported, and invalid levels as invalid. Share get-info supports levels 0, 1, and 2. Server get-info supports 100 and 101. State is fixed after construction.

## Dependencies and Integration
Instantiated by `NamedPipeShare`; called through RPC pipe framing. Depends on NDR request/response structures, share/server info structures, `Win32Error`, and `UnsupportedOpNumException`.

## Risks and Test Signals
Risks include stale share list, no paging/resume support, limited levels, method naming typo, level/union inconsistencies in `ShareInfo.Read()`, and hard-coded Windows version/type identity. Test Windows share browsing, `net view`, level 0/1/2 get-info, unsupported opnums, invalid levels, and empty share lists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/ServerService.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo.cs

## Purpose
NDR union wrapper for MS-SRVS `SERVER_INFO` levels.

## APIs, Types, and Functions
Fields are `uint Level` and `ServerInfoLevel Info`. Constructors support empty, level-only, concrete info, and parser forms. `Read()` handles levels 100 and 101; `Write()` emits the discriminant and embedded full pointer.

## Control Flow, State, and Persistence
`Read()` begins the union, reads the level, dispatches to `ServerInfo100` or `ServerInfo101`, and throws `InvalidLevelException` otherwise. `Write()` writes whatever `Info` pointer is present. No persistence.

## Dependencies and Integration
Used by server get-info responses and parsing. Depends on `NDRParser`, `NDRWriter`, and concrete server info structures.

## Risks and Test Signals
Risks include no level-vs-info validation in `Write()` and level-only unsupported responses writing null info pointers. Test level 100/101 round trips, invalid-level exceptions, and null-info response serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo100.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo100.cs

## Purpose
NDR structure for MS-SRVS `SERVER_INFO_100`, carrying platform ID and server name.

## APIs, Types, and Functions
Fields are `PlatformName PlatformID` and `NDRUnicodeString ServerName`. It implements `Read()`, `Write()`, and `Level => 100`.

## Control Flow, State, and Persistence
Constructor initializes `ServerName`. Read/write wrap structure boundaries and use embedded full pointers for the string. No persistence.

## Dependencies and Integration
Used by `ServerService` level-100 server info responses and by `ServerInfo`.

## Risks and Test Signals
Risks include null `ServerName` if parser or caller does not initialize it and platform values not matching host reality. Test NDR round trips and Windows client display of level-100 info.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo100.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo101.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo101.cs

## Purpose
NDR structure for MS-SRVS `SERVER_INFO_101`, adding version, server type flags, and comment to level-100 data.

## APIs, Types, and Functions
Fields are `PlatformID`, `ServerName`, `VerMajor`, `VerMinor`, `ServerType Type`, and `NDRUnicodeString Comment`. It implements `Read()`, `Write()`, and `Level => 101`.

## Control Flow, State, and Persistence
Read/write use NDR structure boundaries and embedded full pointers for strings. Constructor initializes `ServerName` and `Comment`. No persistence.

## Dependencies and Integration
Used by `ServerService` level-101 server info responses.

## Risks and Test Signals
Risks include hard-coded version/type data from service construction and null string fields if not initialized. Test level-101 response unmarshalling, type-flag combinations, and empty comments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfo101.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfoLevel.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfoLevel.cs

## Purpose
Abstract base for concrete server-info NDR structures.

## APIs, Types, and Functions
Declares abstract `Read(NDRParser)`, `Write(NDRWriter)`, and `uint Level`.

## Control Flow, State, and Persistence
No implementation state. Concrete subclasses implement NDR serialization for specific levels.

## Dependencies and Integration
Used by `ServerInfo` union and `ServerInfo100/101`.

## Risks and Test Signals
Risk is low; level consistency is enforced by caller conventions rather than this base. Test each concrete subclass through `ServerInfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ServerInfo/ServerInfoLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoContainer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoContainer.cs

## Purpose
Interface for NDR share enumeration containers.

## APIs, Types, and Functions
Extends `INDRStructure` and requires a `uint Level` property.

## Control Flow, State, and Persistence
No logic or state. Implemented by level-specific container classes.

## Dependencies and Integration
Used by `ShareEnum` to store level-specific arrays.

## Risks and Test Signals
Risk is low; level mismatch validation occurs in `ShareEnum.Write()`. Test containers through share enum responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoContainer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoEntry.cs

## Purpose
Interface for level-specific share information entries.

## APIs, Types, and Functions
Extends `INDRStructure` and requires `uint Level`.

## Control Flow, State, and Persistence
No implementation logic or state.

## Dependencies and Integration
Used by `ShareInfo` and concrete entries for levels 0, 1, and 2.

## Risks and Test Signals
Risk is low; callers must ensure the union level matches the concrete entry. Test concrete entry serialization through `ShareInfo`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/IShareInfoEntry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareEnum.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareEnum.cs

## Purpose
NDR model for `SHARE_ENUM_STRUCT` and its embedded share-enum union.

## APIs, Types, and Functions
Fields are `uint Level` and `IShareInfoContainer Info`. Constructors support empty, level-only, concrete container, and parser forms. `Read()` and `Write()` handle NDR structure/union serialization.

## Control Flow, State, and Persistence
Read parses the outer level, the duplicated union discriminant, and level 0 or 1 container pointers. Levels 2/501/502/503 throw `UnsupportedLevelException`; other levels throw `InvalidLevelException`. Write validates `Level == Info.Level` when info exists and writes the pointer. No persistence.

## Dependencies and Integration
Used by share enum requests/responses in `ServerService`.

## Risks and Test Signals
Risks include null `Info` with unsupported responses, no read support for level 2 despite service get-info support, and dependence on exact NDR union discriminant behavior. Test level 0/1 parsing and writing, unsupported level handling, invalid levels, and null-info writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareEnum.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo.cs

## Purpose
NDR union wrapper for single-share information responses.

## APIs, Types, and Functions
Fields are `uint Level` and `IShareInfoEntry Info`. Constructors support empty, level-only, concrete entry, and parser forms. `Read()` and `Write()` serialize the union.

## Control Flow, State, and Persistence
`Read()` currently recognizes levels 100 and 101 and maps them to `ShareInfo0Entry` and `ShareInfo1Entry`; other levels throw `InvalidLevelException`. `Write()` writes the level and embedded entry pointer. No persistence.

## Dependencies and Integration
Used by `NetrShareGetInfoResponse` and `ServerService`.

## Risks and Test Signals
Important risk: the parser appears inconsistent with service levels 0/1/2 and MS-SRVS share info levels, so round-trip parsing of this library's own level-0/1/2 responses may fail. Test Windows client unmarshalling and local parse/serialize for all supported service levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Container.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Container.cs

## Purpose
NDR container for arrays of level-0 share entries in share enumeration responses.

## APIs, Types, and Functions
Field `NDRConformantArray<ShareInfo0Entry> Entries`; methods `Read()`, `Write()`, `Add()`, `Count`, and `Level => 0`.

## Control Flow, State, and Persistence
Read consumes a count and embedded full pointer to the conformant array. Write emits current `Count` and the array pointer. `Add()` lazily creates the array. State is the in-memory entries array.

## Dependencies and Integration
Used by `ServerService.GetNetrShareEnumResponse()` for level 0.

## Risks and Test Signals
Risks include ignoring the parsed count variable and potential null pointer/count mismatch. Test empty and multi-share arrays, NDR round trips, and client enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Container.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Entry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Entry.cs

## Purpose
NDR entry for MS-SRVS `SHARE_INFO_0`, containing only the share name.

## APIs, Types, and Functions
Field `NDRUnicodeString NetName`; constructors for empty, share-name, and parser; methods `Read()`, `Write()`, and `Level => 0`.

## Control Flow, State, and Persistence
Read/write wrap a structure and use an embedded full pointer for `NetName`. No persistence.

## Dependencies and Integration
Used by level-0 share enum/get-info responses.

## Risks and Test Signals
Risks include null `NetName` in empty instances and pointer serialization correctness. Test share names with case, spaces, and empty/null scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo0Entry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Container.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Container.cs

## Purpose
NDR container for arrays of level-1 share entries with name, type, and remark.

## APIs, Types, and Functions
Field `NDRConformantArray<ShareInfo1Entry> Entries`; methods `Read()`, `Write()`, `Add()`, `Count`, and `Level => 1`.

## Control Flow, State, and Persistence
Read consumes count and array pointer; write emits computed count and array pointer; add lazily allocates entries. State is in-memory only.

## Dependencies and Integration
Used by server-service level-1 share enumeration.

## Risks and Test Signals
Risks include parsed count not validated against array length and null-array serialization. Test empty and populated level-1 enumerations and client display of remarks/types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Container.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Entry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Entry.cs

## Purpose
NDR entry for MS-SRVS `SHARE_INFO_1`, carrying share name, type, and remark.

## APIs, Types, and Functions
Fields are `NetName`, `ShareType`, and `Remark`. Constructors create empty, share-name/type, or parsed entries. Implements `Read()`, `Write()`, and `Level => 1`.

## Control Flow, State, and Persistence
Share-name constructor initializes an empty remark. Read/write use embedded string pointers and `ShareTypeExtended` serialization. No persistence.

## Dependencies and Integration
Used by level-1 share enum/get-info responses.

## Risks and Test Signals
Risks include empty instances with null strings and hard-coded empty remarks in service responses. Test serialization for disk and special shares, empty remarks, and Unicode share names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo1Entry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo2Entry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo2Entry.cs

## Purpose
NDR entry for MS-SRVS `SHARE_INFO_2`, extending share info with permissions, use counts, path, and password.

## APIs, Types, and Functions
Fields include `NetName`, `ShareType`, `Remark`, `Permissions`, `MaxUses`, `CurrentUses`, `Path`, and `Password`; constant `UnlimitedConnections`; constructors, `Read()`, `Write()`, and `Level => 2`.

## Control Flow, State, and Persistence
The share-name constructor sets empty remark/path, unlimited max uses, and null password. Read/write process strings as embedded full pointers and scalar fields in protocol order. No persistence.

## Dependencies and Integration
Used by `ServerService.GetNetrShareGetInfoResponse()` for level 2.

## Risks and Test Signals
Risks include service returning empty path rather than actual backing path, zero permissions, no current-use accounting, and nullable password pointer handling. Test level-2 get-info from Windows clients and local NDR serialization with null password.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/Structures/ShareInfo/ShareInfo2Entry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Enums/WorkstationServiceOpName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Enums/WorkstationServiceOpName.cs

## Purpose
Enumerates MS-WKST workstation-service RPC operation numbers.

## APIs, Types, and Functions
`WorkstationServiceOpName : ushort` maps opnums including `NetrWkstaGetInfo = 0` and many unsupported workstation, use, join, and computer-name operations.

## Control Flow, State, and Persistence
No logic. `WorkstationService.GetResponseBytes()` switches on this enum and implements only get-info.

## Dependencies and Integration
Used by `WorkstationService` dispatch and RPC unsupported-op fault handling.

## Risks and Test Signals
Risk is limited to enum members implying support that is not implemented. Test opnum 0 success and unsupported opnums producing op-range faults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Enums/WorkstationServiceOpName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoRequest.cs

## Purpose
NDR request model for MS-WKST `NetrWkstaGetInfo`.

## APIs, Types, and Functions
Fields are `ServerName` and `Level`; constructors support empty and byte parsing; `GetBytes()` serializes the top-level Unicode string pointer and level.

## Control Flow, State, and Persistence
Parsing and writing are straightforward NDR operations. No validation or persistence.

## Dependencies and Integration
Used by `WorkstationService.GetResponseBytes()` for opnum 0.

## Risks and Test Signals
Risks include no server-name validation and unchecked malformed buffers. Test parse/serialize round trips for levels 100, 101, unsupported, and invalid values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoResponse.cs

## Purpose
NDR response model for MS-WKST `NetrWkstaGetInfo`.

## APIs, Types, and Functions
Fields are `WorkstationInfo WkstaInfo` and `Win32Error Result`; constructors support empty and parsed forms; `GetBytes()` writes the info union and result.

## Control Flow, State, and Persistence
Parsing reads `WorkstationInfo` then a trailing result. Writing emits the same order. No persistence.

## Dependencies and Integration
Produced by `WorkstationService.GetNetrWkstaGetInfoResponse()`.

## Risks and Test Signals
Risks include null `WkstaInfo` serialization and parser throwing for unsupported levels. Test success levels 100/101 and unsupported/invalid responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/NetrWkstaGetInfoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo.cs

## Purpose
NDR union wrapper for MS-WKST workstation information levels.

## APIs, Types, and Functions
Fields are `uint Level` and `WorkstationInfoLevel Info`. Constructors support empty, level-only, concrete info, and parser forms. `Read()` handles levels 100 and 101; `Write()` validates level consistency when `Info` is non-null.

## Control Flow, State, and Persistence
Read dispatches by level to `WorkstationInfo100` or `WorkstationInfo101` and throws `NotImplementedException` otherwise. Write emits level and embedded pointer. No persistence.

## Dependencies and Integration
Used by `NetrWkstaGetInfoResponse` and `WorkstationService`.

## Risks and Test Signals
Risks include `NotImplementedException` instead of service-specific level exceptions and null-info unsupported responses. Test local and client unmarshalling for level-only error responses and level 100/101 successes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo100.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo100.cs

## Purpose
NDR structure for MS-WKST `WKSTA_INFO_100`, carrying platform, computer name, LAN group, and version.

## APIs, Types, and Functions
Fields are `PlatformID`, `ComputerName`, `LanGroup`, `VerMajor`, and `VerMinor`. Implements parser constructor, `Read()`, `Write()`, and `Level => 100`.

## Control Flow, State, and Persistence
Constructor initializes string fields. Read/write use embedded full pointers for strings and scalar version fields. No persistence.

## Dependencies and Integration
Used by `WorkstationService` level-100 responses.

## Risks and Test Signals
Risks include hard-coded version data and null strings in uninitialized instances. Test NDR round trips and Windows workstation info client behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo100.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo101.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo101.cs

## Purpose
NDR structure for MS-WKST `WKSTA_INFO_101`, adding LAN root to level-100 workstation information.

## APIs, Types, and Functions
Fields are `PlatformID`, `ComputerName`, `LanGroup`, `VerMajor`, `VerMinor`, and `LanRoot`. Implements `Read()`, `Write()`, and `Level => 101`.

## Control Flow, State, and Persistence
Constructor initializes all string fields. Read/write use NDR embedded full pointers. No persistence.

## Dependencies and Integration
Used by `WorkstationService` level-101 responses.

## Risks and Test Signals
Risks include `LanRoot` set to LAN group by the service, which may not match client expectations, and hard-coded version identity. Test level-101 NDR serialization and client display.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfo101.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfoLevel.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfoLevel.cs

## Purpose
Abstract base for concrete workstation-info NDR structures.

## APIs, Types, and Functions
Declares abstract `Read(NDRParser)`, `Write(NDRWriter)`, and `uint Level`.

## Control Flow, State, and Persistence
No implementation state. Concrete subclasses own their fields and serialization.

## Dependencies and Integration
Used by `WorkstationInfo`, `WorkstationInfo100`, and `WorkstationInfo101`.

## Risks and Test Signals
Risk is low; caller code must maintain level consistency. Test concrete classes through the union wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/Structures/WorkstationInfoLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/WorkstationService.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/WorkstationService.cs

## Purpose
Implementation of the `wkssvc` named-pipe RPC service subset, supporting workstation get-info responses for SMB clients querying host/workgroup metadata.

## APIs, Types, and Functions
`WorkstationService : RemoteService` exposes pipe name, interface GUID, version, constructor, `GetResponseBytes()`, `GetNetrWkstaGetInfoResponse()`, and overrides for `InterfaceGuid` and `PipeName`.

## Control Flow, State, and Persistence
Constructor stores platform ID, computer name, LAN group, and hard-coded major/minor version. Dispatch implements only `NetrWkstaGetInfo`; other opnums throw `UnsupportedOpNumException`. Level 100 and 101 return populated info structures; levels 102 and 502 return not-supported; others return invalid-level. State is fixed per service instance.

## Dependencies and Integration
Created by `NamedPipeShare` and invoked through `RPCPipeStream`. Uses workstation request/response and info structures, `Win32Error`, and `PlatformName`.

## Risks and Test Signals
Risks include limited opnum and level support, hard-coded version values, `LanRoot` value choice, and no dynamic domain/workgroup discovery. Test `wkssvc` bind, level 100/101 get-info, unsupported levels, invalid levels, and unsupported opnums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/WorkstationService/WorkstationService.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/LogEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Utilities/LogEntry.cs

## Purpose
Shared logging event payload and severity enumeration used by the SMB server and sample application.

## APIs, Types, and Functions
`Severity` enum ranges from `Critical` to `Trace`. `LogEntry : EventArgs` exposes public fields `Time`, `Severity`, `Source`, and `Message`, initialized by constructor.

## Control Flow, State, and Persistence
No logic beyond construction. Persistence occurs only when subscribers such as `LogWriter` write entries.

## Dependencies and Integration
Used by `SMBServer.LogEntryAdded`, connection logging, and `SMBServer/LogWriter.cs`.

## Risks and Test Signals
Risks include public mutable fields and no structured event IDs. Test event delivery, severity filtering, and timestamp/source propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/LogEntry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/SocketUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Utilities/SocketUtils.cs

## Purpose
Socket utility helpers for TCP keepalive configuration and forceful socket release across .NET Framework and newer runtimes.

## APIs, Types, and Functions
`SetKeepAlive(Socket, TimeSpan)` delegates to `SetKeepAlive(Socket, bool, TimeSpan, TimeSpan)`. `ReleaseSocket(Socket)` shuts down, disconnects, and closes sockets. Conditional `IsDotNetFramework()` selects runtime-specific keepalive APIs.

## Control Flow, State, and Persistence
Keepalive always enables socket keepalive. On .NET Framework it builds a 12-byte `tcp_keepalive` buffer and calls `IOControl(KeepAliveValues)`. On newer runtimes it sets TCP keepalive time, interval, and non-Windows retry count socket options. Release ignores common socket/object-disposed exceptions and closes the socket. No persistence.

## Dependencies and Integration
Used by `SMBServer` accept and stop paths. Depends on `LittleEndianWriter`, `RuntimeInformation`, and socket APIs.

## Risks and Test Signals
Risks include platform-specific socket option numeric constants, retry-count comment/condition mismatch risk, unchecked `IOControl` failures, and forceful close dropping pending data. Test on .NET Framework, .NET Core/5+ Windows, Linux, null sockets, already-closed sockets, and keepalive timing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Utilities/SocketUtils.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/LogWriter.cs -->
# sources/user-network-fs/smblibrary/SMBServer/LogWriter.cs

## Purpose
Sample server log sink that writes `LogEntry` events to daily log files under a `Logs` directory beside the executable.

## APIs, Types, and Functions
Constructors choose default or explicit log directory. Methods include `OpenLogFile()`, `CloseLogFile()`, `WriteLine()` overloads, `OnLogEntryAdded()`, and `GetAssemblyDirectory()`.

## Control Flow, State, and Persistence
Writes are protected by `m_syncLock`. `OpenLogFile()` rotates when the date changes, creates the logs directory if needed, and opens the daily file in append/write-through mode. Exceptions while opening are swallowed, disabling logging. `OnLogEntryAdded()` filters out `Trace` severity and formats one line per event. Persistent state is daily log files.

## Dependencies and Integration
Used by `ServerUI` as a synchronous subscriber to `SMBServer.LogEntryAdded`.

## Risks and Test Signals
Risks include swallowed open errors, no disposal interface, creating a new `StreamWriter` per line, synchronous disk I/O on server activity, and Windows path separators. Test log directory creation, date rotation, concurrent log events, permission failures, and close/reopen behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/LogWriter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/NetworkInterfaceHelper.cs -->
# sources/user-network-fs/smblibrary/SMBServer/NetworkInterfaceHelper.cs

## Purpose
Utility for the sample UI to enumerate local IPv4 addresses and find the subnet mask for a selected address.

## APIs, Types, and Functions
`GetHostIPAddresses()` returns a list of IPv4 `IPAddress` values from all network interfaces. `GetSubnetMask(IPAddress)` returns the matching `UnicastIPAddressInformation.IPv4Mask` or null.

## Control Flow, State, and Persistence
Both methods iterate `NetworkInterface.GetAllNetworkInterfaces()` and each interface's unicast addresses. No state or persistence.

## Dependencies and Integration
Used by `ServerUI_Load()` and NetBIOS name-server startup.

## Risks and Test Signals
Risks include including down/loopback/virtual interfaces, IPv4-only behavior, null subnet mask on some platforms, and no exception handling around network-interface APIs. Test multi-interface hosts, `IPAddress.Any`, disconnected adapters, and NetBIOS-over-TCP startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/NetworkInterfaceHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Program.cs -->
# sources/user-network-fs/smblibrary/SMBServer/Program.cs

## Purpose
WinForms sample application entry point for the SMB server UI, with global exception handling.

## APIs, Types, and Functions
`Main()` is marked `[STAThread]`, subscribes to `Application.ThreadException` and `AppDomain.CurrentDomain.UnhandledException`, enables visual styles, and runs `ServerUI`. Helper handlers call `HandleUnhandledException()`.

## Control Flow, State, and Persistence
Unhandled UI or domain exceptions are formatted into a message box and then `Application.Exit()` is called. No persistent state is written.

## Dependencies and Integration
Starts the `ServerUI` form. Depends on Windows Forms and threading exception events.

## Risks and Test Signals
Risks include casting `UnhandledExceptionEventArgs.ExceptionObject` directly to `Exception`, showing stack traces to users, and no logging of fatal errors if UI cannot display. Test startup, UI-thread exceptions, background exceptions, and graceful application exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Program.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.Designer.cs -->
# sources/user-network-fs/smblibrary/SMBServer/ServerUI.Designer.cs

## Purpose
WinForms designer-generated layout for the sample SMB server control panel.

## APIs, Types, and Functions
Partial class `ServerUI` defines `Dispose()` and `InitializeComponent()`, plus controls for IP address selection, transport radio buttons, start/stop buttons, integrated authentication, SMB1/SMB2 checkboxes, and labels.

## Control Flow, State, and Persistence
`InitializeComponent()` creates controls, sets fixed positions/sizes/text/default states, wires `Click`, `CheckedChanged`, and `Load` event handlers, and configures a fixed-size form. UI state is in WinForms controls; no persistence.

## Dependencies and Integration
Pairs with `ServerUI.cs` logic. Depends on `System.Windows.Forms` and `System.Drawing`.

## Risks and Test Signals
Risks include fixed non-scaled layout, no localization, SMB2 checkbox text limited to 2.0/2.1 despite optional SMB3 support in the library, and designer edits being overwritten. Test form loading, event wiring, tab order, high-DPI display, and enabled/disabled state transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.Designer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.cs -->
# sources/user-network-fs/smblibrary/SMBServer/ServerUI.cs

## Purpose
Code-behind for the sample SMB server UI. It loads local addresses, reads settings, constructs shares and authentication providers, starts/stops the SMB server and optional NetBIOS name server, and enforces simple share access policy.

## APIs, Types, and Functions
Important methods are constructor, `ServerUI_Load()`, `btnStart_Click()`, `btnStop_Click()`, `chkSMB1_CheckedChanged()`, `chkSMB2_CheckedChanged()`, `InitializeShare()`, `Contains()`, and `IndexOf()`.

## Control Flow, State, and Persistence
On load the IP combo is populated with `Any` plus IPv4 addresses. Start chooses transport, builds integrated or independent NTLM authentication, reads `Settings.xml`, creates `FileSystemShare` objects backed by `NTDirectoryFileSystem`, attaches synchronous logging, starts `SMBServer`, and optionally starts `NameServer` for NetBIOS over TCP. UI controls are disabled while running. Stop stops server/logging/name server and re-enables controls. Access policy maps wildcard `*` to `Users` and checks read/write lists case-insensitively.

## Dependencies and Integration
Integrates the library server with Win32 NT file store/security providers, settings helper types, network interface helper, and log writer.

## Risks and Test Signals
Risks include default integrated auth hiding settings users, plain-text passwords for independent auth, synchronous logging, no validation of share paths before server start, `Users` wildcard semantics tied to settings parsing, and no form-closing stop path. Test start/stop for both transports, bad settings file, access allow/deny matrix, name-server startup, checked-protocol invariants, and log writing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ServerUI.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Settings.xml -->
# sources/user-network-fs/smblibrary/SMBServer/Settings.xml

## Purpose
Sample XML configuration consumed by the SMB server UI for independent NTLM users and disk share definitions.

## APIs, Types, and Functions
The XML root is `Settings` with `Shares/Share` entries (`Name`, `Path`, `ReadAccess Accounts`, `WriteAccess Accounts`) and `Users/User` entries (`AccountName`, `Password`).

## Control Flow, State, and Persistence
`SettingsHelper` loads this file from the executable directory at start time. The sample defines a `Shared` share at `C:\Shared`, read access for `*`, write access for `Admin,Test`, and users `Admin`, `Guest`, and `Test` with plain-text passwords.

## Dependencies and Integration
Used by `SettingsHelper.ReadSharesSettings()` and `ReadUserSettings()` when integrated Windows authentication is disabled.

## Risks and Test Signals
Risks include plain-text credentials, Windows-specific sample path, permissive wildcard read access, no schema validation, and deployment mismatch if the file is not copied beside the executable. Test parsing, wildcard mapping, missing attributes, nonexistent share path, and independent-auth login for sample users.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/Settings.xml -->
