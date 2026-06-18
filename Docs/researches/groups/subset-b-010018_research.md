# subset-b-010018 research

This grouped report covers the requested SMBLibrary adapter, Win32 integration, authentication, protocol parsing, and test files. Each file section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Query.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Query.cs

## Purpose
`NTFileSystemAdapter.Query.cs` implements `GetFileInformation` for the managed `IFileSystem`-backed `INTFileStore` adapter. It translates a subset of SMB/NT file information classes into SMBLibrary `FileInformation` records from `DiskAccessLibrary.FileSystems.Abstractions.FileSystemEntry` metadata.

## Important APIs, Types, And Functions
The main API is `GetFileInformation(out FileInformation result, object handle, FileInformationClass informationClass)`. It consumes the adapter's `FileHandle`, calls `m_fileSystem.GetEntry(path)`, and emits `FileBasicInformation`, `FileStandardInformation`, `FileInternalInformation`, `FileEaInformation`, `FileNameInformation`, `FileAllInformation`, `FileStreamInformation`, and `FileNetworkOpenInformation`. The helper `GetFileAttributes(FileSystemEntry entry)` maps hidden, read-only, archive, and directory flags to `FileAttributes`, defaulting to `Normal`.

## Control Flow
The method first resolves the current entry for the handle path and maps I/O or access exceptions through `ToNTStatus`. It then switches on `informationClass`, populating the requested structure with timestamps, allocation size via `GetAllocationSize`, EOF size, directory status, delete-pending state from the handle, name, and named-stream entries when requested. Unsupported but recognized classes return `STATUS_NOT_IMPLEMENTED`; unknown classes return `STATUS_INVALID_INFO_CLASS`.

## State And Persistence
This file is read-only with respect to the backing filesystem. It reflects current metadata from `m_fileSystem`; the only handle-local state it exposes is `DeleteOnClose`. It does not persist or cache information.

## Dependencies And Integration Points
It depends on the partial `NTFileSystemAdapter` core for `m_fileSystem`, `FileHandle`, `GetAllocationSize`, logging, and exception-to-status mapping. It integrates with SMB query-info handling through the `INTFileStore.GetFileInformation` contract and with named-stream support through `IFileSystem.ListDataStreams`.

## Risks
Many information classes are intentionally unimplemented, so clients needing access, position, EA, mode, alignment, compression, pipe, or attribute-tag data receive limited behavior. `FileInternalInformation` emits an empty structure without a stable file ID. `FileNameInformation` returns `entry.Name`, not necessarily a full path. Named stream enumeration assumes the backing `IFileSystem` implementation correctly models alternate data streams.

## Test Signals
This subset has no direct unit test for the adapter query mapping. Indirect coverage would come from SMB query-info flows or file-store integration tests that exercise `INTFileStore.GetFileInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Query.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryDirectory.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryDirectory.cs

## Purpose
`NTFileSystemAdapter.QueryDirectory.cs` implements directory enumeration and directory-entry information conversion for the managed adapter. It bridges SMB query-directory requests to `IFileSystem` directory listing and exact-entry lookup.

## Important APIs, Types, And Functions
The public entry point is `QueryDirectory(out List<QueryDirectoryFileInformation> result, object handle, string fileName, FileInformationClass informationClass)`. Helpers include `GetFiltered`, `ContainsWildcardCharacters`, `IsFileNameInExpression`, `FromFileSystemEntries`, and `FromFileSystemEntry`. Supported output classes include `FileBothDirectoryInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdBothDirectoryInformation`, `FileIdFullDirectoryInformation`, and `FileNamesInformation`.

## Control Flow
The method rejects non-directory handles and empty names with `STATUS_INVALID_PARAMETER`. For wildcard expressions it lists entries in the handle path, filters by a simplified MS-FSA expression matcher, then injects cloned `.` and `..` entries. For exact names it resolves the parent directory path and calls `m_fileSystem.GetEntry(path + fileName)`. It converts entries to SMBLibrary directory information records and maps unsupported information levels to `STATUS_INVALID_INFO_CLASS`.

## State And Persistence
The operation is read-only. It reflects backing directory contents at call time and creates only transient cloned `FileSystemEntry` objects for `.` and `..`.

## Dependencies And Integration Points
The code depends on `DiskAccessLibrary.FileSystems.Abstractions` for entries and path helpers, the core adapter for exception mapping and allocation-size calculation, and SMBLibrary `QueryDirectoryFileInformation` subclasses. It is invoked by SMB1/SMB2 directory enumeration through the `INTFileStore.QueryDirectory` interface.

## Risks
Wildcard matching is only a subset of the MS-FSA rules: suffix `*`, leading DOS_STAR `<`, DOS_DOT `"`, and exact matches are handled, but arbitrary `?`, middle `*`, and complex DOS_QM behavior are not fully implemented. Exact lookup uses string concatenation after `GetDirectoryPath`, making path separator behavior dependent on `FileSystem` conventions. The wildcard path inserts `.` and `..` after filtering, so those entries are returned regardless of the expression. File IDs are emitted as zero.

## Test Signals
No direct directory adapter tests are present in this subset. Useful tests would cover wildcard expression edge cases, exact lookups, invalid handles, empty patterns, unsupported information classes, and `.`/`..` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryDirectory.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryFileSystem.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryFileSystem.cs

## Purpose
`NTFileSystemAdapter.QueryFileSystem.cs` reports volume and filesystem metadata for the managed `IFileSystem` adapter. It provides SMB clients with synthetic disk geometry, capacity, capabilities, and filesystem control data.

## Important APIs, Types, And Functions
`GetFileSystemInformation(out FileSystemInformation result, FileSystemInformationClass informationClass)` supports `FileFsVolumeInformation`, `FileFsSizeInformation`, `FileFsDeviceInformation`, `FileFsAttributeInformation`, `FileFsControlInformation`, `FileFsFullSizeInformation`, `FileFsObjectIdInformation`, and `FileFsSectorSizeInformation`. `SetFileSystemInformation(FileSystemInformation information)` always returns `STATUS_NOT_SUPPORTED`.

## Control Flow
The query method switches by information class. It uses adapter constants `BytesPerSector = 512` and `ClusterSize = 4096`, reports total and free allocation units from `m_fileSystem.Size` and `m_fileSystem.FreeSpace`, marks the device as a mounted disk, advertises case-preserved Unicode names, returns the backing filesystem name, and rejects object ID support with `STATUS_INVALID_PARAMETER`.

## State And Persistence
There is no persisted or mutable state. Values are either fixed constants or current properties from `m_fileSystem`.

## Dependencies And Integration Points
The file depends on the partial adapter's `m_fileSystem` and constants. It implements the `INTFileStore.GetFileSystemInformation` path used by SMB filesystem-info requests.

## Risks
Geometry is synthetic and may not match the backing implementation. Capabilities are conservative but incomplete: named streams are not advertised here even though other adapter code can list them. Quota values are set to `UInt64.MaxValue`; clients that interpret quotas strictly may get unrealistic values. Filesystem mutation through set-info is unsupported.

## Test Signals
No direct tests in this subset validate these returned structures. Coverage would need assertions for capacity rounding, advertised attributes, sector-size information, object-ID rejection, and unsupported set-info.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryFileSystem.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Set.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Set.cs

## Purpose
`NTFileSystemAdapter.Set.cs` implements selected file information updates for the managed adapter: basic metadata, rename, disposition/delete, allocation size, and EOF size.

## Important APIs, Types, And Functions
The public method is `SetFileInformation(object handle, FileInformation information)`. It handles `FileBasicInformation`, `FileRenameInformationType2`, `FileDispositionInformation`, `FileAllocationInformation`, and `FileEndOfFileInformation`. The private helper `IsFileExists(string path)` probes the backing filesystem for replacement decisions.

## Control Flow
For basic information it extracts hidden/read-only/archive flags, calls `m_fileSystem.SetAttributes`, then sets creation, last-write, and last-access timestamps. For rename it normalizes the target to a leading backslash, closes an open stream, optionally deletes an existing target when `ReplaceIfExists` is true, moves the backing object, and updates `fileHandle.Path`. For disposition it closes the stream and deletes immediately when `DeletePending` is true. Allocation and EOF requests both call `fileHandle.Stream.SetLength`.

## State And Persistence
This file mutates backing filesystem metadata and file contents. Rename updates handle state to the new path. Disposition deletes immediately rather than deferring strictly to handle close. Allocation/EOF truncate or extend the underlying stream.

## Dependencies And Integration Points
It depends on `m_fileSystem` mutation APIs, core adapter logging and exception mapping, and SMBLibrary file-information classes. It participates in SMB set-info handling through `INTFileStore.SetFileInformation`.

## Risks
`FileDispositionInformation` deletes immediately, which differs from full NT delete-pending semantics and can expose timing differences. Rename closes the stream and does not reopen it, so subsequent reads/writes through the same handle may fail. Allocation/EOF assume `fileHandle.Stream` is non-null; directory or metadata-only handles can throw. `FileBasicInformation` ignores the NT convention that zero timestamps mean unchanged. Replacement deletion does not distinguish files from non-empty directories beyond backing errors.

## Test Signals
No direct adapter set-info tests are present. Tests should cover rename case-only changes, replace/no-replace collision status, delete-on-close semantics, stream availability after rename, timestamp zero handling, and directory set-info behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Set.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.cs

## Purpose
`NTFileSystemAdapter.cs` is the core of the managed `IFileSystem` to `INTFileStore` adapter. It implements SMB-style create/open, read, write, close, flush, basic unsupported operations, logging, exception mapping, create-option mapping, and allocation-size rounding.

## Important APIs, Types, And Functions
The class `NTFileSystemAdapter : INTFileStore` owns `m_fileSystem`, exposes `LogEntryAdded`, and implements `CreateFile`, `CloseFile`, `ReadFile`, `WriteFile`, `FlushFileBuffers`, `LockFile`, `UnlockFile`, security-info stubs, notify/cancel stubs, `DeviceIOControl`, `Log`, `ToNTStatus`, `ToFileOptions`, `ToFileOptionsString`, and `GetAllocationSize`. `OpenFileStream` adapts SMB desired access/share/create options to .NET stream open calls.

## Control Flow
`CreateFile` derives create access and directory/file constraints from SMB inputs, rejects named streams when unsupported, probes the entry, then branches by `CreateDisposition`. It opens existing objects, creates new files or directories, truncates for overwrite, or deletes and recreates for supersede. If file data access is requested and the target is not a directory, it opens a stream with mapped share and option flags. `ReadFile` seeks, reads, and trims EOF responses; `WriteFile` seeks and writes all bytes. `CloseFile` closes the stream and performs manual delete-on-close when no stream was opened.

## State And Persistence
The adapter stores only the backing filesystem reference and log subscribers. File state lives in returned `FileHandle` objects, including path, directory flag, stream, and delete-on-close flag. Create, overwrite, supersede, write, and close/delete operations mutate the backing filesystem.

## Dependencies And Integration Points
It depends on `DiskAccessLibrary.FileSystems.Abstractions.IFileSystem`, SMBLibrary `INTFileStore`, `NTFileStoreHelper`, `FileHandle`, `NTStatus`, and `Utilities.LogEntry`. Partial class files implement query and set operations. It is suitable for non-Win32 backends that expose the `IFileSystem` abstraction.

## Risks
The implementation is intentionally incomplete for locks, security descriptors, notify change, cancellation, and FSCTLs. NT create disposition semantics are approximated; supersede deletes before recreate and may lose metadata. Named-stream detection rejects any colon in the path when streams are unsupported, which may also reject unusual path syntaxes. Exception-to-status mapping is coarse and returns `STATUS_DATA_ERROR` for many I/O failures. Delete-on-close relies on .NET `FileOptions.DeleteOnClose` when a stream exists but manual deletion for directories or metadata-only opens.

## Test Signals
This subset does not include direct tests for the managed adapter. Indirect expectations are implied by `INTFileStore` tests and SMB server file operations, but notify/cancel tests target the Win32 implementation, not this adapter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/AesCcmTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/AesCcmTests.cs

## Purpose
`AesCcmTests.cs` validates the utility AES-CCM implementation against RFC 3610 and SMB 3.0 encryption-oriented vectors.

## Important APIs, Types, And Functions
The MSTest class `AesCcmTests` calls `AesCcm.Encrypt` and `AesCcm.DecryptAndAuthenticate`, comparing ciphertext, plaintext, and authentication tags with `ByteUtils.AreByteArraysEqual`.

## Control Flow
Each test constructs static key, nonce, plaintext/ciphertext, associated data, and expected tag bytes. Encryption tests capture the calculated signature output parameter and compare both encrypted data and tag. Decryption tests pass ciphertext, associated data, and tag and compare the recovered plaintext.

## State And Persistence
The tests are pure in-memory cryptographic vector checks. They create no persistent state.

## Dependencies And Integration Points
They depend on `Utilities.AesCcm` and `Utilities.ByteUtils`. They protect lower-level cryptography used by SMB2/SMB3 message encryption.

## Risks
The tests cover known vectors but not invalid tag rejection, nonce length boundaries, empty payloads, large payloads, or parameter validation. The SMB vector comments reference archived Microsoft material, but the assertions are local byte fixtures.

## Test Signals
Strong signal for AES-CCM happy-path encryption/decryption compatibility. These tests complement `SMB2EncryptionTests`, which checks SMB transform/header integration around AES-CCM.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/AesCcmTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/Client/SMB2ClientTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/Client/SMB2ClientTests.cs

## Purpose
`SMB2ClientTests.cs` verifies that `SMB2Client.Connect` fails quickly when a TCP peer either never sends an SMB response or sends invalid non-SMB data.

## Important APIs, Types, And Functions
The MSTest class owns a loopback `TcpListener`, randomized port, `m_clientConnected`, and callbacks `AcceptTcpClient_DoNotReply` and `AcceptTcpClient_SendNonSmbData`. Tests instantiate `SMB2Client(timeoutInMilliseconds)` and call `Connect(IPAddress.Loopback, SMBTransportType.DirectTCPTransport, port)`.

## Control Flow
`TestInitialize` starts a loopback listener. Each test begins an async accept callback, starts `client.Connect` on a thread while a stopwatch runs, waits until the listener accepted the connection, then asserts `Connect` returned false and elapsed time is under 200 ms despite the nominal 1000 ms timeout.

## State And Persistence
State is transient network listener/client state and thread-local flags. No files are written.

## Dependencies And Integration Points
The tests depend on `SMBLibrary.Client.SMB2Client`, direct TCP transport, .NET `TcpListener`, and loopback networking. They protect connection negotiation failure paths in client code.

## Risks
The assertions are timing-sensitive and can be flaky on slow or heavily loaded systems. The tests do not close accepted `TcpClient` instances or the listener in a cleanup method. Random port selection may still collide. The declared `ManualResetEvent` variables are unused.

## Test Signals
They signal that malformed or silent servers should not make the client block for the full timeout once the TCP connection is established. They do not validate successful negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/Client/SMB2ClientTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/RequestGetDfsReferralExTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/RequestGetDfsReferralExTests.cs

## Purpose
`RequestGetDfsReferralExTests.cs` validates parsing and serialization round-trip behavior for DFS referral extended requests with a site-name payload.

## Important APIs, Types, And Functions
The tests exercise `SMBLibrary.DFS.RequestGetDfsReferralEx`, `RequestGetDfsReferralExFlags.SiteName`, its byte constructor, properties `MaxReferralLevel`, `Flags`, `RequestFileName`, `SiteName`, and `GetBytes`.

## Control Flow
The parse test feeds a fixed little-endian/UTF-16LE byte buffer and asserts decoded referral level, flag, UNC request path, and site name. The round-trip test constructs an object with equivalent values, serializes it, reparses it, and asserts the same fields.

## State And Persistence
All data is in-memory. The fixed buffer acts as a protocol fixture.

## Dependencies And Integration Points
The tests depend on the DFS request parser/serializer and MSTest. The covered object is used by DFS management/request handling code that exchanges `FSCTL_DFS_GET_REFERRALS_EX`-style payloads.

## Risks
Coverage is limited to the SiteName flag and one well-formed request. It does not cover absent site names, invalid offsets/lengths, other flags, maximum referral levels, or malformed UTF-16 data.

## Test Signals
Good signal for normal site-name request decoding and object serialization preserving fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/RequestGetDfsReferralExTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/ResponseGetDfsReferralTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/ResponseGetDfsReferralTests.cs

## Purpose
`ResponseGetDfsReferralTests.cs` validates DFS referral response parsing for version 4 entries and one serialization round trip.

## Important APIs, Types, And Functions
The MSTest class exercises `ResponseGetDfsReferral`, `DfsReferralEntryV4`, `DfsReferralHeaderFlags`, `DfsReferralEntryFlags`, `ReferralEntries`, `PathConsumed`, `TimeToLive`, paths, network addresses, and `ServiceSiteGuid`.

## Control Flow
One test parses a Windows Server 2008 R2 single-entry fixture and checks header flags plus all V4 entry fields. Another parses a two-entry fixture and validates per-entry target boundaries and network addresses. The round-trip test builds a single V4 entry response, serializes with `GetBytes`, reparses, and revalidates.

## State And Persistence
All fixtures and result objects are in-memory protocol data. No persistent state is created.

## Dependencies And Integration Points
It depends on `SMBLibrary.DFS` response models and is relevant to DFS referral client/server handling.

## Risks
Tests cover V4 entries only and do not exercise V1/V2/V3 referrals, malformed offsets, inconsistent entry counts, non-empty service site GUIDs, or target-list ordering beyond fixed fixtures.

## Test Signals
Strong signal that common V4 DFS referral responses with one or more targets parse correctly and that basic V4 serialization is internally consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/DFS/ResponseGetDfsReferralTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/IntegrationTests/LoginTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/IntegrationTests/LoginTests.cs

## Purpose
`LoginTests.cs` is an in-process SMB2 client/server integration test for NTLM login success, reconnect/login behavior, and failed credentials.

## Important APIs, Types, And Functions
The class creates an `SMBServer` with an empty `SMBShareCollection`, an `IndependentNTLMAuthenticationProvider` that accepts password `"password"`, and a `GSSProvider`. Tests use `SMB2Client.Connect`, `Login`, `Logoff`, and `Disconnect`.

## Control Flow
`TestInitialize` selects a randomized loopback port, builds the server with NTLM GSS authentication, and starts it. `TestCleanup` stops the server. Tests connect a client, then assert success for valid credentials, success after logoff/disconnect/reconnect, and `STATUS_LOGON_FAILURE` for wrong-case password.

## State And Persistence
State is transient process-local server, client sessions, and TCP listeners. No shares are mounted and no files are persisted.

## Dependencies And Integration Points
The tests integrate SMB server startup, GSS/SPNEGO or NTLM negotiation, SMB2 client session setup, logoff, reconnect, and independent NTLM provider behavior.

## Risks
Random port selection may collide. The tests assume loopback networking and thread scheduling are reliable. They do not validate tree connect, guest/anonymous login, signing, encryption, or real OS credential providers.

## Test Signals
Good end-to-end signal for basic SMB2 authentication lifecycle using the independent NTLM provider.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/IntegrationTests/LoginTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTDirectoryFileSystemTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTDirectoryFileSystemTests.cs

## Purpose
`NTDirectoryFileSystemTests.cs` binds the generic `NTFileStoreTests` suite to the Win32 `NTDirectoryFileSystem` implementation rooted at `C:\Tests`.

## Important APIs, Types, And Functions
The class derives from `NTFileStoreTests`, creates `NTDirectoryFileSystem(TestDirectoryPath)`, ensures the test directory exists in a static constructor, and overrides `TestCancel`.

## Control Flow
Construction passes a real Win32 filesystem-backed store to the abstract base test. The overridden cancel test marks itself inconclusive on non-Windows platforms, otherwise delegates to the base `TestCancel`.

## State And Persistence
It creates or reuses the persistent local directory `C:\Tests` on Windows. The inherited test creates a child directory named `Dir`.

## Dependencies And Integration Points
It depends on Windows, `SMBLibrary.Win32.NTDirectoryFileSystem`, `System.Runtime.InteropServices.RuntimeInformation`, and the base `INTFileStore` notify/cancel test. It is the primary test in this subset for Win32 change-notify cancellation.

## Risks
The hard-coded `C:\Tests` path requires permissions and leaves artifacts. Non-Windows environments skip the actual behavior. The class only covers cancel behavior, not the broader Win32 file-store API.

## Test Signals
On Windows, it validates that a pending notify request can be cancelled and completes with `STATUS_CANCELLED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTDirectoryFileSystemTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTFileStoreTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTFileStoreTests.cs

## Purpose
`NTFileStoreTests.cs` defines a reusable abstract MSTest suite for `INTFileStore` implementations, currently focused on notify-change cancellation.

## Important APIs, Types, And Functions
The class stores an `INTFileStore`, a test directory name `Dir`, and nullable `m_notifyChangeStatus`. `TestCancel` calls `CreateFile`, `NotifyChange`, `Cancel`, and `CloseFile`. `OnNotifyChangeCompleted` records callback status. `CreateTestDirectory` opens or creates the test directory.

## Control Flow
The test ensures a directory exists, opens it as a directory, issues a notify request for file name, last write, and directory name changes, asserts `STATUS_PENDING`, sleeps briefly, cancels the request, closes the handle, waits for callback completion, and expects `STATUS_CANCELLED`.

## State And Persistence
The test may create a backing directory named `Dir` in the concrete store. It keeps callback status in memory.

## Dependencies And Integration Points
It depends only on the `INTFileStore` contract and MSTest. `NTDirectoryFileSystemTests` supplies a Win32 concrete store.

## Risks
The busy-wait loops can hang if callback completion never occurs. `m_notifyChangeStatus` is not reset inside `TestCancel`, which matters if test instances are reused. The one-millisecond sleep makes race timing implementation-dependent.

## Test Signals
It provides a focused signal for asynchronous notify cancellation semantics and callback status propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTFileStore/NTFileStoreTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMAuthenticationTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMAuthenticationTests.cs

## Purpose
`NTLMAuthenticationTests.cs` validates NTLM cryptographic primitives and message serialization against MS-NLMP-style known values.

## Important APIs, Types, And Functions
The tests exercise `NTLMCryptography.LMOWFv1`, `NTOWFv1`, `NTOWFv2`, `ComputeLMv1Response`, `ComputeNTLMv1Response`, `ComputeLMv2Response`, `ComputeNTLMv2Proof`, `ChallengeMessage`, `AuthenticateMessage`, `NTLMv2ClientChallenge`, `AVPairUtils`, `NTLMVersion`, and `NegotiateFlags`.

## Control Flow
Hash and response tests compute values from fixed password/user/domain/challenge inputs and compare with byte fixtures. Message tests build or parse challenge and authenticate messages, serialize them, and compare to expected byte layouts. The authenticate-message test reparses the expected bytes to normalize payload ordering before comparing serialized output.

## State And Persistence
All tests are pure in-memory byte-vector checks.

## Dependencies And Integration Points
They depend on `SMBLibrary.Authentication.NTLM` and `Utilities.ByteUtils`. They protect NTLM client/server authentication, exported session key derivation inputs, and higher-level SMB login behavior.

## Risks
The tests cover selected canonical vectors but not malformed messages, Unicode/OEM edge cases, target-info variants, channel binding, MIC presence in authenticate construction, or random challenge generation. LM/NTLMv1 vectors cover legacy algorithms that are security-sensitive despite being obsolete.

## Test Signals
Strong signal for core NTLM hash/response compatibility and basic challenge/authenticate message byte layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMAuthenticationTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMSigningTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMSigningTests.cs

## Purpose
`NTLMSigningTests.cs` validates NTLM message integrity code calculation, exported session key derivation helpers, NTLM signing/sealing key generation, and SPNEGO mechListMIC calculation.

## Important APIs, Types, And Functions
The class calls `NTLMCryptography.ValidateAuthenticateMessageMIC`, `ComputeClientSignKey`, `ComputeClientSealKey`, `ComputeMechListMIC`, `KXKey`, `NTOWFv1`, `NTOWFv2`, `AuthenticationMessageUtils.IsNTLMv2NTResponse`, `RC4.Decrypt`, `ChallengeMessage`, `AuthenticateMessage`, `MD4`, and `HMACMD5`. The private `GetExportedSessionKey` mirrors protocol key-selection logic.

## Control Flow
MIC tests parse captured type 1, type 2, and type 3 messages, derive session base and exported session keys according to NTLMv1, LM, extended session security, or NTLMv2 rules, then validate the authenticate MIC. Key tests compare deterministic sign/seal/mechListMIC outputs against fixed byte arrays.

## State And Persistence
The tests operate only on static in-memory byte arrays and derived keys.

## Dependencies And Integration Points
They depend on NTLM cryptography classes, RC4, MD4/HMAC-MD5 utilities, and message parsers. They protect SMB session signing and SPNEGO MIC behavior after authentication.

## Risks
Fixtures are large and brittle; a legitimate serializer layout change may require care to preserve MIC semantics. The private exported-key helper duplicates production logic and could mask shared misunderstandings. Negative MIC tests and tampered-message cases are absent.

## Test Signals
Strong compatibility signal for MIC validation across LM/NTLMv1/NTLMv1 ESS/NTLMv2 key-exchange paths and for derived client sign/seal keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMSigningTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/RC4Tests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/RC4Tests.cs

## Purpose
`RC4Tests.cs` validates the RC4 implementation used by NTLM key exchange against published ARCFOUR draft vectors and streaming state behavior.

## Important APIs, Types, And Functions
The tests exercise `Utilities.RC4.Encrypt`, `RC4.InitializeStateFromKey`, `RC4KeyState`, `ByteReader.ReadBytes`, `ByteUtils.Concatenate`, and `ByteUtils.AreByteArraysEqual`.

## Control Flow
Three vector tests encrypt fixed plaintext with fixed keys and compare ciphertext. The streaming test initializes key state once, encrypts the plaintext in two segments, concatenates the outputs, and compares to the single-vector expected ciphertext.

## State And Persistence
All state is in-memory. The streaming test specifically verifies mutable `RC4KeyState` continuity across calls.

## Dependencies And Integration Points
It depends on `Utilities.RC4` and utility byte helpers. It supports NTLM tests and production NTLM key exchange.

## Risks
RC4 is a legacy weak cipher, but still required for NTLM compatibility. Tests do not cover decryption separately, empty inputs, or key validation, and only one streaming segmentation pattern is checked.

## Test Signals
Good signal for RC4 keystream correctness and stateful continuation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/RC4Tests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NetBiosTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NetBiosTests.cs

## Purpose
`NetBiosTests.cs` validates NetBIOS name decoding and re-encoding round trips for two encoded name fixtures.

## Important APIs, Types, And Functions
The tests use `NetBiosUtils.DecodeName(buffer, ref offset)` and `NetBiosUtils.EncodeName(name, String.Empty)`, comparing byte arrays with `ByteUtils.AreByteArraysEqual`.

## Control Flow
Each test decodes an encoded name from offset zero, then re-encodes the decoded name with an empty scope and asserts the original encoded bytes are reproduced.

## State And Persistence
All test data is in-memory protocol bytes.

## Dependencies And Integration Points
It depends on `SMBLibrary.NetBios` and `Utilities`. NetBIOS name utilities are relevant to legacy SMB/NetBIOS transport and name service handling.

## Risks
Only two simple fixtures are covered. The tests do not assert decoded text, offset advancement, scope handling, malformed names, or compression/pointer behavior.

## Test Signals
Basic signal for canonical NetBIOS 32-byte name encoding round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NetBiosTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/RPCTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/RPCTests.cs

## Purpose
`RPCTests.cs` validates parsing of selected SRVSVC/WKSSVC RPC request and response structures from fixed NDR byte fixtures.

## Important APIs, Types, And Functions
The tests instantiate `NetrWkstaGetInfoResponse`, `NetrServerGetInfoResponse`, `NetrShareEnumRequest`, `NetrShareEnumResponse`, and `NetrShareGetInfoRequest`. They inspect `WorkstationInfo100`, `ServerInfo101`, `ShareInfo1Container`, info levels, counts, server names, share names, and total entries.

## Control Flow
Each test feeds a static byte buffer to the relevant RPC model constructor, then asserts decoded discriminated-union level, concrete info type, string values, and counts.

## State And Persistence
The file uses only in-memory protocol fixtures.

## Dependencies And Integration Points
It depends on `SMBLibrary.Services` RPC model types. These structures integrate with named pipe RPC services exposed over SMB, especially workstation and server service calls.

## Risks
Coverage is parser-only for selected well-formed little-endian NDR fixtures. Serialization, malformed buffers, alignment edge cases, different info levels, and non-ASCII strings are not covered.

## Test Signals
Useful signal for NDR pointer/string/count decoding in common workstation, server, and share RPC paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/RPCTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateRequestParsingTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateRequestParsingTests.cs

## Purpose
`NegotiateRequestParsingTests.cs` validates SMB 3.1.1 negotiate request parsing when negotiate contexts are present and when the packet begins at non-zero buffer offsets.

## Important APIs, Types, And Functions
The tests exercise `SMBLibrary.SMB2.NegotiateRequest`, `NegotiateContextList`, `Dialects`, `NegotiateContextType.SMB2_PREAUTH_INTEGRITY_CAPABILITIES`, `SMB2_ENCRYPTION_CAPABILITIES`, and `GetBytes`.

## Control Flow
The fixture includes an SMB2 header, dialect list, and four negotiate contexts. Tests parse at offset zero, parse the same bytes copied two bytes into a larger buffer, and parse after a serialize/reparse cycle, asserting dialect count, context count, and first context types.

## State And Persistence
All state is in-memory byte fixture and parsed object state.

## Dependencies And Integration Points
It depends on SMB2 negotiate parser/serializer logic. The covered behavior is important for SMB 3.1.1 preauth integrity, encryption capabilities, compression, and signing or transport capabilities negotiation.

## Risks
Tests check counts and first context types but not all context payload fields. They do not cover malformed offsets, padding errors, missing contexts, or older dialect requests.

## Test Signals
Good regression signal for relative offset handling and preservation of negotiate context lists during serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateRequestParsingTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateResponseParsingTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateResponseParsingTests.cs

## Purpose
`NegotiateResponseParsingTests.cs` validates SMB 3.1.1 negotiate response parsing with negotiate context lists, non-zero offsets, and serialization round trip.

## Important APIs, Types, And Functions
The class exercises `SMBLibrary.SMB2.NegotiateResponse`, `DialectRevision`, `SMB2Dialect.SMB311`, `NegotiateContextList`, and `GetBytes`.

## Control Flow
A large fixture containing an SMB2 negotiate response and two negotiate contexts is parsed at offset zero and offset two. A third test serializes the parsed object, reparses it, and verifies the dialect and context count remain intact.

## State And Persistence
All test state is in-memory protocol bytes.

## Dependencies And Integration Points
It depends on SMB2 negotiate response parsing and is relevant to SMB 3.1.1 session setup because negotiated dialect and contexts feed preauth, encryption, signing, and capabilities.

## Risks
The tests do not assert individual context payload contents, security buffer details, timestamps, GUIDs, or capability flags. Malformed padding and truncated context lists are not covered.

## Test Signals
Good signal for response context-list offset handling and serializer preservation for SMB 3.1.1 negotiate responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/NegotiateResponseParsingTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/QueryInfoResponseParsingTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/QueryInfoResponseParsingTests.cs

## Purpose
`QueryInfoResponseParsingTests.cs` validates extraction of security descriptor data from an SMB2 QUERY_INFO response.

## Important APIs, Types, And Functions
The test uses `SMBLibrary.SMB2.QueryInfoResponse`, `GetSecurityInformation`, `SecurityDescriptor`, `Dacl`, `AccessAllowedACE`, and `Sid.Revision`.

## Control Flow
It parses a fixed SMB2 query-info response fixture, extracts its security descriptor payload, then asserts the DACL contains two ACEs, the second is an access-allowed ACE, and that ACE's SID revision is one.

## State And Persistence
All data is in-memory protocol fixture state.

## Dependencies And Integration Points
It depends on SMB2 query-info response parsing and NT security descriptor/ACE parsing. This supports SMB clients querying file security metadata.

## Risks
The test checks only a few descriptor fields and one well-formed fixture. It does not cover owner/group/SACL parsing, offset/length validation, self-relative descriptor variants, malformed ACEs, or non-security query-info payloads.

## Test Signals
Focused signal that security-info response payload extraction and basic DACL/ACE decoding work.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2/QueryInfoResponseParsingTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2EncryptionTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2EncryptionTests.cs

## Purpose
`SMB2EncryptionTests.cs` validates SMB 3.0 key derivation and transform encryption/decryption behavior using Microsoft SMB encryption sample vectors.

## Important APIs, Types, And Functions
The tests call `SMB2Cryptography.GenerateClientEncryptionKey`, `GenerateClientDecryptionKey`, `EncryptMessage`, `DecryptMessage`, and parse `SMB2TransformHeader`. They compare outputs with `ByteUtils.AreByteArraysEqual`.

## Control Flow
Key generation tests derive client encryption and decryption keys from a fixed session key for dialect `SMB300`. The encryption test encrypts a fixed SMB2 message with a fixed key, nonce, and session ID, then compares ciphertext. The decryption test parses a transformed packet, extracts the encrypted payload after `SMB2TransformHeader.Length`, decrypts it, and compares plaintext.

## State And Persistence
All cryptographic and packet data is in-memory.

## Dependencies And Integration Points
It depends on SMB2 cryptography, AES-CCM utilities, and transform-header parsing. It protects SMB3 encrypted transport behavior.

## Risks
The encryption test intentionally ignores signature validation because the sample associated data contains non-zero nonce padding. Tests cover SMB300 only, not SMB302/SMB311 key labels or AES-GCM. Tampered signature and invalid transform tests are absent.

## Test Signals
Strong positive signal for SMB300 key derivation, encryption ciphertext generation, and decryption of known transform packets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2EncryptionTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2SigningTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2SigningTests.cs

## Purpose
`SMB2SigningTests.cs` validates SMB2/SMB3 message signature calculation for dialects SMB 2.0.2, SMB 2.1, and SMB 3.0.

## Important APIs, Types, And Functions
The tests use `SMB2Cryptography.CalculateSignature`, `SMB2Cryptography.GenerateSigningKey`, `SMB2Dialect.SMB202`, `SMB210`, `SMB300`, `ByteWriter.WriteBytes`, and `ByteUtils.AreByteArraysEqual`.

## Control Flow
Each test builds a fixed SMB2 message with an existing signature field, zeros the 16-byte signature at offset 48, calculates a signature using the dialect-specific algorithm/key, and compares against the expected signature bytes. The SMB300 test first derives a signing key from the exported session key.

## State And Persistence
All state is in-memory packet data and keys.

## Dependencies And Integration Points
It depends on SMB2 cryptography and byte utilities. The covered functionality is central to SMB session integrity when signing is enabled.

## Risks
Coverage stops at SMB300 and does not include SMB311 preauth-integrity-derived signing keys. It does not test verification failure, compound messages, or signing across partial buffers beyond full-message input.

## Test Signals
Strong signal for dialect-specific signing compatibility across SMB202/SMB210 HMAC-MD5 and SMB300 AES-CMAC style paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2SigningTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/NTDirectoryFileSystem.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/NTDirectoryFileSystem.cs

## Purpose
`NTDirectoryFileSystem.cs` implements `INTFileStore` directly over Windows native NT APIs rooted at a local directory. It exposes real NT create/read/write/query/set/notify/FSCTL behavior to SMBLibrary server code.

## Important APIs, Types, And Functions
The file defines `UNICODE_STRING`, `OBJECT_ATTRIBUTES`, `IO_STATUS_BLOCK`, `PendingRequest`, and `NTDirectoryFileSystem`. It P/Invokes `NtCreateFile`, `NtClose`, `NtReadFile`, `NtWriteFile`, `NtFlushBuffersFile`, `NtLockFile`, `NtUnlockFile`, `NtQueryDirectoryFile`, `NtQueryInformationFile`, `NtSetInformationFile`, `NtQueryVolumeInformationFile`, `NtSetVolumeInformationFile`, `NtQuerySecurityObject`, `NtSetSecurityObject`, `NtNotifyChangeDirectoryFile`, `NtFsControlFile`, `NtAlertThread`, and `NtCancelSynchronousIoFile`.

## Control Flow
Paths are converted to native `\??\root\relative` strings. `CreateFile` forces `SYNCHRONIZE` and synchronous alert I/O, adjusts incompatible append/no-buffering access, and calls `NtCreateFile`. Read, write, flush, lock, unlock, query-directory, query-info, set-info, volume-info, security stubs, notify, cancel, and FSCTL dispatch map the `INTFileStore` contract to native calls and parse returned byte buffers into SMBLibrary structures.

## State And Persistence
The store persists all file changes directly in the Windows filesystem under `m_directory`. It keeps an in-memory `PendingRequestCollection` for outstanding notify-change requests. Notify worker threads hold buffers and `PendingRequest` state until completion or cancellation.

## Dependencies And Integration Points
It depends on Windows `ntdll.dll`, kernel32 thread helpers, SMBLibrary file-information parsers, `ByteReader`, `ProcessHelper`, and `PendingRequestCollection`. It is the Win32 concrete file store used by SMB server integrations and tested by `NTDirectoryFileSystemTests`.

## Risks
Native interop is high risk: `UNICODE_STRING.MaximumLength` appears to use character count plus two rather than bytes, and `OBJECT_ATTRIBUTES.ObjectName` allocations are not freed after `NtCreateFile`. `QueryDirectory` and other methods compute `numberOfBytesWritten` but do not always use it. In `SetFileInformation`, the `FileLinkInformationType2` branches build local objects but assign `information = fileLinkInformationRemote`, likely losing the native path conversion. Notify cancellation has acknowledged race windows and uses worker threads plus alert/cancel APIs. Security get/set return invalid-device-request despite P/Invoke declarations existing.

## Test Signals
`NTDirectoryFileSystemTests` covers notify cancellation on Windows. Broader API behavior is largely untested in this subset and depends on Windows native API behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/NTDirectoryFileSystem.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/PendingRequestCollection.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/PendingRequestCollection.cs

## Purpose
`PendingRequestCollection.cs` tracks outstanding notify-change requests by file handle for `NTDirectoryFileSystem`.

## Important APIs, Types, And Functions
The internal class owns `Dictionary<IntPtr, List<PendingRequest>> m_handleToNotifyChangeRequests`. It provides `Add(PendingRequest request)`, `Remove(IntPtr handle, uint threadID)`, and `GetRequestsByHandle(IntPtr handle)`.

## Control Flow
`Add` locks the dictionary, appends to an existing per-handle list or creates a new list. `Remove` locks, scans the per-handle list for matching thread IDs, removes all matches, and removes the handle key when the list becomes empty. `GetRequestsByHandle` returns a copy of the current list or an empty list.

## State And Persistence
State is in-memory only and lasts for the `NTDirectoryFileSystem` instance. It represents active notify worker threads and is not persisted.

## Dependencies And Integration Points
It depends on `PendingRequest` from `NTDirectoryFileSystem.cs`. `CloseFile`, `NotifyChange`, and `Cancel` use it to find and cancel pending notifications.

## Risks
`GetRequestsByHandle` reads the dictionary without taking the same lock used by `Add`/`Remove`, so concurrent access can race. Removal by thread ID assumes uniqueness per handle. Callers can receive copied lists containing request objects that are concurrently completed or removed.

## Test Signals
No direct unit tests. It is exercised indirectly by `NTFileStoreTests.TestCancel` through notify/cancel behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/PendingRequestCollection.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ProcessHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/ProcessHelper.cs

## Purpose
`ProcessHelper.cs` provides process and operating-system bitness detection for Win32 interop code.

## Important APIs, Types, And Functions
The class P/Invokes `kernel32!IsWow64Process`. Public APIs are `IsWow64Process(Process process)`, `IsWow64Process()`, `Is64BitProcess`, and `Is64BitOperatingSystem`. Results for the current process are cached in nullable booleans.

## Control Flow
The process-specific method calls `IsWow64Process` only on OS versions expected to support it, returning false on failure or older systems. The parameterless method caches the current process result. `Is64BitProcess` caches `IntPtr.Size == 8`, and `Is64BitOperatingSystem` combines native 64-bit process or WOW64 process detection.

## State And Persistence
Only process-local cached booleans are stored. No persistent state is written.

## Dependencies And Integration Points
It depends on `System.Diagnostics.Process`, `Environment.OSVersion`, and kernel32. `NTDirectoryFileSystem.SetFileInformation` uses `Is64BitProcess` to choose file rename/link information structures.

## Risks
OS version checks can be affected by application manifest/version lie behavior. Failed `IsWow64Process` calls silently return false. Cache values do not adapt if called in unusual process emulation scenarios, though that is normally stable.

## Test Signals
No tests in this subset cover process bitness detection. Integration is indirect through Win32 set-information paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ProcessHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/IntegratedNTLMAuthenticationProvider.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/IntegratedNTLMAuthenticationProvider.cs

## Purpose
`IntegratedNTLMAuthenticationProvider.cs` implements an NTLM authentication provider backed by Windows SSPI and local account APIs, including guest fallback behavior that tries to mimic Windows server semantics.

## Important APIs, Types, And Functions
`IntegratedNTLMAuthenticationProvider : NTLMAuthenticationProviderBase` contains nested `AuthContext` with SSPI server context and decoded client identity fields. Key overrides are `GetChallengeMessage`, `Authenticate`, `DeleteSecurityContext`, and `GetContextAttribute`. Helpers include `EnableGuestLogin`, `IsUserExists`, and `ToNTStatus(Win32Error errorCode)`.

## Control Flow
Challenge creation calls `SSPIHelper.GetType2Message` from the client's negotiate bytes and stores the returned server context. Authentication parses `AuthenticateMessage`, populates context identity fields, handles anonymous or nonexistent users via optional guest login, then calls `SSPIHelper.AuthenticateType3Message`. Failed SSPI authentication can fall back to guest on `ERROR_ACCOUNT_RESTRICTION`; otherwise Win32 errors map to NT statuses. Context attributes expose access token, domain, guest flag, machine, OS version, session key, and user name.

## State And Persistence
Authentication state lives in `AuthContext` for a GSS/NTLM exchange. SSPI security contexts and access tokens are native OS resources. No persistent data is written.

## Dependencies And Integration Points
It depends on `SSPIHelper`, `NetworkAPI`, `LoginAPI`, `AuthenticateMessage`, `GSSAttributeName`, and SMBLibrary NTLM/GSS provider base classes. It integrates with SMB server session setup on Windows when OS-backed authentication is desired.

## Risks
Guest fallback is security-sensitive and depends on local policy and `Guest` account state. Exceptions from SSPI are collapsed to `SEC_E_INVALID_TOKEN`, which can hide operational causes. `EnableGuestLogin` calls `LogonUser` each time. Native access-token lifetime is delegated to callers. Nonexistent-user handling may allow guest when configured. Attribute `IsAnonymous` is not handled even though the enum contains it.

## Test Signals
No direct tests cover the integrated Windows provider in this subset. `LoginTests` use `IndependentNTLMAuthenticationProvider`, so this provider needs Windows-specific integration testing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/IntegratedNTLMAuthenticationProvider.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/LoginAPI.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/LoginAPI.cs

## Purpose
`LoginAPI.cs` wraps selected Windows logon APIs for credential validation, guest policy checks, and impersonation support.

## Important APIs, Types, And Functions
It defines `LogonType` values for interactive, network, and service logons. `LoginAPI` P/Invokes `advapi32!LogonUser`, `advapi32!ImpersonateLoggedOnUser`, and `kernel32!CloseHandle`. Public helpers are `ValidateUserPassword` and `HasEmptyPassword`.

## Control Flow
`ValidateUserPassword` calls `LogonUser` with an empty domain and provider `LOGON32_PROVIDER_WINNT40`, closes the returned token on success, returns false for expected account/logon denial errors, and throws on unexpected Win32 errors. `HasEmptyPassword` attempts network logon with an empty password and interprets success or selected policy errors as indicating empty-password behavior.

## State And Persistence
No persistent state is stored. Successful calls briefly acquire native token handles and close them.

## Dependencies And Integration Points
It depends on Win32 advapi32/kernel32 and `Utilities.Win32Error`. `IntegratedNTLMAuthenticationProvider` uses it to decide whether guest login is enabled.

## Risks
Unexpected errors throw exceptions, so callers must isolate OS/policy issues. Passing an empty domain restricts behavior to local/default context. Correct token cleanup is important; `ImpersonateLoggedOnUser` is exposed but no helper reverts impersonation.

## Test Signals
No direct tests in this subset. Behavior requires Windows account-policy integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/LoginAPI.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/NetworkAPI.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/NetworkAPI.cs

## Purpose
`NetworkAPI.cs` wraps NetAPI user and group enumeration calls used by Windows-integrated authentication.

## Important APIs, Types, And Functions
It defines NetAPI constants and marshaled structs `USER_INFO_0`, `USER_INFO_1`, and `LOCALGROUP_USERS_INFO_0`. It P/Invokes `NetApiBufferFree`, `NetUserEnum`, `NetUserGetInfo`, and `NetUserGetLocalGroups`. Public helpers are `EnumerateGroups`, `EnumerateAllUsers`, `EnumerateEnabledUsers`, `IsUserExists`, and `EnumerateNetworkUsers`.

## Control Flow
Enumeration methods call NetAPI with preferred maximum buffer sizes, marshal returned arrays by pointer arithmetic, collect names, and free NetAPI buffers. `IsUserExists` calls `NetUserGetInfo` level 0 and handles success/user-not-found specially. `EnumerateNetworkUsers` filters enabled users by membership in local groups `Users`, `Administrators`, or `Guests`.

## State And Persistence
No persistent state is stored. Native buffers are allocated by NetAPI and freed with `NetApiBufferFree` when entries are returned.

## Dependencies And Integration Points
It depends on `Netapi32.dll`, marshaling, and `Utilities`. `IntegratedNTLMAuthenticationProvider` calls `IsUserExists`; server UI or account listing code may use the enumeration helpers.

## Risks
Some methods only free buffers when `entriesRead > 0`; NetAPI may return a non-zero buffer with zero entries in edge cases. Pointer arithmetic uses `ToInt64`, which is generally safe but manually maintained. Group name filtering is English/localized-name dependent. Network/domain users are not comprehensively represented by local NetUser calls.

## Test Signals
No direct tests in this subset. Windows account enumeration and guest fallback behavior require platform integration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/NetworkAPI.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.Kerberos.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.Kerberos.cs

## Purpose
`SSPIHelper.Kerberos.cs` adds Kerberos credential acquisition helpers to the shared SSPI helper.

## Important APIs, Types, And Functions
It exposes `AcquireKerberosCredentialsHandle(string serverPrincipalName)` and `AcquireKerberosCredentialsHandle(string serverPrincipalName, string domainName, string userName, string password)`, both funneled to a private nullable-auth overload.

## Control Flow
The credential method optionally marshals `SEC_WINNT_AUTH_IDENTITY`, calls `AcquireCredentialsHandle` with the provided server principal and package `"Kerberos"` for inbound/outbound credentials, frees the temporary auth structure, throws on non-`SEC_E_OK`, and returns a `SecHandle`.

## State And Persistence
Returned credential handles are native SSPI resources. The method itself persists no state and frees only the temporary auth buffer, not the returned credential.

## Dependencies And Integration Points
It depends on the partial `SSPIHelper` core definitions and secur32. It is available for Kerberos-capable GSS/SPNEGO integration even though this subset mainly tests NTLM.

## Risks
Callers must release returned credentials with the private `FreeCredentialsHandle` path where available; no public dispose wrapper is provided. Passing null domain/user/password through `GetWinNTAuthIdentity` can throw because it uses `.Length`, so the explicit-credential overload expects non-null strings.

## Test Signals
No tests in this subset cover Kerberos SSPI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.Kerberos.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.NTLM.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.NTLM.cs

## Purpose
`SSPIHelper.NTLM.cs` provides Windows SSPI NTLM credential acquisition and type 1/type 2/type 3 message helpers for client and server authentication.

## Important APIs, Types, And Functions
Public APIs include `AcquireNTLMCredentialsHandle`, `GetType1Message`, `GetType3Message`, `GetType2Message`, and `AuthenticateType3Message`. They use `SecHandle`, `SecBuffer`, `SecBufferDesc`, `AcquireCredentialsHandle`, `InitializeSecurityContext`, `AcceptSecurityContext`, and `FreeCredentialsHandle`.

## Control Flow
Credential acquisition optionally marshals explicit credentials, calls SSPI for package `"NTLM"`, frees the auth data, and returns a credential handle. Client type 1 creation acquires credentials, gets an initial security context token, then frees credentials. Type 3 creation feeds a type 2 token into `InitializeSecurityContext`. Server type 2 creation accepts a type 1 token with new inbound credentials. Authentication feeds the client's type 3 token into `AcceptSecurityContext` and returns true for `SEC_E_OK`, false for `SEC_E_LOGON_DENIED`, or throws for other SSPI errors.

## State And Persistence
Native client/server security contexts and credential handles are external resources. Buffers are allocated with unmanaged memory and disposed per call. The helper does not persist state itself.

## Dependencies And Integration Points
It depends on `SSPIHelper.cs`, `SecBuffer`, `SecBufferDesc`, and secur32. `IntegratedNTLMAuthenticationProvider` uses type 2 and type 3 server helpers. Client-side Windows authentication can use type 1/type 3 helpers.

## Risks
Credential and context ownership is manual. `GetType3Message` creates a `newContext` but returns only token bytes, leaving lifecycle expectations unclear. Explicit credential overloads can fail on null strings. Exceptions expose raw SSPI error codes rather than typed statuses except in the integrated provider wrapper.

## Test Signals
No direct tests use SSPI NTLM in this subset; NTLM cryptography tests cover the independent implementation, not Windows SSPI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.NTLM.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.cs

## Purpose
`SSPIHelper.cs` contains shared Win32 SSPI interop declarations and common helpers for security context initialization and context attributes.

## Important APIs, Types, And Functions
It defines `SecHandle`, `MAX_TOKEN_SIZE`, SSPI status constants, credential/context flags, `SEC_WINNT_AUTH_IDENTITY`, `SecPkgContext_SessionKey`, and P/Invokes `AcquireCredentialsHandle`, `InitializeSecurityContext`, `AcceptSecurityContext`, `QueryContextAttributes`, `FreeContextBuffer`, `FreeCredentialsHandle`, and `DeleteSecurityContext`. Public helpers are `GetInitialMessage`, `GetUserName`, `GetSessionKey`, and `GetAccessToken`.

## Control Flow
`GetInitialMessage` initializes a client security context with confidentiality and integrity flags and returns the output token. Attribute helpers query context name, session key, or access token and return null/zero on failure. `GetWinNTAuthIdentity` packages domain/user/password strings and lengths for SSPI credential acquisition.

## State And Persistence
The file persists no managed state. It allocates output buffers per call and returns native handles or token bytes. Session key bytes are copied from native memory; access tokens remain native handles owned by the SSPI context/caller contract.

## Dependencies And Integration Points
It is the base partial class for NTLM and Kerberos helper files. Integrated authentication providers use it to create, authenticate, inspect, and delete SSPI contexts.

## Risks
`QueryContextAttributes` allocations for strings/session keys may require `FreeContextBuffer`, but `GetUserName` and `GetSessionKey` do not free returned native buffers. `GetWinNTAuthIdentity` uses ANSI flag despite .NET strings and will throw if strings are null. `GetInitialMessage` disposes buffers manually and could leak if an exception is thrown before disposal. Error handling is exception-based.

## Test Signals
No direct SSPI helper tests are present. Behavior is indirectly required for Windows integrated NTLM/Kerberos authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBuffer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBuffer.cs

## Purpose
`SecBuffer.cs` defines managed wrappers for SSPI `SecBuffer` structures and unmanaged token/data buffers.

## Important APIs, Types, And Functions
It defines `SecBufferType` values `SECBUFFER_EMPTY`, `SECBUFFER_DATA`, and `SECBUFFER_TOKEN`, plus `SecBuffer : IDisposable` fields `cbBuffer`, `BufferType`, and `pvBuffer`. Constructors allocate by size or copy byte arrays. `Dispose` frees unmanaged memory and `GetBufferBytes` copies bytes back to managed arrays.

## Control Flow
Constructors allocate `Marshal.AllocHGlobal` and optionally `Marshal.Copy` input bytes. `GetBufferBytes` returns null for zero-length buffers or copies `cbBuffer` bytes from `pvBuffer`. `Dispose` frees `pvBuffer` if non-zero.

## State And Persistence
Each `SecBuffer` owns unmanaged memory until disposed. No persistent state is written.

## Dependencies And Integration Points
It depends on `System.Runtime.InteropServices` and is used by `SSPIHelper` NTLM/Kerberos context calls through `SecBufferDesc`.

## Risks
As a struct with unmanaged ownership, copying `SecBuffer` values can duplicate the pointer and make double-free or leak patterns easy. Constructors do not guard against null byte arrays. Callers must dispose explicitly even on exceptions.

## Test Signals
No direct tests. It is indirectly exercised by SSPI authentication paths when run on Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBuffer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBufferDesc.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBufferDesc.cs

## Purpose
`SecBufferDesc.cs` defines the SSPI `SecBufferDesc` wrapper used to pass one or more `SecBuffer` structures to secur32 APIs.

## Important APIs, Types, And Functions
`SecBufferDesc : IDisposable` has `SECBUFFER_VERSION`, `ulVersion`, `cBuffers`, and `pBuffers`. Constructors accept one `SecBuffer` or an array. `GetBufferBytes(int bufferIndex)` marshals a `SecBuffer` from the descriptor and returns its bytes. `Dispose` frees the descriptor array memory.

## Control Flow
The array constructor allocates unmanaged memory sized for all buffer structs and copies each `SecBuffer` struct into it. `GetBufferBytes` checks disposal, computes the indexed struct pointer, unmarshals it, and calls `SecBuffer.GetBufferBytes`. `Dispose` frees `pBuffers`.

## State And Persistence
It owns unmanaged memory for the descriptor's array of `SecBuffer` structs, not necessarily the pointed-to token buffers themselves. No persistent state is written.

## Dependencies And Integration Points
It depends on `SecBuffer` and marshaling. `SSPIHelper` uses it for `InitializeSecurityContext` and `AcceptSecurityContext` input/output buffers.

## Risks
It does not dispose the underlying `SecBuffer` instances; callers must free both descriptor and buffers. As a struct, copies can duplicate ownership of `pBuffers`. Bounds are not checked in `GetBufferBytes`, so invalid indexes can marshal arbitrary memory.

## Test Signals
No direct tests; behavior is covered only through SSPI calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/Structures/SecBufferDesc.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ThreadingHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/ThreadingHelper.cs

## Purpose
`ThreadingHelper.cs` exposes minimal kernel32 thread-handle functions needed by Win32 notify cancellation.

## Important APIs, Types, And Functions
The class P/Invokes `GetCurrentThreadId`, `OpenThread`, and `CloseHandle`.

## Control Flow
There is no additional managed control flow; callers directly invoke the native functions. `NTDirectoryFileSystem.NotifyChange` records the worker thread ID, and `Cancel` opens that thread and closes the handle after alerting or cancelling synchronous I/O.

## State And Persistence
No managed state is stored. Native thread handles returned by `OpenThread` must be closed by callers.

## Dependencies And Integration Points
It depends on kernel32 and is tightly coupled to `NTDirectoryFileSystem` notify/cancel behavior.

## Risks
The helper exposes raw handles and access masks, so callers must request correct permissions and always close handles. It is Windows-only and unguarded by platform checks.

## Test Signals
Indirectly exercised by `NTDirectoryFileSystemTests.TestCancel` on Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/ThreadingHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/Enums/GSSAttributeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/Enums/GSSAttributeName.cs

## Purpose
`GSSAttributeName.cs` defines the attribute keys that SMBLibrary GSS mechanisms and authentication providers can expose after authentication.

## Important APIs, Types, And Functions
The enum `GSSAttributeName` contains `AccessToken`, `DomainName`, `IsAnonymous`, `IsGuest`, `MachineName`, `OSVersion`, `SessionKey`, and `UserName`. The `IsGuest` member documents guest-account fallback access.

## Control Flow
The file has no executable control flow. Providers switch on enum values to return context attributes.

## State And Persistence
No state is stored. The enum is an API contract.

## Dependencies And Integration Points
It is used by `IntegratedNTLMAuthenticationProvider.GetContextAttribute` and likely other GSS/NTLM mechanisms to expose identity, token, and session-key attributes to SMB server session handling.

## Risks
Adding or reordering enum values can affect binary consumers if values are serialized or persisted elsewhere. `IntegratedNTLMAuthenticationProvider` handles most values but not `IsAnonymous`, so consumers should expect null for unsupported attributes.

## Test Signals
No direct tests. `LoginTests` validate authentication success/failure but do not query GSS attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/Enums/GSSAttributeName.cs -->
