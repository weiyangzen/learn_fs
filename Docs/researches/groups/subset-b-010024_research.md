# subset-b-010024 research

Grouped research report for SMBLibrary SMB2 wire structures, server connection/session state, and SMB1 server helper paths. Each source file section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Header.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Header.cs

## Purpose

Defines the fixed 64-byte SMB2 packet header serializer/parser used by SMB2 request and response packets. It models protocol id, command, credit fields, status, flags, chaining offset, message id, sync tree id or async id, session id, and optional signing signature.

## Important APIs, Types, And Functions

`SMB2Header(SMB2CommandName)` builds an outbound header, `SMB2Header(byte[], int)` parses inbound bytes, `WriteBytes` serializes fields, `IsResponse`, `IsAsync`, `IsRelatedOperations`, and `IsSigned` toggle flag bits, and `IsValidSMB2Header` checks the `0xFE 'SMB'` signature.

## Control Flow

Parsing reads the common prefix, then branches on `SMB2PacketHeaderFlags.AsyncCommand` to interpret bytes 32-39 as either `AsyncID` or `Reserved` plus `TreeID`. Serialization mirrors that branch and only writes the 16-byte signature when the signed flag is set.

## State And Persistence Behavior

The class is transient wire state. Persistence is limited to values copied into packet objects and later used by server dispatch, signing, compounding, and response correlation.

## Dependencies And Integration Points

Depends on `Utilities` byte readers/writers, SMB2 enums, and `NTStatus`. It integrates with packet framing, SMB2 signing, async completion, tree/session lookup, and compound `NextCommand` handling.

## Risks And Edge Cases

Parsed unsigned headers leave `Signature` unset, so downstream code must not assume a non-null array. The parser does not validate `StructureSize`, buffer length beyond the first four bytes in `IsValidSMB2Header`, or impossible flag combinations.

## Test Signals

Useful signals are round-trip byte equality for sync and async headers, signed versus unsigned signature behavior, response flag toggling, compound `NextCommand` preservation, and rejection of short or wrong-signature buffers.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Header.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2TransformHeader.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2TransformHeader.cs

## Purpose

Implements the SMB 3.x transform header used for encrypted SMB2 messages. It carries the transform protocol id, authentication signature, nonce, original plaintext size, encryption flags/algorithm field, and session id.

## Important APIs, Types, And Functions

`SMB2TransformHeader(byte[], int)` parses a 52-byte transform header, `WriteBytes` writes the protocol id and signature plus associated data, `GetAssociatedData` returns the nonce-through-session-id span for AEAD authentication, and `IsTransformHeader` checks the `0xFD 'SMB'` signature.

## Control Flow

Outbound writing places the first 20 bytes separately, then delegates to `WriteAssociatedData` for the nonce, original size, reserved field, flags, and session id. Inbound parsing reads the same fixed offsets.

## State And Persistence Behavior

No durable state is stored here; this is per-message encryption metadata consumed by encryption/decryption and session lookup.

## Dependencies And Integration Points

Depends on `Utilities` byte helpers and `SMB2TransformHeaderFlags`. It is an integration point between SMB 3.x encryption code and session key material.

## Risks And Edge Cases

The default constructor initializes only `ProtocolId`; callers must set `Signature` and `Nonce` before writing or `ByteWriter` can fail. `IsTransformHeader` does not check buffer length. The flags field is overloaded with algorithm semantics for older dialects, so dialect-specific validation belongs above this class.

## Test Signals

Round-trip tests should cover full header serialization, associated-data bytes excluding signature/protocol id, short-buffer failure behavior, and AES-CCM/GCM session-id lookup paths.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2TransformHeader.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/CreateContext.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/CreateContext.cs

## Purpose

Represents an SMB2 `SMB2_CREATE_CONTEXT` entry and static helpers for reading, writing, and sizing lists of create contexts attached to SMB2 CREATE requests and responses.

## Important APIs, Types, And Functions

Fields include `Next`, `Name`, `Data`, and reserved/offset bookkeeping. The constructor parses one context, private `WriteBytes` serializes one context, `Length` sizes it, and the list helpers process 8-byte aligned chains.

## Control Flow

Reading follows each context's `Next` offset until zero. Writing computes each context length, pads all but the last to 8-byte alignment, stores `Next`, then writes name and data payload at computed offsets.

## State And Persistence Behavior

The structure carries create-time extension state such as durable handles, leases, query-on-disk-id, or negotiate contexts. It is not persisted by itself; server/client create handlers interpret `Name` and `Data`.

## Dependencies And Integration Points

Uses `Utilities` byte helpers and `Math.Ceiling`. It integrates with SMB2 CREATE marshalling and context-specific parsers outside this file.

## Risks And Edge Cases

`WriteBytes` treats `Name` as ANSI bytes, but `Length` multiplies `Name.Length` by two; this can overestimate buffers and offsets relative to actual write behavior. The reader trusts offsets and lengths without bounds checks or cycle protection on malformed `Next` chains.

## Test Signals

Test one and multiple contexts, empty data, non-8-byte name lengths, exact `Next` offsets, malformed offsets, and create-context names with non-ASCII characters if the protocol layer claims ANSI semantics.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/CreateContext.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/CipherAlgorithm.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/CipherAlgorithm.cs

## Purpose

Declares SMB 3.1.1 negotiate encryption cipher identifiers: AES-128-CCM, AES-128-GCM, AES-256-CCM, and AES-256-GCM.

## Important APIs, Types, And Functions

The public `CipherAlgorithm : ushort` enum maps wire values `0x0001` through `0x0004`.

## Control Flow

There is no control flow; values are consumed by encryption capability parsing and negotiate selection.

## State And Persistence Behavior

No runtime state. The selected enum value becomes part of negotiated session encryption state elsewhere.

## Dependencies And Integration Points

Used by `EncryptionCapabilities` and SMB2 negotiate/encryption code.

## Risks And Edge Cases

Compatibility depends on negotiate code respecting dialect support. Advertising AES-256 ciphers to dialects or peers that do not support them would be a higher-layer bug.

## Test Signals

Verify wire-value round trips and cipher ordering preference in negotiate capability tests.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/CipherAlgorithm.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/HashAlgorithm.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/HashAlgorithm.cs

## Purpose

Declares the SMB 3.1.1 preauthentication integrity hash algorithm enum.

## Important APIs, Types, And Functions

`HashAlgorithm : ushort` currently exposes `SHA512 = 1`, matching SMB2 preauth integrity capabilities.

## Control Flow

No control flow; the value is serialized by preauth capability contexts.

## State And Persistence Behavior

No local state. Negotiation code uses the selected hash to build and update the preauth integrity hash.

## Dependencies And Integration Points

Used by `PreAuthIntegrityCapabilities` and SMB 3.1.1 negotiate handling.

## Risks And Edge Cases

Only SHA-512 is represented. Future algorithms would need enum and selection updates.

## Test Signals

Round-trip preauth capability parsing and negotiation should assert value `1` maps to SHA-512.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/HashAlgorithm.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/LockFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/LockFlags.cs

## Purpose

Defines SMB2 lock element flag bits for shared locks, exclusive locks, unlock requests, and fail-immediately behavior.

## Important APIs, Types, And Functions

`LockFlags : uint` is a `[Flags]` enum with protocol constants `0x1`, `0x2`, `0x4`, and `0x8`.

## Control Flow

No control flow; `LockElement` reads, writes, and toggles these bits.

## State And Persistence Behavior

No local persistence. Values are passed to server file-lock handling.

## Dependencies And Integration Points

Consumed by `LockElement` and SMB2 lock request processing.

## Risks And Edge Cases

The enum permits invalid combinations such as shared plus exclusive plus unlock; validation must happen in lock command handling.

## Test Signals

Test bitwise combinations and command-layer rejection of mutually exclusive flag mixes.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/LockFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/FileID.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/FileID.cs

## Purpose

Models the SMB2 16-byte file identifier made of persistent and volatile 64-bit ids.

## Important APIs, Types, And Functions

`FileID(byte[], int)` parses two little-endian `ulong` values and `WriteBytes` serializes them. `Length` is the fixed 16-byte wire size.

## Control Flow

No branching: persistent id is at offset 0 and volatile id at offset 8.

## State And Persistence Behavior

In this server, `SMB2Session` uses the volatile id as the dictionary key for open files and open searches; persistent is set equal to volatile because durable handles are not supported.

## Dependencies And Integration Points

Used by SMB2 create/close/read/write/query and async context code.

## Risks And Edge Cases

Durable-handle semantics are not implemented despite the persistent field. Callers must validate session scope and not trust a `FileID` from another session.

## Test Signals

Round-trip id serialization, session lookup by volatile id, invalid id rejection, and durable-handle non-support behavior are key signals.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/FileID.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/LockElement.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/LockElement.cs

## Purpose

Represents one SMB2 byte-range lock element and provides helpers for lock-list marshalling.

## Important APIs, Types, And Functions

Fields are `Offset`, `Length`, `Flags`, and `Reserved`. Boolean properties toggle each `LockFlags` bit. `ReadLockList` and `WriteLockList` process repeated 24-byte elements.

## Control Flow

Parsing reads 64-bit offset/length then 32-bit flags/reserved. The boolean setters mutate the flag mask in place. List helpers step by `StructureLength`.

## State And Persistence Behavior

Lock elements are request/response payload data; persistent lock state is managed by `INTFileStore.LockFile` and `UnlockFile` in command handlers.

## Dependencies And Integration Points

Uses `Utilities` byte helpers and `LockFlags`; integrates with SMB2 lock request handling.

## Risks And Edge Cases

`WriteBytes` writes `Flags` and `Reserved` with `WriteUInt64` at offsets 16 and 20 even though both fields are 32-bit. That can overwrite beyond the 24-byte structure and corrupt adjacent elements. The struct also does not validate exclusive/shared/unlock combinations.

## Test Signals

Round-trip a single lock and a two-lock list with sentinels after the buffer to catch overwrite. Add validation tests for shared, exclusive, unlock, and fail-immediately combinations.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/LockElement.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/EncryptionCapabilities.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/EncryptionCapabilities.cs

## Purpose

Implements the SMB2 encryption capabilities negotiate context, carrying the list of cipher algorithms a peer supports.

## Important APIs, Types, And Functions

Extends `NegotiateContext`, exposes `Ciphers`, overrides `WriteData`, `DataLength`, and `ContextType`.

## Control Flow

Writing emits a cipher count at data offset 0, followed by each 16-bit cipher at offset `2 + index * 2`. Reading gets the count and appends parsed enum values.

## State And Persistence Behavior

The context is transient negotiate data. Its chosen cipher affects later SMB3 transform encryption state.

## Dependencies And Integration Points

Depends on `NegotiateContext`, `CipherAlgorithm`, and `Utilities`; used by SMB2 negotiate parsing and generation.

## Risks And Edge Cases

The read loop currently reads ciphers from `Data` at `index * 2`, so the first parsed cipher is the cipher count rather than the first cipher value. This can corrupt capability negotiation. Bounds checks are also absent for short data.

## Test Signals

Parse a buffer with two known ciphers and assert the first value is not the count. Round-trip write/read and short-data failure tests should cover this file.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/EncryptionCapabilities.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/NegotiateContext.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/NegotiateContext.cs

## Purpose

Provides the base SMB2 negotiate context record and list helpers for SMB 3.1.1 negotiate extensions.

## Important APIs, Types, And Functions

The base stores context type, reserved value, and raw `Data`. `ReadNegotiateContext` dispatches known types to `PreAuthIntegrityCapabilities` or `EncryptionCapabilities`; list helpers read/write 8-byte aligned context arrays and compute lengths.

## Control Flow

Reading one context consumes the fixed 8-byte header and raw data. Reading a list advances by each context's padded length. Writing calls virtual `WriteData`, writes type/length/reserved, and copies data.

## State And Persistence Behavior

No persisted state; instances carry negotiate-time metadata that later determines preauth hashing and encryption settings.

## Dependencies And Integration Points

Uses `Utilities` and negotiate context subclasses. It is consumed by negotiate request/response structures.

## Risks And Edge Cases

Unknown contexts are preserved only as raw data. The reader trusts `count`, offsets, and `DataLength`, so malformed packets can cause out-of-range reads. Padding bytes are not explicitly zeroed by this class.

## Test Signals

Test dispatch for known types, raw preservation for unknown types, padded list offsets, last-entry unpadded length computation, and short-buffer rejection at the packet layer.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/NegotiateContext.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/PreAuthIntegrityCapabilities.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/PreAuthIntegrityCapabilities.cs

## Purpose

Implements the SMB2 preauthentication integrity capabilities negotiate context, including supported hash algorithms and salt.

## Important APIs, Types, And Functions

Extends `NegotiateContext`, exposes `HashAlgorithms` and `Salt`, overrides `WriteData`, `DataLength`, and `ContextType`.

## Control Flow

Parsing reads hash count and salt length, reads each 16-bit hash algorithm starting at offset 4, then reads salt after the algorithm list. Writing emits the same layout.

## State And Persistence Behavior

The context is negotiate-time data. The selected algorithm and salt feed SMB 3.1.1 preauth integrity computation outside this file.

## Dependencies And Integration Points

Depends on `HashAlgorithm`, `NegotiateContext`, and byte utilities.

## Risks And Edge Cases

`Salt` is not initialized by the default constructor, so callers must set it before `DataLength` or `WriteData`. The parser trusts lengths without data-size validation.

## Test Signals

Round-trip tests should cover one SHA-512 value, non-empty salt, empty salt if allowed, null-salt guard behavior, and malformed short data.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/NegotiateContext/PreAuthIntegrityCapabilities.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionManager.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionManager.cs

## Purpose

Tracks active server connections, releases connection resources, sends keepalive probes, and aggregates session information.

## Important APIs, Types, And Functions

`AddConnection`, `RemoveConnection`, `ReleaseConnection`, `ReleaseConnection(IPEndPoint)`, `SendSMBKeepAlive`, `ReleaseAllConnections`, and `GetSessionsInformation` operate on the active connection list.

## Control Flow

Connections are added under a list lock. Release aborts the send queue, releases the socket, closes sessions, disposes the receive buffer, and removes the entry. Keepalive snapshots the list and sends unsolicited SMB1 or SMB2 echo replies when both receive and send timestamps are stale.

## State And Persistence Behavior

Maintains in-memory `m_activeConnections`; no disk persistence. Releasing a connection cascades to session and file handle cleanup.

## Dependencies And Integration Points

Uses `ConnectionState`, SMB1/SMB2 echo helpers, `SMBServer.Enqueue*`, `SocketUtils`, and `SessionInformation`.

## Risks And Edge Cases

The keepalive snapshot is made without locking `m_activeConnections`, unlike other methods, so concurrent mutation could race. Release assumes buffer disposal under a receive-buffer lock is sufficient for any receiver thread.

## Test Signals

Exercise add/remove idempotence, release cleanup order, release by endpoint, keepalive for SMB1 and SMB2 states, and concurrent release while enumerating sessions.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionManager.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionRequestEventArgs.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionRequestEventArgs.cs

## Purpose

Event argument object for server connection admission decisions.

## Important APIs, Types, And Functions

Public fields are `IPEndPoint` and `Accept`, defaulting to true. The constructor records the remote endpoint.

## Control Flow

No internal control flow; event subscribers can flip `Accept` before the server proceeds.

## State And Persistence Behavior

Per-event transient state only.

## Dependencies And Integration Points

Uses `System.Net.IPEndPoint` and `EventArgs`; integrates with connection accept hooks in the server.

## Risks And Edge Cases

Public mutable fields make validation a caller responsibility. A null endpoint is not rejected here.

## Test Signals

Test default accept behavior and server rejection path when an event handler sets `Accept = false`.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionRequestEventArgs.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ConnectionState.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ConnectionState.cs

## Purpose

Base connection state shared by SMB1 and SMB2 connections. It holds socket, endpoint, NetBIOS receive buffer, send queue, timestamps, dialect, authentication context, and logging callback.

## Important APIs, Types, And Functions

Constructors create or wrap state; virtual `CloseSessions` and `GetSessionsInformation` are overridden by dialect-specific subclasses. Properties expose transport objects and timestamps; `UpdateLastReceiveDT`, `UpdateLastSendDT`, and `ConnectionIdentifier` support connection management.

## Control Flow

The copy constructor preserves the same socket, receive buffer, send queue, and last-send reference when upgrading a generic state into SMB1 or SMB2 state. Logging prefixes messages with endpoint identity.

## State And Persistence Behavior

Connection-scoped in-memory state. `LastSendDTRef` is deliberately shared so sender threads keep updating the original reference after state conversion.

## Dependencies And Integration Points

Depends on sockets, NetBIOS `SessionPacket`, `NBTConnectionReceiveBuffer`, GSS authentication context, and `Utilities.BlockingQueue`/`Reference`.

## Risks And Edge Cases

Most fields are not synchronized beyond the send timestamp reference. Subclasses must close sessions to avoid leaking file handles. `AuthenticationContext` is not copied in the copy constructor, so callers must understand when it is transferred or reused.

## Test Signals

Test SMB1/SMB2 state conversion, timestamp updates visible through the shared reference, connection identifier formatting, and subclass close/session-info overrides.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ConnectionState.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenFileObject.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenFileObject.cs

## Purpose

Stores one open server-side file object in a session: tree id, share name, relative path, backing file-store handle, access mode, and open timestamp.

## Important APIs, Types, And Functions

Constructor records all fields. Properties expose `TreeID`, `ShareName`, mutable `Path`, `Handle`, `FileAccess`, and `OpenedDT`.

## Control Flow

No algorithmic flow; session dictionaries create, look up, mutate path on rename if needed, and remove instances.

## State And Persistence Behavior

This is in-memory open-file state. The actual persistent file state remains in the backing `INTFileStore` handle.

## Dependencies And Integration Points

Uses `System.IO.FileAccess`; consumed by SMB1/SMB2 sessions and command helpers.

## Risks And Edge Cases

The backing `Handle` is an untyped object, so correctness depends on the associated share/file store. The mutable `Path` can diverge from file-store state if rename paths are not updated consistently.

## Test Signals

Open/close tests should assert path, share, access, and timestamp reporting through session information.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenFileObject.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenSearch.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenSearch.cs

## Purpose

Represents an open SMB directory enumeration/search, including cached entries and current enumeration position.

## Important APIs, Types, And Functions

Constructor stores a `List<QueryDirectoryFileInformation>` and `EnumerationLocation`.

## Control Flow

Find-first creates the object with all entries and initial returned count. Find-next slices from `EnumerationLocation`, advances it, and removes the search at end of enumeration.

## State And Persistence Behavior

Session-scoped in-memory search state; it is not refreshed from disk after creation.

## Dependencies And Integration Points

Uses `QueryDirectoryFileInformation`; consumed by SMB1 transaction2 find helpers and SMB2 directory query code.

## Risks And Edge Cases

Cached entries can become stale if the directory changes during enumeration. No internal locking is provided.

## Test Signals

Test find-first/find-next pagination, end-of-search removal, invalid handle lookup, and stale-entry tolerance if files change mid-search.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/OpenSearch.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ProcessStateObject.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ProcessStateObject.cs

## Purpose

Holds partial SMB1 transaction or NT transaction request state while secondary packets arrive.

## Important APIs, Types, And Functions

Public fields capture subcommand id, max response sizes, timeout, transaction name, setup bytes, full parameter/data buffers, and received byte counts.

## Control Flow

Transaction helpers create one object by PID, copy initial fragments, then secondary requests write into the buffers by displacement until both received counts reach total lengths.

## State And Persistence Behavior

Connection-scoped in-memory assembly state keyed by process id in `SMB1ConnectionState`.

## Dependencies And Integration Points

Used by `TransactionHelper` and `NTTransactHelper`.

## Risks And Edge Cases

State is keyed only by PID, so overlapping transactions from the same PID can collide. Received counts are incremented by fragment length rather than tracking unique ranges, so duplicate or overlapping secondary packets can make a transaction appear complete incorrectly.

## Test Signals

Test multi-fragment assembly, out-of-order displacement, duplicate fragment handling, PID collision behavior, and cleanup after complete or invalid sequences.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/ProcessStateObject.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1AsyncContext.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1AsyncContext.cs

## Purpose

Carries context for a pending asynchronous SMB1 operation, mainly change-notify and cancel handling.

## Important APIs, Types, And Functions

Public fields hold UID, TID, PID, MID, FID, connection reference, and the backing file-store IO request token.

## Control Flow

Notify-change creates the context before calling the file store. Cancel lookup uses UID/TID/PID/MID to find it and passes `IORequest` to `Cancel`.

## State And Persistence Behavior

Connection-scoped in-memory pending request state in `SMB1ConnectionState.m_pendingRequests`.

## Dependencies And Integration Points

Used by `NotifyChangeHelper`, `CancelHelper`, and `SMB1ConnectionState`.

## Risks And Edge Cases

The untyped `IORequest` token must match the file-store implementation. Context identity omits command name, so reused MID/PID combinations must be managed carefully.

## Test Signals

Test pending notify creation, cancel removal, completion removal, and behavior after session or file closes before completion.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1AsyncContext.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1ConnectionState.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1ConnectionState.cs

## Purpose

Extends `ConnectionState` with SMB1-specific session, tree id, file id, transaction assembly, and async request tracking.

## Important APIs, Types, And Functions

Provides allocation and CRUD methods for UIDs, sessions, TIDs, FIDs, process states, and async contexts. Overrides session cleanup and session information aggregation.

## Control Flow

Allocation scans from the next id, skips reserved values, and checks all relevant dictionaries. Session removal closes resources before deleting. Async contexts are searched by UID/TID/PID/MID.

## State And Persistence Behavior

All state is connection-local memory: sessions by UID, process state by PID, and pending async list. Closing sessions closes open files through session close paths.

## Dependencies And Integration Points

Depends on `SMB1Session`, `ProcessStateObject`, `SMB1AsyncContext`, and base connection state.

## Risks And Edge Cases

Some scans over sessions are not protected by `m_sessions` locks even though sessions can mutate. PID-only process state can collide for concurrent transactions. Reserved-value handling skips zero TID/FID despite comments saying zero is valid.

## Test Signals

Test allocation wraparound and reserved values, concurrent session add/remove, transaction state lifecycle, async lookup/removal, and close-session file cleanup.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1ConnectionState.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1Session.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1Session.cs

## Purpose

Stores SMB1 authenticated session state, connected tree shares, open file handles, and open directory searches.

## Important APIs, Types, And Functions

Tree methods add, get, disconnect, and test TIDs. File methods add, get, remove, and report open files. Search methods allocate, add, get, and remove search handles. `Close` disconnects all trees.

## Control Flow

Adding a tree or file asks the connection for a globally unique TID/FID, then stores the share or `OpenFileObject`. Disconnecting a tree closes every open file under that tree through the share's file store before removing the tree.

## State And Persistence Behavior

Session-local in-memory dictionaries. Persistent file effects happen only through the underlying file store handles.

## Dependencies And Integration Points

Uses `ISMBShare`, `OpenFileObject`, `OpenSearch`, `SecurityContext`, and SMB1 connection id allocation.

## Risks And Edge Cases

Search dictionaries are mutated without the same connection lock used for files. The session key is stored but not exposed in this file, so signing use must be elsewhere. `MaxSearches` is declared but not enforced.

## Test Signals

Test tree disconnect closing only matching handles, FID uniqueness across sessions, search pagination handles, and `Close` cleanup with multiple shares.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB1Session.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2AsyncContext.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2AsyncContext.cs

## Purpose

Carries context for a pending asynchronous SMB2 operation.

## Important APIs, Types, And Functions

Public fields hold async id, `FileID`, connection, session id, tree id, and file-store IO request token.

## Control Flow

Created by `SMB2ConnectionState.CreateAsyncContext`, later looked up by async id for completion or cancellation.

## State And Persistence Behavior

Connection-scoped pending request state in an SMB2 async dictionary.

## Dependencies And Integration Points

Uses `SMB2.FileID` and `SMB2ConnectionState`.

## Risks And Edge Cases

The class is an unvalidated bag of fields. Callers must ensure session/tree/file are still valid when the async completion arrives.

## Test Signals

Test async id creation, lookup, removal, cancellation, and completion after file/session close.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2AsyncContext.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2ConnectionState.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2ConnectionState.cs

## Purpose

Extends base connection state with SMB2 sessions and async request tracking.

## Important APIs, Types, And Functions

Methods allocate/create/get/remove sessions, close all sessions, collect session information, allocate async ids, and create/get/remove async contexts.

## Control Flow

Session ids and async ids scan from monotonic counters, skip reserved values, then add to dictionaries. Session removal closes the session before removing it. Async contexts are keyed by generated async id.

## State And Persistence Behavior

Connection-local dictionaries for sessions and pending SMB2 operations. Persistent file state is held by session open-file handles and underlying file stores.

## Dependencies And Integration Points

Depends on `SMB2Session`, `SMB2AsyncContext`, `FileID`, and base `ConnectionState`.

## Risks And Edge Cases

Dictionary membership checks in allocation are not locked consistently with dictionary mutation. The code skips `0xFFFFFFFF` but not all protocol-reserved 64-bit ids. Durable/persistent reconnect state is not represented.

## Test Signals

Test session allocation/removal, async allocation wraparound, session info aggregation, close cleanup, and races between async completion and session removal.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2ConnectionState.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2Session.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2Session.cs

## Purpose

Stores SMB2 authenticated session state, connected tree shares, open files keyed by volatile file id, open searches, signing metadata, and security context.

## Important APIs, Types, And Functions

Methods add/get/disconnect trees, add/get/remove open files, report open file information, manage open searches, and close the session. Properties expose session key, security context, user/machine names, creation time, signing-required flag, and signing key.

## Control Flow

Tree ids and volatile file ids are session-scoped counters. Add-open-file creates an SMB2 `FileID` with persistent equal to volatile because durable handles are unsupported. Disconnecting a tree closes matching open handles and removes the tree.

## State And Persistence Behavior

Session-local memory only. Open handles persist until close, tree disconnect, or session close; durable handle persistence across disconnect is explicitly not implemented.

## Dependencies And Integration Points

Uses `ISMBShare`, `OpenFileObject`, `OpenSearch`, `FileID`, and `SecurityContext`.

## Risks And Edge Cases

Open searches are mutated without locking. `GetConnectedTree` and `IsTreeConnected` are not locked. Persistent file ids are synthetic, so SMB2 durable/persistent handle clients will not get reconnect semantics.

## Test Signals

Test tree/file id uniqueness, invalid cross-session file id rejection, signing metadata preservation, tree disconnect cleanup, and open-search lifecycle.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SMB2Session.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SecurityContext.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SecurityContext.cs

## Purpose

Public security context object attached to authenticated sessions and passed into file-store operations.

## Important APIs, Types, And Functions

Constructor records username, machine name, client endpoint, GSS context, and access token. Properties expose user, machine, and endpoint; `AuthenticationContext` and `AccessToken` are public fields.

## Control Flow

No internal flow. Authentication helpers build it after NTLM/GSS completion, and file stores consume it for authorization decisions.

## State And Persistence Behavior

Session-scoped identity state. It does not persist beyond session lifetime.

## Dependencies And Integration Points

Depends on GSSAPI context and `IPEndPoint`; used by SMB1/SMB2 sessions and file store helpers.

## Risks And Edge Cases

Public mutable authentication/token fields can be changed by any caller. There is no null or lifetime validation of the access token.

## Test Signals

Authentication tests should verify correct user/machine/endpoint propagation and file-store authorization receiving the expected token.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/ConnectionState/SecurityContext.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Enums/SMBDialect.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Enums/SMBDialect.cs

## Purpose

Defines the server's coarse negotiated SMB dialect enum.

## Important APIs, Types, And Functions

Values are `NotSet`, `NTLM012`, `SMB202`, `SMB210`, and `SMB300`.

## Control Flow

No control flow; connection negotiation stores one value in `ConnectionState.Dialect`.

## State And Persistence Behavior

Connection-level negotiated protocol state.

## Dependencies And Integration Points

Used by connection/session information and dialect-specific dispatch.

## Risks And Edge Cases

The enum stops at SMB 3.0 while other source files include SMB 3.1.1 structures; reporting or gating may be too coarse for newer dialect behavior.

## Test Signals

Negotiation tests should assert expected enum values and session information reporting for SMB1 and SMB2 connections.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Enums/SMBDialect.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Helpers/ServerPathUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Helpers/ServerPathUtils.cs

## Purpose

Provides helpers for extracting server-relative path, share-relative path, and share name from UNC-like server paths.

## Important APIs, Types, And Functions

`GetRelativeServerPath`, `GetRelativeSharePath`, and `GetShareName` operate on string paths such as `\\server\share\file`.

## Control Flow

The server-relative helper strips the leading server component. Share-relative helper strips the share component. Share-name helper strips leading slash then truncates at the next slash.

## State And Persistence Behavior

Stateless string utility.

## Dependencies And Integration Points

Used by server dispatch and tree-connect style path handling.

## Risks And Edge Cases

`GetRelativeSharePath` computes the separator index in `relativePath` but returns `path.Substring(index)`, which is wrong for UNC inputs because the index applies to the shortened string. It can return a substring from the original server name rather than the share-relative suffix.

## Test Signals

Test UNC server-only, UNC share-only, UNC share plus file, already-relative paths, no leading slash, and malformed empty strings.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Helpers/ServerPathUtils.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/OpenFileInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/OpenFileInformation.cs

## Purpose

DTO for reporting one open file in server session information.

## Important APIs, Types, And Functions

Public fields are share name, path, `FileAccess`, and open timestamp. The constructor initializes all fields.

## Control Flow

No logic; sessions build instances from `OpenFileObject` values.

## State And Persistence Behavior

Snapshot reporting state. It does not own or close the underlying file handle.

## Dependencies And Integration Points

Uses `System.IO.FileAccess`; consumed by `SessionInformation` and management/status APIs.

## Risks And Edge Cases

Fields are mutable and represent a point-in-time snapshot that can become stale immediately after reporting.

## Test Signals

Session information tests should assert open file entries match active handles and disappear after close or tree disconnect.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/OpenFileInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/SessionInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/SessionInformation.cs

## Purpose

DTO for reporting an authenticated SMB session and its open files.

## Important APIs, Types, And Functions

Public fields are client endpoint, dialect, user name, machine name, open file list, and creation timestamp. The constructor initializes all fields.

## Control Flow

No internal logic; connection states aggregate instances from sessions.

## State And Persistence Behavior

Snapshot of in-memory session state.

## Dependencies And Integration Points

Uses `OpenFileInformation`, `SMBDialect`, and `IPEndPoint`.

## Risks And Edge Cases

Mutable fields and lists can be altered by consumers unless copied. The open-file list can be stale under concurrent close/open activity.

## Test Signals

Test aggregation across multiple SMB1/SMB2 sessions and snapshot contents after file open and close.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/Information/SessionInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/NameServer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/NameServer.cs

## Purpose

Implements a minimal NetBIOS name service responder and name registration broadcaster for the server's IPv4 address.

## Important APIs, Types, And Functions

Constructor validates IPv4 concrete address and computes broadcast address. `Start` binds UDP port 137 and begins async receive plus registration thread. `Stop` closes the client. `GetBroadcastAddress` computes subnet broadcast address.

## Control Flow

Receive callback parses name-service packets. NB queries for the local machine workstation/file-server suffix receive positive address responses. NBSTAT requests receive workstation, file server, and workgroup names. Registration sends three name registration requests four times to broadcast.

## State And Persistence Behavior

Holds UDP client, server/broadcast addresses, and listening flag. No durable persistence.

## Dependencies And Integration Points

Uses NetBIOS packet classes, `UdpClient`, `Environment.MachineName`, and threading.

## Risks And Edge Cases

Binding directly to port 137 may require privileges and conflict with OS services. `Stop` assumes `m_client` exists. Packet parse exceptions are swallowed. Only IPv4 and a fixed `WORKGROUP` are supported.

## Test Signals

Test broadcast address math, constructor rejection of `IPAddress.Any` and IPv6, NB query responses, NBSTAT responses, stop during receive, and registration send count.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/NameServer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/CancelHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/CancelHelper.cs

## Purpose

Handles SMB1 `NT_CANCEL` by cancelling a pending asynchronous file-store request.

## Important APIs, Types, And Functions

`ProcessNTCancelRequest` looks up session and pending async context by UID/TID/PID/MID, calls `share.FileStore.Cancel`, logs the target path when available, and removes the context on success or cancelled status.

## Control Flow

If no context exists, it silently does nothing. If cancel succeeds or reports already cancelled, the context is removed from the connection pending list.

## State And Persistence Behavior

Mutates SMB1 connection pending async state; backing IO cancellation is delegated to the file store.

## Dependencies And Integration Points

Depends on `SMB1ConnectionState`, `SMB1AsyncContext`, `ISMBShare.FileStore`, and logging.

## Risks And Edge Cases

The method assumes `state.GetSession(header.UID)` returns non-null before path logging. Cancel behavior depends entirely on the untyped `IORequest` token.

## Test Signals

Test cancel of existing notify, cancel of unknown MID, cancellation status variants, and session/file closed before cancel.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/CancelHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/CloseHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/CloseHelper.cs

## Purpose

Builds SMB1 close responses for file handles and find-search handles.

## Important APIs, Types, And Functions

`GetCloseResponse` closes a file-store handle for a request FID and removes it from the session. `GetFindClose2Response` removes an open search by search handle.

## Control Flow

File close validates FID, calls `CloseFile`, returns an error response on failure, logs success, removes the open file, and returns `CloseResponse`.

## State And Persistence Behavior

Mutates session open-file and open-search dictionaries; persistent file state is affected by file-store close semantics such as delete-on-close.

## Dependencies And Integration Points

Uses SMB1 close command types, `SMB1Session`, `OpenFileObject`, `ISMBShare.FileStore`, and logging.

## Risks And Edge Cases

Find close does not validate whether the search handle existed. File close assumes session lookup succeeds.

## Test Signals

Test valid close, invalid FID status, close failure propagation, delete-on-close effects in the file store, and find-close handle removal.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/CloseHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/EchoHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/EchoHelper.cs

## Purpose

Creates SMB1 echo responses and unsolicited echo replies used as keepalive probes.

## Important APIs, Types, And Functions

`GetEchoResponse` returns one `EchoResponse` per requested echo count, copying request data. `GetUnsolicitedEchoReply` builds a complete SMB1 message with wildcard UID/TID/PID/MID values.

## Control Flow

Normal echo loops from zero to `EchoCount - 1` and sets sequence numbers. Unsolicited echo constructs header flags compatible with NT LANMAN behavior and adds one response command.

## State And Persistence Behavior

No persisted state; keepalive sending updates connection last-send elsewhere.

## Dependencies And Integration Points

Uses SMB1 message/header/echo types. Called by command dispatch and `ConnectionManager.SendSMBKeepAlive`.

## Risks And Edge Cases

Large `EchoCount` can generate many response commands. Unsolicited replies rely on clients discarding unknown PID/MID responses as specified.

## Test Signals

Test sequence numbers, payload echoing, zero count, high count, and keepalive header values.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/EchoHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/FileStoreResponseHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/FileStoreResponseHelper.cs

## Purpose

Implements SMB1 simple file-store command responses for create/delete directory, delete, rename, check directory, query/set file info, set info by FID, and disk information.

## Important APIs, Types, And Functions

Each `Get*Response` method validates access where the share is `FileSystemShare`, delegates to `SMB1FileStoreHelper` or `FileStore`, maps results into SMB1 response structures, logs, and returns `ErrorResponse` on failure.

## Control Flow

Path operations normalize or pass path strings, run share-level read/write checks, call helper methods, set `header.Status`, and build command-specific responses. Disk information queries `FileFsSizeInformation` and clamps counts to 16-bit SMB1 fields.

## State And Persistence Behavior

Mutates persistent filesystem through file-store operations for create, delete, rename, and set info. It also reads open-file state for SetInformation2.

## Dependencies And Integration Points

Depends on SMB1 command classes, `SMB1FileStoreHelper`, `FileSystemShare`, `INTFileStore`, and session security context.

## Risks And Edge Cases

Access checks are only applied for `FileSystemShare`, so named pipe or custom shares must enforce their own checks. Size fields are truncated for legacy responses. Several methods assume valid sessions.

## Test Signals

Cover access denied paths, file versus directory delete, rename source and target permissions, query/set info mapping, disk-size truncation, and invalid FID for SetInformation2.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/FileStoreResponseHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/LockingHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/LockingHelper.cs

## Purpose

Handles SMB1 `LOCKING_ANDX` byte-range lock and unlock requests.

## Important APIs, Types, And Functions

`GetLockingAndXResponse` validates FID, rejects `CHANGE_LOCKTYPE`, processes unlock ranges, processes lock ranges, and rolls back prior locks if a later lock fails.

## Control Flow

The method returns no response when both lock and unlock counts are zero. Unlocks are applied first. Locks use exclusive mode unless the request has `SHARED_LOCK`; on failure, all locks acquired earlier in the same request are unlocked to preserve atomicity.

## State And Persistence Behavior

Persistent lock state lives in the file store. Session open-file state is only read.

## Dependencies And Integration Points

Uses SMB1 lock command types, `SMB1Session`, `OpenFileObject`, and `INTFileStore.LockFile`/`UnlockFile`.

## Risks And Edge Cases

Rollback ignores unlock status. `CANCEL_LOCK` is mentioned in comments but no separate cancel behavior is implemented. Session lookup is assumed valid.

## Test Signals

Test invalid FID, zero-count no-response, unsupported change-locktype, shared/exclusive locks, unlocks, failure rollback, and overlapping lock conflict statuses.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/LockingHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTCreateHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTCreateHelper.cs

## Purpose

Implements SMB1 NT Create AndX open/create handling for files and named pipes.

## Important APIs, Types, And Functions

`GetNTCreateResponse` performs path normalization, access derivation, share access checks, `CreateFile`, session FID allocation, and response creation. Private helpers build named-pipe and filesystem basic/extended responses and map file status/attributes.

## Control Flow

The helper adds `FILE_READ_ATTRIBUTES` to desired access to query network-open information after create. If FID allocation fails, it closes the file-store handle. Named pipes return pipe resource metadata; filesystem opens return timestamps, sizes, attributes, directory flag, and maximal access masks for extended responses.

## State And Persistence Behavior

Creates persistent/open file-store handles and records them in `SMB1Session` open-file state. Actual file creation/truncation depends on requested disposition.

## Dependencies And Integration Points

Depends on SMB1 NT create command types, `NTFileStoreHelper`, `FileSystemShare`, `NamedPipeShare`, `INTFileStore`, and session security context.

## Risks And Edge Cases

Maximal access rights are hard-coded rather than computed from ACLs. Attribute conversion only keeps a subset. The extra read-attributes access can alter authorization requirements compared with the client's request.

## Test Signals

Test file create/open/overwrite statuses, directory opens, named-pipe responses, extended response rights, FID exhaustion cleanup, and access-denied behavior.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTCreateHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTTransactHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTTransactHelper.cs

## Purpose

Assembles and dispatches SMB1 NT transaction requests, including IOCTL, security descriptor set/query, and notify-change.

## Important APIs, Types, And Functions

`GetNTTransactResponse` overloads handle primary and secondary fragments. `GetCompleteNTTransactResponse` dispatches subcommands. Private helpers implement IOCTL, set security descriptor, query security descriptor, and response fragmentation.

## Control Flow

Incomplete requests allocate `ProcessStateObject` and return `NTTransactInterimResponse`. Secondary fragments copy bytes by displacement until complete. Complete requests parse the subcommand, call the relevant helper, return no immediate response for pending notify, or fragment response data against `MaxBufferSize`.

## State And Persistence Behavior

Uses connection process-state assembly and async notify state. Security setters mutate file-store security descriptors; IOCTL and query paths delegate to file-store state.

## Dependencies And Integration Points

Depends on SMB1 NT transaction classes, `NotifyChangeHelper`, `SecurityDescriptor`, `IoControlCode`, `SMB1ConnectionState`, and `INTFileStore` methods.

## Risks And Edge Cases

Assembly is PID-keyed and has overlap-counting issues inherited from `ProcessStateObject`. Response fragmentation loop uses `TransactionResponse.CalculateMessageSize` for additional NT transact responses. Security query returns `STATUS_BUFFER_TOO_SMALL` rather than a partial descriptor.

## Test Signals

Test multi-packet assembly, unknown function status, FSCTL-only rejection, invalid FID, IOCTL buffer overflow, security descriptor set/query, notify pending/completion, and fragmented responses.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NTTransactHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NegotiateHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NegotiateHelper.cs

## Purpose

Builds SMB1 negotiate responses for classic and extended-security negotiation.

## Important APIs, Types, And Functions

`GetNegotiateResponse` returns a non-extended NTLM challenge response. `GetNegotiateResponseExtended` returns capability and GUID information for extended security. `CreateNegotiateMessage` builds the NTLM negotiate flags used for challenge generation.

## Control Flow

The classic path selects the NT LAN Manager dialect index, advertises server limits/capabilities, asks `GSSProvider` for an NTLM challenge, and stores the authentication context in connection state. Extended response advertises extended security and server GUID but does not include the token here.

## State And Persistence Behavior

Initializes connection authentication context and negotiated capability data; no filesystem state.

## Dependencies And Integration Points

Depends on SMB1 negotiate structures, `GSSProvider`, NTLM structures, and `SMBServer.NTLanManagerDialect`.

## Risks And Edge Cases

Dialect index is taken directly from `IndexOf`; absent dialect could become `0xFFFF` after cast. Capabilities are static and may advertise features only partially implemented. Time zone uses obsolete local time APIs.

## Test Signals

Test dialect selection, absent dialect behavior, capability flags, challenge generation, server time fields, and extended-security GUID response.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NegotiateHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NotifyChangeHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NotifyChangeHelper.cs

## Purpose

Starts and completes asynchronous SMB1 NT transaction notify-change requests.

## Important APIs, Types, And Functions

`ProcessNTTransactNotifyChangeRequest` creates async context and calls `FileStore.NotifyChange`. `OnNotifyChangeCompleted` removes context, logs, builds an SMB1 NT transact response or error, and enqueues it.

## Control Flow

The start path locks the context to order logs, sets request status to pending or not implemented. Completion reacquires that lock, removes the async context, reconstructs an SMB1 header from saved ids, fragments success data through `NTTransactHelper`, or sends an error status.

## State And Persistence Behavior

Maintains pending async context in connection state and depends on file-store watch state until completion/cancel.

## Dependencies And Integration Points

Uses `SMB1AsyncContext`, `NTTransactNotifyChange*` structures, `SMBServer.EnqueueMessage`, and file-store `NotifyChange`.

## Risks And Edge Cases

The start method does not validate `openFile` before using `openFile.Handle`; invalid FID can throw. Completion silently drops output if the session disappeared. Oversized change lists are converted to `STATUS_NOTIFY_ENUM_DIR`.

## Test Signals

Test valid notify pending/completion, invalid FID, unsupported file store status mapping, oversized completion data, cancel completion, and session close before callback.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NotifyChangeHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/OpenAndXHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/OpenAndXHelper.cs

## Purpose

Implements legacy SMB1 Open AndX handling and maps OpenAndX modes to NT create semantics.

## Important APIs, Types, And Functions

`GetOpenAndXResponse` normalizes path, converts access/share/open/create options, performs access checks, opens through `CreateFile`, allocates FID, and returns basic or extended file/named-pipe responses. Private converters map access mode, sharing mode, open mode, create options, and open result.

## Control Flow

Invalid access/share/open combinations become `STATUS_OS2_INVALID_ACCESS`. Successful opens add session open-file state. Named-pipe responses use pipe metadata; filesystem responses use `FileNetworkOpenInformation` and clamp file size to 32 bits.

## State And Persistence Behavior

Creates or opens file-store handles and records session FIDs. File creation/truncation follows converted disposition.

## Dependencies And Integration Points

Depends on SMB1 OpenAndX command types, shares, `NTFileStoreHelper`, and file-store create/query APIs.

## Risks And Edge Cases

`SharingMode.Compatibility` maps to read sharing only and may not match all legacy behavior. Access rights in responses are simplified. Extended maximal access rights are hard-coded.

## Test Signals

Test all access/share/open-mode conversions, invalid combinations, named-pipe open, file size clamping, FID exhaustion cleanup, and access-denied cases.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/OpenAndXHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/ReadWriteResponseHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/ReadWriteResponseHelper.cs

## Purpose

Builds SMB1 read, read-andx, write, write-andx, and flush responses against open file-store handles.

## Important APIs, Types, And Functions

Methods validate FIDs and share access, call `ReadFile`, `WriteFile`, or `FlushFileBuffers`, map EOF for ReadAndX, set returned counts/data, and produce error responses on failure.

## Control Flow

ReadAndX honors `LargeRead` for filesystem shares by using `MaxCountLarge`; EOF is converted to success with zero data for Windows/JCIFS compatibility. Write methods return written counts. Flush with FID `0xFFFF` currently returns success without scanning PID-owned opens.

## State And Persistence Behavior

Reads and writes persistent file content through `INTFileStore`. Session open-file state is read but not mutated.

## Dependencies And Integration Points

Uses SMB1 read/write/flush command types, `FileSystemShare` access checks, and file-store read/write/flush APIs.

## Risks And Edge Cases

FID `0xFFFF` flush is effectively a no-op despite the comment requiring PID-wide flush. Access checks are share-type dependent. Count casts to 16-bit in legacy write/read responses can truncate large counts.

## Test Signals

Test invalid FID, access denied, EOF mapping, large read selection, short writes, named-pipe read/write behavior, and flush-all semantics.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/ReadWriteResponseHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.Query.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.Query.cs

## Purpose

Partial SMB1 file-store helper for querying file information by path or handle and converting NT file information to SMB1 query information levels.

## Important APIs, Types, And Functions

`GetFileInformation` overloads open a path for read attributes or query an existing handle. It maps SMB1 `QueryInformationLevel` to `FileInformationClass`, calls the file store, and converts through `QueryInformationHelper`.

## Control Flow

Path-based methods open the object with `FILE_READ_ATTRIBUTES`, query, close, and return status. Unsupported information levels return `STATUS_OS2_INVALID_LEVEL`.

## State And Persistence Behavior

No persistent mutations; opens are temporary and closed before return.

## Dependencies And Integration Points

Depends on `INTFileStore`, `QueryInformationHelper`, `UnsupportedInformationLevelException`, and `SecurityContext`.

## Risks And Edge Cases

Temporary opens can fail because of sharing conflicts even for metadata queries. Path-based file information class overload always uses `FILE_READ_ATTRIBUTES`, which may not be sufficient for every class.

## Test Signals

Test supported/unsupported levels, path and handle queries, close-on-error, sharing conflicts, and conversion correctness for timestamps, sizes, and attributes.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.Query.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryDirectory.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryDirectory.cs

## Purpose

Partial SMB1 helper for directory enumeration by wildcard pattern.

## Important APIs, Types, And Functions

`QueryDirectory` splits a file-name pattern into directory path and search pattern, opens the directory, calls `fileStore.QueryDirectory`, closes the handle, and returns entries.

## Control Flow

The method requires at least one backslash separator. It opens the containing directory with list/traverse/synchronize access and synchronous directory options, then queries entries matching the final component.

## State And Persistence Behavior

No persistent mutation. Returned entries may later be cached in `OpenSearch` for SMB1 find-next.

## Dependencies And Integration Points

Uses `INTFileStore.CreateFile`, `QueryDirectory`, `FileInformationClass`, and `SecurityContext`.

## Risks And Edge Cases

Patterns without a slash return invalid parameter. Directory handles are temporary, so very large searches are materialized into a list before pagination. Access and sharing conflicts can stop enumeration.

## Test Signals

Test `\dir\*`, exact file, wildcard prefixes, malformed patterns, unsupported information classes through callers, and handle closure after query.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryDirectory.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryFileSystem.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryFileSystem.cs

## Purpose

Partial SMB1 helper for querying filesystem information and converting it to SMB1 transaction2 query levels.

## Important APIs, Types, And Functions

`GetFileSystemInformation` maps `QueryFSInformationLevel` to `FileSystemInformationClass`, calls `fileStore.GetFileSystemInformation`, converts through `QueryFSInformationHelper`, and returns an NT status.

## Control Flow

Unsupported SMB1 levels are caught and mapped to `STATUS_OS2_INVALID_LEVEL`; file-store failure statuses pass through.

## State And Persistence Behavior

Read-only filesystem metadata query.

## Dependencies And Integration Points

Depends on `INTFileStore`, `QueryFSInformationHelper`, and filesystem information classes.

## Risks And Edge Cases

Conversion may lose information compared with passthrough classes. The helper does not enforce share read permissions; callers must do that.

## Test Signals

Test each supported level, unsupported level status, file-store failure propagation, and conversion of volume/size/device/attribute fields.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.QueryFileSystem.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.Set.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.Set.cs

## Purpose

Partial SMB1 helper for converting SMB1 set-information payloads to NT file information and applying them to an existing handle.

## Important APIs, Types, And Functions

`SetFileInformation` calls `SetInformationHelper.ToFileInformation` and then `fileStore.SetFileInformation`.

## Control Flow

There is no additional validation in this wrapper; parse/conversion exceptions are handled by callers such as transaction2 set-file-information.

## State And Persistence Behavior

Mutates persistent file metadata through the file store.

## Dependencies And Integration Points

Depends on `SetInformation`, `SetInformationHelper`, `FileInformation`, and `INTFileStore`.

## Risks And Edge Cases

Caller must catch unsupported/malformed levels and enforce write access. This wrapper assumes the handle is valid for the requested set operation.

## Test Signals

Test conversion for basic, disposition, rename, allocation/end-of-file levels, unsupported levels, and file-store status propagation.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.Set.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.cs

## Purpose

Partial SMB1 file-store helper for create/delete/rename/check/query/set operations built on NT create and set-info primitives.

## Important APIs, Types, And Functions

Methods include `CreateDirectory`, `DeleteDirectory`, `DeleteFile`, `Delete`, `Rename`, `CheckDirectory`, `QueryInformation`, `SetInformation`, `SetInformation2`, and `GetFileAttributes`.

## Control Flow

Most helpers open a path with the required access/disposition/options, perform one metadata operation, then close. Delete sets `FileDispositionInformation.DeletePending`; rename sets `FileRenameInformationType2`; set-info builds `FileBasicInformation`.

## State And Persistence Behavior

Mutates persistent filesystem state for create, delete, rename, and attribute/time updates. Temporary handles are closed before return.

## Dependencies And Integration Points

Depends on `INTFileStore`, NT file information structures, access masks, create options/dispositions, and `SecurityContext`.

## Risks And Edge Cases

Delete and rename rely on delete access and share-delete semantics; conflicts surface as file-store statuses. `SetInformation` only maps hidden/read-only/archive and last-write time, omitting other SMB attributes. `CheckDirectory` opens with zero access, which may vary by backend.

## Test Signals

Test create existing, delete file versus directory, delete-on-close, rename directory/file cases, check-directory errors, query info close behavior, and attribute mapping.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SessionSetupHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SessionSetupHelper.cs

## Purpose

Handles SMB1 session setup for classic NTLM challenge/response and extended-security GSS/NTLM blobs.

## Important APIs, Types, And Functions

`GetSessionSetupResponse` authenticates classic `SessionSetupAndXRequest`; `GetSessionSetupResponseExtended` accepts security blobs and supports multi-step authentication; `CreateAuthenticateMessage` builds an NTLM authenticate message from legacy password fields.

## Control Flow

Classic setup constructs an authenticate message, calls `NTLMAuthenticate`, fetches session attributes, truncates session key to 16 bytes, creates a normal or guest session, sets UID, and records large read/write capabilities. Extended setup calls `AcceptSecurityContext`, allocates a UID even for more-processing-required, and creates the session on final success.

## State And Persistence Behavior

Mutates connection authentication context, creates `SMB1Session` entries, sets connection large-read/write flags, and stores session key/access token in session security context.

## Dependencies And Integration Points

Depends on `GSSProvider`, NTLM message utilities, SMB1 session setup structures, and `SMB1ConnectionState`.

## Risks And Edge Cases

The code assumes authentication context attributes are present when logging failures. UID allocation during extended multi-step auth can reserve ids before success. Guest fallback depends on provider attributes.

## Test Signals

Test classic success/failure, guest login, extended continue and final success, session key truncation, large read/write flags, UID exhaustion, and malformed password/blob inputs.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SessionSetupHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/Transaction2SubcommandHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/Transaction2SubcommandHelper.cs

## Purpose

Implements SMB1 Transaction2 subcommands for directory search, filesystem query/set, path query, file query, and file set information.

## Important APIs, Types, And Functions

`GetSubcommandResponse` overloads handle FindFirst2, FindNext2, QueryFSInformation, SetFSInformation, QueryPathInformation, QueryFileInformation, and SetFileInformation.

## Control Flow

FindFirst queries and caches all entries in `OpenSearch`, returns a segment, and optionally closes at EOS. FindNext pages from cached entries and removes the search at end. Query/set methods choose passthrough or SMB1 information-level conversion, enforce share access, truncate responses to `maxDataCount` with `STATUS_BUFFER_OVERFLOW`, and delegate to file-store helpers.

## State And Persistence Behavior

Mutates open-search state and persistent file/filesystem metadata for set operations. Query operations read backing file-store state.

## Dependencies And Integration Points

Depends on Transaction2 command classes, `SMB1FileStoreHelper`, `FindInformationHelper`, `FileInformation`, `FileSystemInformation`, shares, sessions, and file stores.

## Risks And Edge Cases

Find results are fully materialized and cached, so large directories can consume memory and become stale. `returnResumeKeys` is computed but unused. Access checks are share-type dependent. Buffer overflow truncates response bytes without all callers necessarily expecting partial structures.

## Test Signals

Test find pagination and close flags, invalid SID, unsupported levels, passthrough versus legacy levels, buffer overflow truncation, access denied, malformed set buffers, and file-store status propagation.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/Transaction2SubcommandHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionHelper.cs

## Purpose

Assembles, dispatches, and fragments SMB1 Transaction and Transaction2 requests and responses.

## Important APIs, Types, And Functions

`GetTransactionResponse` overloads handle primary and secondary transaction packets. `GetCompleteTransactionResponse` dispatches named-pipe transaction subcommands. `GetCompleteTransaction2Response` dispatches Transaction2 subcommands. The final overload fragments response setup/parameters/data into one or more response commands.

## Control Flow

Primary packets with incomplete parameter/data payloads allocate process state and return interim. Secondary packets copy fragments by displacement and return no command until complete. Complete transactions parse subcommands, set header status, build subcommand response data, and fragment when calculated response size exceeds `MaxBufferSize`.

## State And Persistence Behavior

Uses connection process-state assembly and open-search/file-store state through subcommand helpers. Named-pipe and filesystem operations are delegated.

## Dependencies And Integration Points

Depends on SMB1 transaction classes, `ProcessStateObject`, `TransactionSubcommandHelper`, `Transaction2SubcommandHelper`, and `INTFileStore` via shares.

## Risks And Edge Cases

Fragment assembly keyed only by PID is fragile for concurrent transactions. Duplicate/overlapping fragments can overcount received bytes. Response fragmentation primarily splits data, with parameters sent in the first response only. RAP/LANMAN requests are explicitly not implemented.

## Test Signals

Test primary-only and multi-secondary assembly, invalid parse status, unsupported subcommands, transaction2 dispatch, max-buffer fragmentation, zero-length parameters/data, and PID collision behavior.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionSubcommandHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionSubcommandHelper.cs

## Purpose

Implements SMB1 Transaction named-pipe subcommands that are supported outside Transaction2.

## Important APIs, Types, And Functions

`GetSubcommandResponse` handles `TRANS_TRANSACT_NMPIPE` by issuing `FSCTL_PIPE_TRANSCEIVE`; `ProcessSubcommand` handles `TRANS_WAIT_NMPIPE` by issuing `FSCTL_PIPE_WAIT`.

## Control Flow

TransactNamedPipe validates FID, sends write data to `DeviceIOControl`, accepts success or buffer overflow, and returns read data. WaitNamedPipe validates `\PIPE\` naming, builds a `PipeWaitRequest`, and calls `DeviceIOControl` without a file handle.

## State And Persistence Behavior

Named-pipe state lives in the file store or pipe service. The helper only reads open-file state for transceive.

## Dependencies And Integration Points

Depends on transaction named-pipe command classes, `PipeWaitRequest`, `IoControlCode`, `SMB1Session`, and `INTFileStore.DeviceIOControl`.

## Risks And Edge Cases

If the wait name does not start with `\PIPE\`, the method sets invalid status but continues to `Substring(6)`, which can throw or use a bad pipe name. Transceive requires a valid FID and does not enforce share-specific access checks here.

## Test Signals

Test named-pipe transceive success, buffer overflow, invalid FID, invalid wait-name short string, wait timeout propagation, and unsupported pipe operations in `TransactionHelper`.

Source-read signal: reviewed the complete local source file for this item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/TransactionSubcommandHelper.cs -->
