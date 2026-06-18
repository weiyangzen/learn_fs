# Research: subset-b-010020

Grouped research for SMBLibrary SMB2 client, DFS referral, NT file-store enum, metadata, filesystem, IOCTL, and ACE files. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2Client.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2Client.cs

## Purpose
`SMB2Client` is the stateful SMB2/SMB3 client transport and session manager. It opens Direct TCP or NetBIOS-over-TCP connections, negotiates dialects through SMB 3.1.1, authenticates, tracks credits, signs or encrypts traffic, and exposes high-level share operations.

## Important APIs, Types, And Functions
Important public APIs are constructors, `Connect`, `Disconnect`, `Login`, `Logoff`, `ListShares`, `TreeConnect`, `Echo`, `MaxTransactSize`, `MaxReadSize`, `MaxWriteSize`, `Transport`, and `IsConnected`. Internal integration points include `TrySendCommand`, `WaitForCommand`, and `WaitForSessionResponsePacket`.

## Control Flow
Connection setup resolves or receives an address, opens a socket, optionally performs NetBIOS session establishment, sends `NegotiateRequest`, and records dialect, security blob, signing requirement, maximum sizes, and SMB 3.1.1 preauth state. Login drives an authentication client through one or more `SessionSetupRequest` exchanges, then derives signing/encryption keys. Receive callbacks dequeue NetBIOS session packets, decrypt SMB3 transform packets when needed, parse SMB2 responses, update preauth hash and credits, verify signatures, and signal waiting callers by message ID.

## State And Persistence Behavior
State includes socket/receive buffer ownership, incoming command queue, wait handles, server name, message ID, session ID, negotiated dialect, available credits, signing/encryption keys, preauth hash, authentication blobs, and connection/login booleans. Persistence is network session state only; the class does not write repository or local files.

## Dependencies And Integration Points
Depends on `SMBLibrary.SMB2` packet classes, NetBIOS session packets, socket async receive APIs, `IAuthenticationClient`/NTLM authentication, `SMB2Cryptography`, `ServerServiceHelper`, and `SMB2FileStore` returned from tree connect.

## Risks
Credit accounting is shared mutable state and is not guarded for multiple concurrent request senders. Receive callback disposal races can leave waiters timing out. `Random` is used for SMB 3.1.1 salt rather than a cryptographic RNG. Signature verification is skipped for interim async responses by design, and encrypted sessions bypass header signing. Timeout paths return null rather than rich errors, so callers must map them carefully.

## Test Signals
Signals include integration tests against SMB2/SMB3 servers for Direct TCP and NetBIOS, dialect negotiation including SMB 3.1.1, NTLM login success/failure, signed and encrypted tree connects, credit exhaustion and multi-credit reads/writes, response timeout, invalid signature rejection, and share enumeration through IPC$.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2Client.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2FileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2FileStore.cs

## Purpose
`SMB2FileStore` adapts an authenticated SMB2 tree connection to the `ISMBFileStore` API for open, close, read, write, query, set, security, FSCTL, and tree disconnect operations.

## Important APIs, Types, And Functions
Important methods are `CreateFile`, `CloseFile`, `ReadFile`, `WriteFile`, `FlushFileBuffers`, `QueryDirectory`, `GetFileInformation`, `SetFileInformation`, `GetFileSystemInformation`, `GetSecurityInformation`, `SetSecurityInformation`, `DeviceIOControl`, `Disconnect`, and `MaxReadSize`/`MaxWriteSize`. Lock, unlock, notify, cancel, and filesystem-set operations currently throw `NotImplementedException`.

## Control Flow
Each operation builds the matching SMB2 request, assigns the tree ID, calculates credit charge for large read/write/query/ioctl buffers, sends through `SMB2Client.TrySendCommand`, waits by message ID, extracts typed response payloads on success, and maps missing responses to timeout or invalid-SMB status. Directory queries loop until the server stops returning `STATUS_SUCCESS` pages.

## State And Persistence Behavior
Persistent state is limited to the client reference, tree ID, and share encryption flag. File handles are SMB2 `FileID` objects returned by create/open and supplied by callers on later operations.

## Dependencies And Integration Points
Depends on SMB2 request/response classes, NT file-store structures (`FileInformation`, `FileSystemInformation`, `SecurityDescriptor`), and `SMB2Client` transport/session state. It is the client-side implementation behind `TreeConnect`.

## Risks
Several `INTFileStore` capabilities are absent. Query output buffers are fixed at 4096 for many information classes and may truncate larger descriptors. `GetFileSystemInformation` opens the share root and always closes it afterward, so failure between open and close would leak a remote handle. Credit charge calculation assumes 64 KiB credit units and that client max sizes are negotiated correctly.

## Test Signals
Test through SMB2 file lifecycle flows: create/open dispositions, large multi-credit reads and writes, paged directory enumeration, QueryInfo and SetInfo round trips, security descriptor query/set, IOCTL success and buffer overflow responses, encrypted share operation, and timeout/disconnect behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2FileStore.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntry.cs

## Purpose
Defines the abstract base for DFS referral entry encoders and decoders.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntry class. Fields include none declared. Direct methods: WriteBytes, ReadEntry.

## Control Flow
`ReadEntry` peeks at the referral version in the buffer and dispatches to V1, V2, V3, or V4 constructors, while subclasses provide `WriteBytes`, `Length`, and `StringsLength`.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV1.cs

## Purpose
Models `[MS-DFSC] DFS_REFERRAL_V1`, an older referral entry containing a server type, flags, and inline UTF-16 share name.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV1 class. Fields include FixedLength:int, VersionNumber:ushort, Size:ushort, ServerType:DfsServerType, ReferralEntryFlags:DfsReferralEntryFlags, ShareName:string. Direct methods: DfsReferralEntryV1, WriteBytes.

## Control Flow
The constructor reads fixed header fields and a null-terminated share name at offset 8. `WriteBytes` writes the header plus inline share name and reports a total length of fixed bytes plus the UTF-16 terminator.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV1.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV2.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV2.cs

## Purpose
Models `[MS-DFSC] DFS_REFERRAL_V2`, with proximity, TTL, DFS path, alternate path, and target network address.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV2 class. Fields include FixedLength:int, VersionNumber:ushort, Size:ushort, ServerType:DfsServerType, ReferralEntryFlags:DfsReferralEntryFlags, Proximity:uint, TimeToLive:uint, DfsPath:string, DfsAlternatePath:string, NetworkAddress:string. Direct methods: DfsReferralEntryV2, WriteBytes.

## Control Flow
The constructor reads fixed fields and three offsets relative to the entry start, then decodes referenced UTF-16 strings. `WriteBytes` lays the fixed entry first, writes relative string offsets, then writes the three null-terminated strings into the shared trailing string area.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV2.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV3.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV3.cs

## Purpose
Models `[MS-DFSC] DFS_REFERRAL_V3`, supporting normal referrals and NameListReferral entries used for SYSVOL/NETLOGON expansion.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV3 class. Fields include FixedLength:int, VersionNumber:ushort, Size:ushort, ServerType:DfsServerType, ReferralEntryFlags:DfsReferralEntryFlags, TimeToLive:uint, DfsPath:string, DfsAlternatePath:string, NetworkAddress:string, ServiceSiteGuid:Guid, SpecialName:string, ExpandedNames:List<string>. Direct methods: DfsReferralEntryV3, WriteBytes.

## Control Flow
Normal entries read offsets for DFS path, alternate path, network address, and service-site GUID. Name-list entries read special-name and expanded-name-list offsets. `WriteBytes`, `Length`, `StringsLength`, and `IsNameListReferral` switch behavior based on `NameListReferral`.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV3.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV4.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV4.cs

## Purpose
Models DFS referral V4 as a V3-compatible entry with target-set boundary flag support.

## Important APIs, Types, And Functions
Direct types: DfsReferralEntryV4 class. Fields include none declared. Direct methods: DfsReferralEntryV4.

## Control Flow
The class inherits V3 parsing/writing and sets `VersionNumber = 4`; `IsTargetSetBoundary` exposes the V4-specific flag as a boolean property over `ReferralEntryFlags`.

## State And Persistence Behavior
State is a mutable in-memory representation of one referral entry. Persistence occurs only when the entry is serialized into a DFS referral response buffer.

## Dependencies And Integration Points
Depends on little-endian helpers, UTF-16 string helpers, DFS referral enums, and `ResponseGetDfsReferral` for list assembly and parsing.

## Risks
Risks are mostly bounds and offset related: malformed buffers can point string offsets outside the packet, nullable strings are not guarded on serialization, and V3/V4 behavior depends on correctly interpreting flag combinations.

## Test Signals
Round-trip tests should cover each version, normal and name-list V3, V4 target-set-boundary flag, bad version dispatch, relative string offsets, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/DfsReferralEntryV4.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsReferralEntryFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsReferralEntryFlags.cs

## Purpose
Defines the wire-level `DfsReferralEntryFlags` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include None = 0x0000, NameListReferral = 0x0002, TargetSetBoundary = 0x0004. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsReferralEntryFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsReferralHeaderFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsReferralHeaderFlags.cs

## Purpose
Defines the wire-level `DfsReferralHeaderFlags` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include ReferralServers = 0x00000001, StorageServers = 0x00000002, TargetFailback = 0x00000004. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsReferralHeaderFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsServerType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsServerType.cs

## Purpose
Defines the wire-level `DfsServerType` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include NonRoot = 0x0000, Root = 0x0001. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/DfsServerType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/RequestGetDfsReferralExFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/RequestGetDfsReferralExFlags.cs

## Purpose
Defines the wire-level `RequestGetDfsReferralExFlags` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include SiteName = 0x0001. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/Enums/RequestGetDfsReferralExFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferral.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferral.cs

## Purpose
Represents the legacy `REQ_GET_DFS_REFERRAL` request payload with maximum referral level and requested UNC path.

## Important APIs, Types, And Functions
Direct types: RequestGetDfsReferral class. Fields include MaxReferralLevel:ushort, RequestFileName:string. Direct methods: RequestGetDfsReferral, GetBytes.

## Control Flow
The byte constructor reads `MaxReferralLevel` and then decodes the remaining UTF-16 request file name. `GetBytes` writes the level followed by UTF-16 path bytes.

## State And Persistence Behavior
The class is a transient packet model. It stores parsed fields and serializes them to byte arrays but does not retain global state or write files.

## Dependencies And Integration Points
Used by DFS referral helpers over SMB IOCTL/FSCTL paths. Depends on UTF-16 helpers, little-endian helpers, referral enums, and referral entry subclasses.

## Risks
Length and offset validation are the critical risks. The request classes assume well-formed UTF-16 sizes; the response parser validates header presence but still relies on entry constructors for deeper string-offset safety.

## Test Signals
Test with known referral request/response byte fixtures, optional site-name requests, zero-referral responses, multi-entry mixed-version responses, and deliberately truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferral.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferralEx.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferralEx.cs

## Purpose
Represents `REQ_GET_DFS_REFERRAL_EX`, adding flags, request file-name length, and optional site-name data to the basic DFS referral request.

## Important APIs, Types, And Functions
Direct types: RequestGetDfsReferralEx class. Fields include MaxReferralLevel:ushort, Flags:RequestGetDfsReferralExFlags, RequestFileName:string, SiteName:string. Direct methods: RequestGetDfsReferralEx, GetBytes.

## Control Flow
The byte constructor reads max referral level, flags, request-name length, request name, and optional null-terminated site name when the site flag is set. `GetBytes` mirrors that layout and includes a site-name terminator when present.

## State And Persistence Behavior
The class is a transient packet model. It stores parsed fields and serializes them to byte arrays but does not retain global state or write files.

## Dependencies And Integration Points
Used by DFS referral helpers over SMB IOCTL/FSCTL paths. Depends on UTF-16 helpers, little-endian helpers, referral enums, and referral entry subclasses.

## Risks
Length and offset validation are the critical risks. The request classes assume well-formed UTF-16 sizes; the response parser validates header presence but still relies on entry constructors for deeper string-offset safety.

## Test Signals
Test with known referral request/response byte fixtures, optional site-name requests, zero-referral responses, multi-entry mixed-version responses, and deliberately truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/RequestGetDfsReferralEx.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/ResponseGetDfsReferral.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/DFS/ResponseGetDfsReferral.cs

## Purpose
Represents `RESP_GET_DFS_REFERRAL`, the DFS response header and ordered list of versioned referral entries.

## Important APIs, Types, And Functions
Direct types: ResponseGetDfsReferral class. Fields include HeaderSize:int, MinReferralEntryHeaderSize:int, PathConsumed:ushort, ReferralHeaderFlags:DfsReferralHeaderFlags, ReferralEntries:List<DfsReferralEntry>. Direct methods: ResponseGetDfsReferral, GetBytes.

## Control Flow
Parsing reads `PathConsumed`, referral count, header flags, then loops through `DfsReferralEntry.ReadEntry` while validating that entry headers fit. Serialization computes fixed-entry length first, then trailing string area, writes the header, and asks each entry to serialize itself with the current string offset.

## State And Persistence Behavior
The class is a transient packet model. It stores parsed fields and serializes them to byte arrays but does not retain global state or write files.

## Dependencies And Integration Points
Used by DFS referral helpers over SMB IOCTL/FSCTL paths. Depends on UTF-16 helpers, little-endian helpers, referral enums, and referral entry subclasses.

## Risks
Length and offset validation are the critical risks. The request classes assume well-formed UTF-16 sizes; the response parser validates header presence but still relies on entry constructors for deeper string-offset safety.

## Test Signals
Test with known referral request/response byte fixtures, optional site-name requests, zero-referral responses, multi-entry mixed-version responses, and deliberately truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/DFS/ResponseGetDfsReferral.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/NTStatus.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Enums/NTStatus.cs

## Purpose
Defines the wire-level `NTStatus` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include STATUS_SUCCESS = 0x00000000, STATUS_PENDING = 0x00000103, STATUS_NOTIFY_CLEANUP = 0x0000010B, STATUS_NOTIFY_ENUM_DIR = 0x0000010C, SEC_I_CONTINUE_NEEDED = 0x00090312, STATUS_OBJECT_NAME_EXISTS = 0x40000000, STATUS_BUFFER_OVERFLOW = 0x80000005, STATUS_NO_MORE_FILES = 0x80000006, SEC_E_SECPKG_NOT_FOUND = 0x80090305, SEC_E_INVALID_TOKEN = 0x80090308, STATUS_NOT_IMPLEMENTED = 0xC0000002, STATUS_INVALID_INFO_CLASS = 0xC0000003, STATUS_INFO_LENGTH_MISMATCH = 0xC0000004, STATUS_INVALID_HANDLE = 0xC0000008, STATUS_INVALID_PARAMETER = 0xC000000D, STATUS_NO_SUCH_DEVICE = 0xC000000E, STATUS_NO_SUCH_FILE = 0xC000000F, STATUS_INVALID_DEVICE_REQUEST = 0xC0000010, STATUS_END_OF_FILE = 0xC0000011, STATUS_MORE_PROCESSING_REQUIRED = 0xC0000016, STATUS_ACCESS_DENIED = 0xC0000022, STATUS_BUFFER_TOO_SMALL = 0xC0000023, STATUS_OBJECT_NAME_INVALID = 0xC0000033, STATUS_OBJECT_NAME_NOT_FOUND = 0xC0000034, STATUS_OBJECT_NAME_COLLISION = 0xC0000035, STATUS_OBJECT_PATH_INVALID = 0xC0000039, STATUS_OBJECT_PATH_NOT_FOUND = 0xC000003A, STATUS_OBJECT_PATH_SYNTAX_BAD = 0xC000003B, STATUS_DATA_ERROR = 0xC000003E, STATUS_SHARING_VIOLATION = 0xC0000043, STATUS_FILE_LOCK_CONFLICT = 0xC0000054, STATUS_LOCK_NOT_GRANTED = 0xC0000055, STATUS_DELETE_PENDING = 0xC0000056, STATUS_IO_TIMEOUT = 0xC00000B5, STATUS_PRIVILEGE_NOT_HELD = 0xC0000061, STATUS_WRONG_PASSWORD = 0xC000006A, STATUS_LOGON_FAILURE = 0xC000006D, STATUS_ACCOUNT_RESTRICTION = 0xC000006E, STATUS_INVALID_LOGON_HOURS = 0xC000006F, STATUS_INVALID_WORKSTATION = 0xC0000070. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/NTStatus.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/SMBTransportType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Enums/SMBTransportType.cs

## Purpose
Defines the wire-level `SMBTransportType` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include NetBiosOverTCP, DirectTCPTransport. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/SMBTransportType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/Win32Error.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Enums/Win32Error.cs

## Purpose
Defines the wire-level `Win32Error` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include ERROR_SUCCESS = 0x0000, ERROR_ACCESS_DENIED = 0x0005, ERROR_SHARING_VIOLATION = 0x0020, ERROR_NOT_SUPPORTED = 0x0032, ERROR_INVALID_PARAMETER = 0x0057, ERROR_DISK_FULL = 0x0070, ERROR_INVALID_NAME = 0x007B, ERROR_INVALID_LEVEL = 0x007C, ERROR_DIR_NOT_EMPTY = 0x0091, ERROR_BAD_PATHNAME = 0x00A1, ERROR_ALREADY_EXISTS = 0x00B7, ERROR_NO_TOKEN = 0x03F0, ERROR_LOGON_FAILURE = 0x052E, ERROR_ACCOUNT_RESTRICTION = 0x052F, ERROR_INVALID_LOGON_HOURS = 0x0530, ERROR_INVALID_WORKSTATION = 0x0531, ERROR_PASSWORD_EXPIRED = 0x0532, ERROR_ACCOUNT_DISABLED = 0x0533, ERROR_LOGON_TYPE_NOT_GRANTED = 0x0569, ERROR_ACCOUNT_EXPIRED = 0x0701, ERROR_PASSWORD_MUST_CHANGE = 0x0773, ERROR_ACCOUNT_LOCKED_OUT = 0x0775, NERR_NetNameNotFound = 0x0906. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Enums/Win32Error.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Exceptions/UnsupportedInformationLevelException.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Exceptions/UnsupportedInformationLevelException.cs

## Purpose
`UnsupportedInformationLevelException` is a focused exception for unsupported SMB/NT information class requests.

## Important APIs, Types, And Functions
It exposes the default `Exception` constructor and a message constructor.

## Control Flow
There is no custom control flow beyond base exception construction.

## State And Persistence Behavior
No mutable state beyond standard exception fields.

## Dependencies And Integration Points
Thrown by file-information and filesystem-information factories when a requested class has no implementation.

## Risks
Risk is inconsistent mapping from this exception to SMB status codes by callers.

## Test Signals
Test unsupported information-class requests through factories and server/client query paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Exceptions/UnsupportedInformationLevelException.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Helpers/FileTimeHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Helpers/FileTimeHelper.cs

## Purpose
`FileTimeHelper` centralizes conversion between Windows FILETIME wire integers and .NET `DateTime`/`SetFileTime` values for SMB file metadata.

## Important APIs, Types, And Functions
Important APIs include `ReadFileTimeSafe`, `ReadFileTime`, nullable read/write overloads, `WriteFileTime`, `ReadSetFileTime`, and `WriteSetFileTime`.

## Control Flow
Readers pull little-endian signed 64-bit FILETIME values from buffers and convert to UTC `DateTime`; safe reads clamp values above .NET's maximum. Nullable helpers map zero to null. `SetFileTime` helpers preserve the special no-change sentinel.

## State And Persistence Behavior
No retained state beyond constants for the Windows epoch minimum and .NET maximum FILETIME. Persistence is only the serialized timestamp fields in SMB structures.

## Dependencies And Integration Points
Used by file and filesystem information structures, especially basic/network-open/volume metadata and set-info timestamps.

## Risks
Timestamp edge cases are easy to mishandle: pre-1601 values, null/zero, max-value clamping, local-vs-UTC confusion, and the `SetFileTime` no-change sentinel need explicit coverage.

## Test Signals
Use boundary tests for zero, 1601-01-01 UTC, normal values, `DateTime.MaxValue`, over-max safe reads, nullable writes, and `SetFileTime.MustNotChange` round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Helpers/FileTimeHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Helpers/SP800_1008.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Helpers/SP800_1008.cs

## Purpose
`SP800_1008` implements the NIST SP 800-108 counter-mode key derivation function variant used by SMB2/SMB3 cryptographic key derivation.

## Important APIs, Types, And Functions
Exports internal static `DeriveKey(HMAC hmac, byte[] label, byte[] context, int keyLengthInBits)`.

## Control Flow
For each counter block, it HMACs counter, label, zero separator, context, and requested key length in bits, appends the result, and finally truncates to the requested byte length.

## State And Persistence Behavior
It is stateless except for mutating/using the caller-supplied `HMAC` instance. The returned key is a new byte array.

## Dependencies And Integration Points
Called by SMB2 cryptography helpers to derive signing, encryption, and decryption keys from the session key and preauth context.

## Risks
The function assumes key length is byte-aligned and that the supplied HMAC is already keyed correctly. Reusing the same HMAC instance concurrently would be unsafe.

## Test Signals
Validate with known SP 800-108 vectors and SMB dialect-specific signing/encryption key derivation fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Helpers/SP800_1008.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/AccessMask.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/AccessMask.cs

## Purpose
Defines the wire-level `AccessMask` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include DELETE = 0x00010000, READ_CONTROL = 0x00020000, WRITE_DAC = 0x00040000, WRITE_OWNER = 0x00080000, SYNCHRONIZE = 0x00100000, ACCESS_SYSTEM_SECURITY = 0x01000000, MAXIMUM_ALLOWED = 0x02000000, GENERIC_ALL = 0x10000000, GENERIC_EXECUTE = 0x20000000, GENERIC_WRITE = 0x40000000, GENERIC_READ = 0x80000000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/AccessMask.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/DirectoryAccessMask.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/DirectoryAccessMask.cs

## Purpose
Defines the wire-level `DirectoryAccessMask` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include FILE_LIST_DIRECTORY = 0x00000001, FILE_ADD_FILE = 0x00000002, FILE_ADD_SUBDIRECTORY = 0x00000004, FILE_READ_EA = 0x00000008, FILE_WRITE_EA = 0x00000010, FILE_TRAVERSE = 0x00000020, FILE_DELETE_CHILD = 0x00000040, FILE_READ_ATTRIBUTES = 0x00000080, FILE_WRITE_ATTRIBUTES = 0x00000100, DELETE = 0x00010000, READ_CONTROL = 0x00020000, WRITE_DAC = 0x00040000, WRITE_OWNER = 0x00080000, SYNCHRONIZE = 0x00100000, ACCESS_SYSTEM_SECURITY = 0x01000000, MAXIMUM_ALLOWED = 0x02000000, GENERIC_ALL = 0x10000000, GENERIC_EXECUTE = 0x20000000, GENERIC_WRITE = 0x40000000, GENERIC_READ = 0x80000000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/DirectoryAccessMask.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/FileAccessMask.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/FileAccessMask.cs

## Purpose
Defines the wire-level `FileAccessMask` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include FILE_READ_DATA = 0x00000001, FILE_WRITE_DATA = 0x00000002, FILE_APPEND_DATA = 0x00000004, FILE_READ_EA = 0x00000008, FILE_WRITE_EA = 0x00000010, FILE_EXECUTE = 0x00000020, FILE_DELETE_CHILD = 0x00000040, FILE_READ_ATTRIBUTES = 0x00000080, FILE_WRITE_ATTRIBUTES = 0x00000100, DELETE = 0x00010000, READ_CONTROL = 0x00020000, WRITE_DAC = 0x00040000, WRITE_OWNER = 0x00080000, SYNCHRONIZE = 0x00100000, ACCESS_SYSTEM_SECURITY = 0x01000000, MAXIMUM_ALLOWED = 0x02000000, GENERIC_ALL = 0x10000000, GENERIC_EXECUTE = 0x20000000, GENERIC_WRITE = 0x40000000, GENERIC_READ = 0x80000000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/AccessMask/FileAccessMask.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/CompressionFormat.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/CompressionFormat.cs

## Purpose
Defines the wire-level `CompressionFormat` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include COMPRESSION_FORMAT_NONE = 0x0000, COMPRESSION_FORMAT_DEFAULT = 0x0001, COMPRESSION_FORMAT_LZNT1 = 0x0002. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/CompressionFormat.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/ExtendedAttributeFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/ExtendedAttributeFlags.cs

## Purpose
Defines the wire-level `ExtendedAttributeFlags` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include FILE_NEED_EA = 0x80. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/ExtendedAttributeFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileAttributes.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileAttributes.cs

## Purpose
Defines the wire-level `FileAttributes` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include ReadOnly = 0x00000001, Hidden = 0x00000002, System = 0x00000004, Directory = 0x00000010, Archive = 0x00000020, Normal = 0x00000080, Temporary = 0x00000100, SparseFile = 0x00000200, ReparsePoint = 0x00000400, Compressed = 0x00000800, Offline = 0x00001000, NotContentIndexed = 0x00002000, Encrypted = 0x00004000, IntegrityStream = 0x00008000, NoScrubData = 0x00020000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileAttributes.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileInformationClass.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileInformationClass.cs

## Purpose
Defines the wire-level `FileInformationClass` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FileDirectoryInformation = 0x01, FileFullDirectoryInformation = 0x02, FileBothDirectoryInformation = 0x03, FileBasicInformation = 0x04, FileStandardInformation = 0x05, FileInternalInformation = 0x06, FileEaInformation = 0x07, FileAccessInformation = 0x08, FileNameInformation = 0x09, FileRenameInformation = 0x0A, FileLinkInformation = 0x0B, FileNamesInformation = 0x0C, FileDispositionInformation = 0x0D, FilePositionInformation = 0x0E, FileFullEaInformation = 0x0F, FileModeInformation = 0x10, FileAlignmentInformation = 0x11, FileAllInformation = 0x12, FileAllocationInformation = 0x13, FileEndOfFileInformation = 0x14, FileAlternateNameInformation = 0x15, FileStreamInformation = 0x16, FilePipeInformation = 0x17, FilePipeLocalInformation = 0x18, FilePipeRemoteInformation = 0x19, FileCompressionInformation = 0x1C, FileNetworkOpenInformation = 0x22, FileAttributeTagInformation = 0x23, FileIdBothDirectoryInformation = 0x25, FileIdFullDirectoryInformation = 0x26, FileValidDataLengthInformation = 0x27, FileShortNameInformation = 0x28. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileInformationClass.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceCharacteristics.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceCharacteristics.cs

## Purpose
Defines the wire-level `DeviceCharacteristics` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include RemovableMedia = 0x0001, ReadOnlyDevice = 0x0002, FloppyDiskette = 0x0004, WriteOnceMedia = 0x0008, RemoteDevice = 0x0010, IsMounted = 0x0020, VirtualVolume = 0x0040, SecureOpen = 0x0100, TerminalServicesDevice = 0x1000, WebDAVDevice = 0x2000, PortableDevice = 0x4000, AllowAppContainerTraversal = 0x20000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceCharacteristics.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceType.cs

## Purpose
Defines the wire-level `DeviceType` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include Beep = 0x0001, CDRom = 0x0002, CDRomFileSystem = 0x0003, Controller = 0x0004, DataLink = 0x0005, DFS = 0x0006, Disk = 0x0007, DiskFileSystem = 0x0008, FileSystem = 0x0009, ImportPort = 0x000A, Keyboard = 0x000B, MailSlot = 0x000C, MidiIn = 0x000D, MidiOut = 0x000E, Mouse = 0x000F, MultiUNCProvider = 0x0010, NamedPipe = 0x0011, Network = 0x0012, NetworkBrowser = 0x0013, NetworkFileSystem = 0x0014, Null = 0x0015, ParallelPort = 0x0016, PhysicalNetcard = 0x0017, Printer = 0x0018, Scanner = 0x0019, SerialMousePort = 0x001A, SerialPort = 0x001B, Screen = 0x001C, Sound = 0x001D, Streams = 0x001E, Tape = 0x001F, TapeFileSystem = 0x0020, Transport = 0x0021, Unknown = 0x0022, Video = 0x0023, VirtualDisk = 0x0024, WaveIn = 0x0025, WaveOut = 0x0026, PS2Port = 0x0027, NetworkRedirector = 0x0028. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemAttributes.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemAttributes.cs

## Purpose
Defines the wire-level `FileSystemAttributes` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include CaseSensitiveSearch = 0x0001, CasePreservedNames = 0x0002, UnicodeOnDisk = 0x0004, PersistentACLs = 0x0008, FileCompression = 0x0010, VolumeQuotas = 0x0020, SupportsSparseFiles = 0x0040, SupportsReparsePoints = 0x0080, SupportsRemoteStorage = 0x0100, ReturnsCleanupResultInfo = 0x0200, SupportsPOSIXUnlinkRename = 0x0400, VolumeIsCompressed = 0x8000, SupportsObjectIDs = 0x00010000, SupportsEncryption = 0x00020000, NamedStreams = 0x00040000, ReadOnlyVolume = 0x00080000, SequentialWriteOnce = 0x00100000, SupportsTransactions = 0x00200000, SupportsHardLinks = 0x00400000, SupportsExtendedAttributes = 0x00800000, SupportsOpenByFileID = 0x01000000, SupportsUSNJournal = 0x02000000, SupportsIntegrityStreams = 0x04000000, SupportsBlockRefCounting = 0x08000000, SupportsSparseVDL = 0x10000000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemAttributes.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemControlFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemControlFlags.cs

## Purpose
Defines the wire-level `FileSystemControlFlags` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include QuotaTrack = 0x00000001, QuotaEnforce = 0x00000002, ContentIndexingDisabled = 0x00000008, LogQuotaThreshold = 0x00000010, LogQuotaLimit = 0x00000020, LogVolumeThreshold = 0x00000040, LogVolumeLimit = 0x00000080, QuotasIncomplete = 0x00000100, QuotasRebuilding = 0x00000200. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemControlFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemInformationClass.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemInformationClass.cs

## Purpose
Defines the wire-level `FileSystemInformationClass` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FileFsVolumeInformation = 0x01, FileFsLabelInformation = 0x02, FileFsSizeInformation = 0x03, FileFsDeviceInformation = 0x04, FileFsAttributeInformation = 0x05, FileFsControlInformation = 0x06, FileFsFullSizeInformation = 0x07, FileFsObjectIdInformation = 0x08, FileFsDriverPathInformation = 0x09, FileFsVolumeFlagsInformation = 0x0A, FileFsSectorSizeInformation = 0x0B. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemInformationClass.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/SectorSizeInformationFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/SectorSizeInformationFlags.cs

## Purpose
Defines the wire-level `SectorSizeInformationFlags` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include AlignedDevice = 0x00000001, PartitionAlignedOnDevice = 0x00000002, NoSeekPenalty = 0x0000004, TrimEnabled = 0x00000008. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/SectorSizeInformationFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/IoControlCode.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/IoControlCode.cs

## Purpose
Defines the wire-level `IoControlCode` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FSCTL_DFS_GET_REFERRALS = 0x00060194, FSCTL_DFS_GET_REFERRALS_EX = 0x000601B0, FSCTL_IS_PATHNAME_VALID = 0x0009002C, FSCTL_GET_COMPRESSION = 0x0009003C, FSCTL_FILESYSTEM_GET_STATISTICS = 0x00090060, FSCTL_QUERY_FAT_BPB = 0x00090058, FSCTL_GET_NTFS_VOLUME_DATA = 0x00090064, FSCTL_GET_RETRIEVAL_POINTERS = 0x00090073, FSCTL_FIND_FILES_BY_SID = 0x0009008F, FSCTL_SET_OBJECT_ID = 0x00090098, FSCTL_GET_OBJECT_ID = 0x0009009C, FSCTL_DELETE_OBJECT_ID = 0x000900A0, FSCTL_SET_REPARSE_POINT = 0x000900A4, FSCTL_GET_REPARSE_POINT = 0x000900A8, FSCTL_DELETE_REPARSE_POINT = 0x000900AC, FSCTL_SET_OBJECT_ID_EXTENDED = 0x000900BC, FSCTL_CREATE_OR_GET_OBJECT_ID = 0x000900C0, FSCTL_SET_SPARSE = 0x000900C4, FSCTL_READ_FILE_USN_DATA = 0x000900EB, FSCTL_WRITE_USN_CLOSE_RECORD = 0x000900EF, FSCTL_QUERY_SPARING_INFO = 0x00090138, FSCTL_QUERY_ON_DISK_VOLUME_INFO = 0x0009013C, FSCTL_SET_ZERO_ON_DEALLOCATION = 0x00090194, FSCTL_QUERY_FILE_REGIONS = 0x00090284, FSCTL_QUERY_SHARED_VIRTUAL_DISK_SUPPORT = 0x00090300, FSCTL_SVHDX_SYNC_TUNNEL_REQUEST = 0x00090304, FSCTL_STORAGE_QOS_CONTROL = 0x00090350, FSCTL_SVHDX_ASYNC_TUNNEL_REQUEST = 0x00090364, FSCTL_QUERY_ALLOCATED_RANGES = 0x000940CF, FSCTL_OFFLOAD_READ = 0x00094264, FSCTL_SET_ZERO_DATA = 0x000980C8, FSCTL_SET_DEFECT_MANAGEMENT = 0x00098134, FSCTL_FILE_LEVEL_TRIM = 0x00098208, FSCTL_OFFLOAD_WRITE = 0x00098268, FSCTL_DUPLICATE_EXTENTS_TO_FILE = 0x00098344, FSCTL_SET_COMPRESSION = 0x0009C040, FSCTL_PIPE_WAIT = 0x00110018, FSCTL_PIPE_PEEK = 0x0011400C, FSCTL_PIPE_TRANSCEIVE = 0x0011C017, FSCTL_SRV_REQUEST_RESUME_KEY = 0x00140078. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/IoControlCode.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NotifyChangeFilter.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NotifyChangeFilter.cs

## Purpose
Defines the wire-level `NotifyChangeFilter` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include FileName = 0x0000001, DirName = 0x0000002, Attributes = 0x0000004, Size = 0x0000008, LastWrite = 0x000000010, LastAccess = 0x00000020, Creation = 0x00000040, EA = 0x00000080, Security = 0x00000100, StreamName = 0x00000200, StreamSize = 0x00000400, StreamWrite = 0x00000800. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NotifyChangeFilter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateDisposition.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateDisposition.cs

## Purpose
Defines the wire-level `CreateDisposition` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FILE_SUPERSEDE = 0x0000, FILE_OPEN = 0x0001, FILE_CREATE = 0x0002, FILE_OPEN_IF = 0x0003, FILE_OVERWRITE = 0x0004, FILE_OVERWRITE_IF = 0x0005. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateDisposition.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateOptions.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateOptions.cs

## Purpose
Defines the wire-level `CreateOptions` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include FILE_DIRECTORY_FILE = 0x00000001, FILE_WRITE_THROUGH = 0x00000002, FILE_SEQUENTIAL_ONLY = 0x00000004, FILE_NO_INTERMEDIATE_BUFFERING = 0x00000008, FILE_SYNCHRONOUS_IO_ALERT = 0x00000010, FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020, FILE_NON_DIRECTORY_FILE = 0x00000040, FILE_CREATE_TREE_CONNECTION = 0x00000080, FILE_COMPLETE_IF_OPLOCKED = 0x00000100, FILE_NO_EA_KNOWLEDGE = 0x00000200, FILE_OPEN_REMOTE_INSTANCE = 0x00000400, FILE_RANDOM_ACCESS = 0x00000800, FILE_DELETE_ON_CLOSE = 0x00001000, FILE_OPEN_BY_FILE_ID = 0x00002000, FILE_OPEN_FOR_BACKUP_INTENT = 0x00004000, FILE_NO_COMPRESSION = 0x00008000, FILE_OPEN_REQUIRING_OPLOCK = 0x00010000, FILE_DISALLOW_EXCLUSIVE = 0x00020000, FILE_RESERVE_OPFILTER = 0x00100000, FILE_OPEN_REPARSE_POINT = 0x00200000, FILE_OPEN_NO_RECALL = 0x00400000, FILE_OPEN_FOR_FREE_SPACE_QUERY = 0x00800000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/CreateOptions.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/FileStatus.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/FileStatus.cs

## Purpose
Defines the wire-level `FileStatus` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FILE_SUPERSEDED = 0x00000000, FILE_OPENED = 0x00000001, FILE_CREATED = 0x00000002, FILE_OVERWRITTEN = 0x00000003, FILE_EXISTS = 0x00000004, FILE_DOES_NOT_EXIST = 0x00000005. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/FileStatus.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/ShareAccess.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/ShareAccess.cs

## Purpose
Defines the wire-level `ShareAccess` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include None = 0x00000000, Read = 0x00000001, Write = 0x00000002, Delete = 0x00000004. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/NtCreateFile/ShareAccess.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/SecurityInformation/ImpersonationLevel.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/SecurityInformation/ImpersonationLevel.cs

## Purpose
Defines the wire-level `ImpersonationLevel` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include Anonymous = 0x00000000, Identification = 0x00000001, Impersonation = 0x00000002, Delegation = 0x00000003. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/SecurityInformation/ImpersonationLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/SecurityInformation/SecurityInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/SecurityInformation/SecurityInformation.cs

## Purpose
Defines the wire-level `SecurityInformation` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include OWNER_SECURITY_INFORMATION = 0x00000001, GROUP_SECURITY_INFORMATION = 0x00000002, DACL_SECURITY_INFORMATION = 0x00000004, SACL_SECURITY_INFORMATION = 0x00000008, LABEL_SECURITY_INFORMATION = 0x00000010, ATTRIBUTE_SECURITY_INFORMATION = 0x00000020, SCOPE_SECURITY_INFORMATION = 0x00000040, BACKUP_SECURITY_INFORMATION = 0x00010000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/SecurityInformation/SecurityInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/FileHandle.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/FileHandle.cs

## Purpose
`FileHandle` is a simple server-side handle container tying a logical path to a stream, directory flag, and delete-on-close behavior.

## Important APIs, Types, And Functions
Direct types: FileHandle class. Fields include Path:string, IsDirectory:bool, Stream:Stream, DeleteOnClose:bool.

## Control Flow
Construction stores the supplied path, directory bit, stream, and delete-on-close flag. Other file-store code uses the object as opaque handle state.

## State And Persistence Behavior
State is per-open-handle and persists only as long as the server keeps the handle object. It may own an open `Stream` that must be closed elsewhere.

## Dependencies And Integration Points
Integrated by NT file-store implementations that expose local or virtual files through SMB server operations.

## Risks
Risk centers on lifecycle ownership: streams must be closed exactly once and delete-on-close must be honored after all access checks and sharing rules.

## Test Signals
Test create/open/close flows, directory vs file handles, stream disposal, and delete-on-close cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/FileHandle.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/INTFileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/INTFileStore.cs

## Purpose
`INTFileStore` defines SMBLibrary's server-side NT file-store contract and the notify-completion delegate used by SMB1/SMB2 server paths.

## Important APIs, Types, And Functions
The interface covers file create/close/read/write/flush/lock/unlock, directory query, file and filesystem information get/set, security descriptor get/set, notify change, cancel, and device IO control.

## Control Flow
There is no implementation control flow here. SMB server command handlers call these methods to translate protocol requests into backend storage behavior.

## State And Persistence Behavior
The interface itself has no state. Implementations decide handle identity, persistence, async notify state, and backend storage lifetime.

## Dependencies And Integration Points
Implemented by stores such as `NamedPipeStore` and local NT file stores, and consumed by SMB1/SMB2 server command processors.

## Risks
All implementations must agree on opaque handle types, error mapping, sharing semantics, security behavior, and async notify/cancel contracts or protocol handlers will misbehave.

## Test Signals
Contract tests should run the same create/read/write/query/security/ioctl scenarios against each `INTFileStore` implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/INTFileStore.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NTFileStoreHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NTFileStoreHelper.cs

## Purpose
`NTFileStoreHelper` maps SMB/NT access masks and share modes to .NET file APIs and provides convenience queries for network-open information.

## Important APIs, Types, And Functions
Important APIs are `ToCreateFileAccess`, `ToFileAccess`, `ToFileShare`, and `GetNetworkOpenInformation` overloads for path or handle.

## Control Flow
Access conversion checks desired read/write/append bits and create disposition to choose .NET `FileAccess`. Share conversion maps SMB read/write/delete sharing to `FileShare`. Network-open helpers open or query a file through an `INTFileStore`, collect `FileNetworkOpenInformation`, and close temporary handles.

## State And Persistence Behavior
No global state. Temporary handles created for path-based queries must be closed before returning.

## Dependencies And Integration Points
Used by file-store implementations and server handlers that need to bridge SMB semantics with local .NET stream/file behavior.

## Risks
SMB generic access bits, append-only writes, overwrite dispositions, and delete sharing do not map perfectly to .NET flags. Helper-created handles can leak if future code adds throwing paths between open and close.

## Test Signals
Test access/share conversion matrices and `GetNetworkOpenInformation` success/failure/cleanup paths against real and fake stores.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NTFileStoreHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NamedPipeStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NamedPipeStore.cs

## Purpose
`NamedPipeStore` implements `INTFileStore` for IPC named pipes backed by in-process RPC `RemoteService` instances.

## Important APIs, Types, And Functions
Important methods include `CreateFile`, `CloseFile`, `ReadFile`, `WriteFile`, `DeviceIOControl`, `GetFileInformation`, and placeholder implementations for unsupported file-store operations.

## Control Flow
Create resolves a pipe path to a registered service and returns a stream-like handle. Read/write delegate to the pipe handle buffers. `DeviceIOControl` handles pipe wait and pipe transceive/control codes for RPC transport. Metadata queries synthesize file information suitable for named pipes; most filesystem, directory, security, notify, lock, and set operations return unsupported statuses.

## State And Persistence Behavior
State is the service list plus per-open pipe handles/service buffers. There is no disk persistence; data is transient RPC pipe traffic.

## Dependencies And Integration Points
Depends on `SMBLibrary.RPC`, `SMBLibrary.Services`, pipe IOCTL request structures, and the `INTFileStore` contract. It is exposed through IPC$-style server shares.

## Risks
Pipe semantics differ from disk files, so returning the wrong status for unsupported operations can break clients. Buffer ownership and max-output handling in transceive paths are protocol-sensitive.

## Test Signals
Exercise RPC bind/transceive flows, opening known and unknown pipes, close cleanup, read/write ordering, FSCTL_PIPE_WAIT, FSCTL_PIPE_TRANSCEIVE, and unsupported operation status codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NamedPipeStore.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/FileInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/FileInformation.cs

## Purpose
`FileInformation` is the abstract base for NT file information records used by SMB query/set-info operations.

## Important APIs, Types, And Functions
Subclasses implement `WriteBytes`, `FileInformationClass`, and `Length`; `GetBytes` allocates a correctly sized buffer; static `GetFileInformation` dispatches a buffer and class code to supported concrete record types.

## Control Flow
Callers parse a response by passing the wire buffer and `FileInformationClass`; the switch constructs the matching class or throws `UnsupportedInformationLevelException`/`NotImplementedException`. Serialization is delegated to the concrete subclass.

## State And Persistence Behavior
The base class has no state. Concrete instances carry parsed metadata until serialized or consumed.

## Dependencies And Integration Points
Used by SMB1/SMB2 QueryInfo/SetInfo handlers and client file-store APIs. It depends on all concrete file-information classes and the `FileInformationClass` enum.

## Risks
Unsupported classes throw at runtime, and the factory defaults to Type2 rename/link layouts. New information classes must update both enum and factory or query paths will fail.

## Test Signals
Factory coverage should instantiate every supported class from bytes and verify `GetBytes` round trips; unsupported classes should return the expected exception/status mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/FileInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAccessInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAccessInformation.cs

## Purpose
`FileAccessInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileAccessInformation class. Fields include FixedLength:int, AccessFlags:AccessMask. Direct methods include FileAccessInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAccessInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAlignmentInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAlignmentInformation.cs

## Purpose
`FileAlignmentInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileAlignmentInformation class. Fields include FixedLength:int, AlignmentRequirement:uint. Direct methods include FileAlignmentInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAlignmentInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAllInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAllInformation.cs

## Purpose
`FileAllInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileAllInformation class. Fields include BasicInformation:FileBasicInformation, StandardInformation:FileStandardInformation, InternalInformation:FileInternalInformation, EaInformation:FileEaInformation, AccessInformation:FileAccessInformation, PositionInformation:FilePositionInformation, ModeInformation:FileModeInformation, AlignmentInformation:FileAlignmentInformation, NameInformation:FileNameInformation. Direct methods include FileAllInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAllInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAlternateNameInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAlternateNameInformation.cs

## Purpose
`FileAlternateNameInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileAlternateNameInformation class. Fields include none declared. Direct methods include FileAlternateNameInformation.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAlternateNameInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAttributeTagInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAttributeTagInformation.cs

## Purpose
`FileAttributeTagInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileAttributeTagInformation class. Fields include FixedLength:int, FileAttributes:FileAttributes, ReparsePointTag:uint. Direct methods include FileAttributeTagInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileAttributeTagInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileBasicInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileBasicInformation.cs

## Purpose
`FileBasicInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileBasicInformation class. Fields include FixedLength:int, CreationTime:SetFileTime, LastAccessTime:SetFileTime, LastWriteTime:SetFileTime, ChangeTime:SetFileTime, FileAttributes:FileAttributes, Reserved:uint. Direct methods include FileBasicInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileBasicInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileCompressionInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileCompressionInformation.cs

## Purpose
`FileCompressionInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileCompressionInformation class. Fields include FixedLength:int, CompressedFileSize:long, CompressionFormat:CompressionFormat, CompressionUnitShift:byte, ChunkShift:byte, ClusterShift:byte, Reserved:byte[]. Direct methods include FileCompressionInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileCompressionInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileEaInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileEaInformation.cs

## Purpose
`FileEaInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileEaInformation class. Fields include FixedLength:int, EaSize:uint. Direct methods include FileEaInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileEaInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileFullEAEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileFullEAEntry.cs

## Purpose
`FileFullEAEntry` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileFullEAEntry class. Fields include FixedLength:int, NextEntryOffset:uint, Flags:ExtendedAttributeFlags, EaNameLength:byte, EaValueLength:ushort, EaName:string, EaValue:string. Direct methods include FileFullEAEntry, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileFullEAEntry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileFullEAInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileFullEAInformation.cs

## Purpose
`FileFullEAInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileFullEAInformation class. Fields include none declared. Direct methods include FileFullEAInformation, WriteBytes, ReadList, WriteList.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileFullEAInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileInternalInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileInternalInformation.cs

## Purpose
`FileInternalInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileInternalInformation class. Fields include FixedLength:int, IndexNumber:long. Direct methods include FileInternalInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileInternalInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileModeInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileModeInformation.cs

## Purpose
`FileModeInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileModeInformation class. Fields include FixedSize:int, FileMode:CreateOptions. Direct methods include FileModeInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileModeInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileNameInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileNameInformation.cs

## Purpose
`FileNameInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileNameInformation class. Fields include FixedLength:int, FileNameLength:uint, FileName:string. Direct methods include FileNameInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileNameInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileNetworkOpenInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileNetworkOpenInformation.cs

## Purpose
`FileNetworkOpenInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileNetworkOpenInformation class. Fields include FixedLength:int, CreationTime:DateTime?, LastAccessTime:DateTime?, LastWriteTime:DateTime?, ChangeTime:DateTime?, AllocationSize:long, EndOfFile:long, FileAttributes:FileAttributes, Reserved:uint. Direct methods include FileNetworkOpenInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileNetworkOpenInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FilePositionInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FilePositionInformation.cs

## Purpose
`FilePositionInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FilePositionInformation class. Fields include FixedLength:int, CurrentByteOffset:long. Direct methods include FilePositionInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FilePositionInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStandardInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStandardInformation.cs

## Purpose
`FileStandardInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileStandardInformation class. Fields include FixedLength:int, AllocationSize:long, EndOfFile:long, NumberOfLinks:uint, DeletePending:bool, Directory:bool, Reserved:ushort. Direct methods include FileStandardInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStandardInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStreamEntry.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStreamEntry.cs

## Purpose
`FileStreamEntry` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileStreamEntry class. Fields include FixedLength:int, NextEntryOffset:uint, StreamNameLength:uint, StreamSize:long, StreamAllocationSize:long, StreamName:string. Direct methods include FileStreamEntry, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStreamEntry.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStreamInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStreamInformation.cs

## Purpose
`FileStreamInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileStreamInformation class. Fields include none declared. Direct methods include FileStreamInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileStreamInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileBothDirectoryInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileBothDirectoryInformation.cs

## Purpose
`FileBothDirectoryInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileBothDirectoryInformation class. Fields include FixedLength:int, CreationTime:DateTime, LastAccessTime:DateTime, LastWriteTime:DateTime, ChangeTime:DateTime, EndOfFile:long, AllocationSize:long, FileAttributes:FileAttributes, FileNameLength:uint, EaSize:uint, ShortNameLength:byte, Reserved:byte, ShortName:string, FileName:string. Direct methods include FileBothDirectoryInformation, WriteBytes.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileBothDirectoryInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileDirectoryInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileDirectoryInformation.cs

## Purpose
`FileDirectoryInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileDirectoryInformation class. Fields include FixedLength:int, CreationTime:DateTime, LastAccessTime:DateTime, LastWriteTime:DateTime, ChangeTime:DateTime, EndOfFile:long, AllocationSize:long, FileAttributes:FileAttributes, FileNameLength:uint, FileName:string. Direct methods include FileDirectoryInformation, WriteBytes.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileDirectoryInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileFullDirectoryInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileFullDirectoryInformation.cs

## Purpose
`FileFullDirectoryInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileFullDirectoryInformation class. Fields include FixedLength:int, CreationTime:DateTime, LastAccessTime:DateTime, LastWriteTime:DateTime, ChangeTime:DateTime, EndOfFile:long, AllocationSize:long, FileAttributes:FileAttributes, FileNameLength:uint, EaSize:uint, FileName:string. Direct methods include FileFullDirectoryInformation, WriteBytes.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileFullDirectoryInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileIdBothDirectoryInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileIdBothDirectoryInformation.cs

## Purpose
`FileIdBothDirectoryInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileIdBothDirectoryInformation class. Fields include FixedLength:int, CreationTime:DateTime, LastAccessTime:DateTime, LastWriteTime:DateTime, ChangeTime:DateTime, EndOfFile:long, AllocationSize:long, FileAttributes:FileAttributes, FileNameLength:uint, EaSize:uint, ShortNameLength:byte, Reserved1:byte, ShortName:string, Reserved2:ushort, FileId:ulong, FileName:string. Direct methods include FileIdBothDirectoryInformation, WriteBytes.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileIdBothDirectoryInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileIdFullDirectoryInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileIdFullDirectoryInformation.cs

## Purpose
`FileIdFullDirectoryInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileIdFullDirectoryInformation class. Fields include FixedLength:int, CreationTime:DateTime, LastAccessTime:DateTime, LastWriteTime:DateTime, ChangeTime:DateTime, EndOfFile:long, AllocationSize:long, FileAttributes:FileAttributes, FileNameLength:uint, EaSize:uint, Reserved:uint, FileId:ulong, FileName:string. Direct methods include FileIdFullDirectoryInformation, WriteBytes.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileIdFullDirectoryInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileNamesInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileNamesInformation.cs

## Purpose
`FileNamesInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileNamesInformation class. Fields include FixedLength:int, FileNameLength:uint, FileName:string. Direct methods include FileNamesInformation, WriteBytes.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/FileNamesInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/QueryDirectoryFileInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/QueryDirectoryFileInformation.cs

## Purpose
`QueryDirectoryFileInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: QueryDirectoryFileInformation class. Fields include NextEntryOffset:uint, FileIndex:uint. Direct methods include QueryDirectoryFileInformation, WriteBytes, ReadFileInformation, ReadFileInformationList, GetBytes, GetListLength.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/QueryDirectoryFileInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileAllocationInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileAllocationInformation.cs

## Purpose
`FileAllocationInformation` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileAllocationInformation class. Fields include FixedLength:int, AllocationSize:long. Direct methods include FileAllocationInformation, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileAllocationInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileDispositionInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileDispositionInformation.cs

## Purpose
`FileDispositionInformation` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileDispositionInformation class. Fields include FixedLength:int, DeletePending:bool. Direct methods include FileDispositionInformation, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileDispositionInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileEndOfFileInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileEndOfFileInformation.cs

## Purpose
`FileEndOfFileInformation` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileEndOfFileInformation class. Fields include FixedLength:int, EndOfFile:long. Direct methods include FileEndOfFileInformation, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileEndOfFileInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType1.cs

## Purpose
`FileLinkInformationType1` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileLinkInformationType1 class. Fields include FixedLength:int, ReplaceIfExists:bool, RootDirectory:uint, FileNameLength:uint, FileName:string. Direct methods include FileLinkInformationType1, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType1.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType2.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType2.cs

## Purpose
`FileLinkInformationType2` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileLinkInformationType2 class. Fields include FixedLength:int, ReplaceIfExists:bool, RootDirectory:ulong, FileNameLength:uint, FileName:string. Direct methods include FileLinkInformationType2, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType2.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileRenameInformationType1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileRenameInformationType1.cs

## Purpose
`FileRenameInformationType1` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileRenameInformationType1 class. Fields include FixedLength:int, ReplaceIfExists:bool, RootDirectory:uint, FileNameLength:uint, FileName:string. Direct methods include FileRenameInformationType1, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileRenameInformationType1.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileRenameInformationType2.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileRenameInformationType2.cs

## Purpose
`FileRenameInformationType2` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileRenameInformationType2 class. Fields include FixedLength:int, ReplaceIfExists:bool, RootDirectory:ulong, FileNameLength:uint, FileName:string. Direct methods include FileRenameInformationType2, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileRenameInformationType2.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileValidDataLengthInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileValidDataLengthInformation.cs

## Purpose
`FileValidDataLengthInformation` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileValidDataLengthInformation class. Fields include FixedLength:int, ValidDataLength:long. Direct methods include FileValidDataLengthInformation, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileValidDataLengthInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/SetFileTime.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/SetFileTime.cs

## Purpose
`SetFileTime` represents SMB set-info timestamp semantics, including null time and the special must-not-change sentinel.

## Important APIs, Types, And Functions
It exposes `MustNotChange`, nullable `Time`, `ToFileTimeUtc`, and `FromFileTimeUtc`.

## Control Flow
Constructors create either a sentinel or concrete nullable time. Conversion to FILETIME returns `-1` for must-not-change, `0` for null, or the UTC FILETIME. Conversion from FILETIME reverses those meanings.

## State And Persistence Behavior
The struct is value state only and persists as timestamp integers in file-basic-information buffers.

## Dependencies And Integration Points
Used by `FileTimeHelper` and `FileBasicInformation` for SMB set-file-basic-info operations.

## Risks
Confusing `0`, `-1`, null, and real times can unexpectedly clear or preserve timestamps.

## Test Signals
Test all sentinel conversions and round trips through `FileTimeHelper.ReadSetFileTime`/`WriteSetFileTime`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/SetFileTime.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileNotifyInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileNotifyInformation.cs

## Purpose
Defines the wire-level `FileAction` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include Added = 0x00000001, Removed = 0x00000002, Modified = 0x00000003, RenamedOldName = 0x00000004, RenamedNewName = 0x00000005, AddedStream = 0x00000006, RemovedStream = 0x00000007, ModifiedStream = 0x00000008, RemovedByDelete = 0x00000009, IDNotTunneled = 0x0000000A, TunneledIDCollision = 0x0000000B. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileNotifyInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsAttributeInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsAttributeInformation.cs

## Purpose
`FileFsAttributeInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsAttributeInformation class. Fields include FixedLength:int, FileSystemAttributes:FileSystemAttributes, MaximumComponentNameLength:uint, FileSystemNameLength:uint, FileSystemName:string. Direct methods include FileFsAttributeInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsAttributeInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsControlInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsControlInformation.cs

## Purpose
`FileFsControlInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsControlInformation class. Fields include FixedLength:int, FreeSpaceStartFiltering:long, FreeSpaceThreshold:long, FreeSpaceStopFiltering:long, DefaultQuotaThreshold:ulong, DefaultQuotaLimit:ulong, FileSystemControlFlags:FileSystemControlFlags, Padding:uint. Direct methods include FileFsControlInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsControlInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsDeviceInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsDeviceInformation.cs

## Purpose
`FileFsDeviceInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsDeviceInformation class. Fields include FixedLength:int, DeviceType:DeviceType, Characteristics:DeviceCharacteristics. Direct methods include FileFsDeviceInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsDeviceInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsFullSizeInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsFullSizeInformation.cs

## Purpose
`FileFsFullSizeInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsFullSizeInformation class. Fields include FixedLength:int, TotalAllocationUnits:long, CallerAvailableAllocationUnits:long, ActualAvailableAllocationUnits:long, SectorsPerAllocationUnit:uint, BytesPerSector:uint. Direct methods include FileFsFullSizeInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsFullSizeInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsObjectIdInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsObjectIdInformation.cs

## Purpose
`FileFsObjectIdInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsObjectIdInformation class. Fields include FixedLength:int, ObjectID:Guid, ExtendedInfo:byte[]. Direct methods include FileFsObjectIdInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsObjectIdInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSectorSizeInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSectorSizeInformation.cs

## Purpose
`FileFsSectorSizeInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsSectorSizeInformation class. Fields include FixedLength:int, LogicalBytesPerSector:uint, PhysicalBytesPerSectorForAtomicity:uint, PhysicalBytesPerSectorForPerformance:uint, FileSystemEffectivePhysicalBytesPerSectorForAtomicity:uint, Flags:SectorSizeInformationFlags, ByteOffsetForSectorAlignment:uint, ByteOffsetForPartitionAlignment:uint. Direct methods include FileFsSectorSizeInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSectorSizeInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSizeInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSizeInformation.cs

## Purpose
`FileFsSizeInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsSizeInformation class. Fields include FixedLength:int, TotalAllocationUnits:long, AvailableAllocationUnits:long, SectorsPerAllocationUnit:uint, BytesPerSector:uint. Direct methods include FileFsSizeInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSizeInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsVolumeInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsVolumeInformation.cs

## Purpose
`FileFsVolumeInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsVolumeInformation class. Fields include FixedLength:int, VolumeCreationTime:DateTime?, VolumeSerialNumber:uint, VolumeLabelLength:uint, SupportsObjects:bool, Reserved:byte, VolumeLabel:string. Direct methods include FileFsVolumeInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsVolumeInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileSystemInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileSystemInformation.cs

## Purpose
`FileSystemInformation` is the abstract base and factory for NT filesystem information records used by SMB QueryInfo with `InfoType.FileSystem`.

## Important APIs, Types, And Functions
Subclasses implement `WriteBytes`, `FileSystemInformationClass`, and `Length`; `GetBytes` serializes an instance; static `GetFileSystemInformation` dispatches class codes to concrete filesystem information types.

## Control Flow
Factory control flow switches on `FileSystemInformationClass` and returns volume, size, device, attribute, control, full-size, object-id, or sector-size records. Unsupported classes throw `UnsupportedInformationLevelException`.

## State And Persistence Behavior
The base class has no retained state; subclasses carry one parsed filesystem metadata response.

## Dependencies And Integration Points
Used by SMB1/SMB2 file stores and server query-info handlers to expose volume and filesystem capabilities.

## Risks
Factory drift is the main risk: enum values without concrete parser support become runtime failures. Buffer size assumptions also matter because some strings are variable length.

## Test Signals
Test every supported filesystem info class with parse/write round trips and unsupported class error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileSystemInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/ObjectIDBufferType1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/ObjectIDBufferType1.cs

## Purpose
`ObjectIDBufferType1` models the 64-byte FSCTL object ID buffer containing object, birth volume, birth object, and domain GUIDs.

## Important APIs, Types, And Functions
Direct types: ObjectIDBufferType1 class. Fields include Length:int, ObjectId:Guid, BirthVolumeId:Guid, BirthObjectId:Guid, DomainId:Guid. Direct methods include ObjectIDBufferType1, GetBytes.

## Control Flow
The constructor reads four consecutive 16-byte GUIDs. `GetBytes` writes the GUIDs back in the same order.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Used by object-id IOCTL handlers and depends on GUID byte conversion helpers.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/ObjectIDBufferType1.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/PipeWaitRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/PipeWaitRequest.cs

## Purpose
`PipeWaitRequest` models the named-pipe wait FSCTL input buffer with timeout, time-specified flag, padding, and pipe name.

## Important APIs, Types, And Functions
Direct types: PipeWaitRequest class. Fields include FixedLength:int, Timeout:ulong, NameLength:uint, TimeSpecified:bool, Padding:byte, Name:string. Direct methods include PipeWaitRequest, GetBytes.

## Control Flow
The constructor reads timeout, name length, time flag, padding, and UTF-16 pipe name. `GetBytes` serializes the fixed header followed by the name.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Used by named-pipe IOCTL handling in `NamedPipeStore` and SMB server/client FSCTL paths.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/PipeWaitRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/ACE.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/ACE.cs

## Purpose
`ACE` is the abstract base for access-control entries inside SMB security descriptors.

## Important APIs, Types, And Functions
Direct types: ACE class. Fields include Header:AceHeader. Direct methods include WriteBytes, GetAce.

## Control Flow
`GetAce` reads the ACE header type and dispatches to `AccessAllowedACE` or `AccessDeniedACE`; subclasses provide `WriteBytes` and `Length`.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Depends on `AceHeader`, ACE type enums, SID, access masks, ACL/security descriptor parsing.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/ACE.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessAllowedACE.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessAllowedACE.cs

## Purpose
`AccessAllowedACE` models a concrete discretionary ACL entry with an access mask and SID.

## Important APIs, Types, And Functions
Direct types: AccessAllowedACE class. Fields include FixedLength:int, Mask:AccessMask, Sid:SID. Direct methods include AccessAllowedACE, WriteBytes.

## Control Flow
The constructor reads the ACE header, access mask, and SID. `WriteBytes` fills the header size, writes the header, mask, and SID, and advances the caller's offset.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Used by ACL and security descriptor serialization, with dependencies on `AceHeader`, `AccessMask`, and `SID`.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessAllowedACE.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessDeniedACE.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessDeniedACE.cs

## Purpose
`AccessDeniedACE` models a concrete discretionary ACL entry with an access mask and SID.

## Important APIs, Types, And Functions
Direct types: AccessDeniedACE class. Fields include FixedLength:int, Mask:AccessMask, Sid:SID. Direct methods include AccessDeniedACE, WriteBytes.

## Control Flow
The constructor reads the ACE header, access mask, and SID. `WriteBytes` fills the header size, writes the header, mask, and SID, and advances the caller's offset.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Used by ACL and security descriptor serialization, with dependencies on `AceHeader`, `AccessMask`, and `SID`.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessDeniedACE.cs -->
