# subset-b-010017 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DFSTest.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DFSTest.groovy

Purpose: Spock research fixture for DFS path resolution through `Session.resolver`, `SmbPath`, `DFSReferralV34`, and `SMB2GetDFSReferralResponse`. Important flow: all concrete scenarios are currently commented out, but they document intended root referral, domain referral, root link, and interlink resolution flows using a stubbed `Connection`, `SMBClient`, `StubResponder`, `SMB2IoctlResponse`, tree connect/disconnect packets, and synchronous `DirectFuture`.

State and persistence: no active test state; dormant helpers would model transient connection/session state and referral responses only. Dependencies are SMBJ connection/auth/event/security classes and SMB DFS referral message encoders. Integration risk is that DFS resolver behavior can regress without this file failing because executable tests are disabled. Test signal is therefore weak: it is useful as design documentation, not coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DFSTest.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DirectFuture.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DirectFuture.groovy

Purpose: tiny test helper implementing `java.util.concurrent.Future<V>` for already-computed SMB packet responses. API surface is constructor `DirectFuture(V contents)`, `get()`, timed `get(long, TimeUnit)`, `isDone()`, `cancel()`, and `isCancelled()`. Control flow is intentionally flat: both `get` methods return stored contents immediately; cancellation always fails and never changes state.

State and persistence: one in-memory `contents` field, no synchronization, no persistence, no timeout behavior. It integrates with DFS/connection stubs that expect `Connection.send` to return a `Future<SMB2Packet>`. Risks are that it cannot model cancellation, blocking, timeout, or exception behavior, so tests using it cover only happy synchronous response paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DirectFuture.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/SMB2GetDFSReferralResponseTest.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/SMB2GetDFSReferralResponseTest.groovy

Purpose: Spock parser tests for DFS referral response wire payloads. Important APIs are `SMB2GetDFSReferralResponse.read(SMBBuffer)`, `referralEntries`, `referralHeaderFlags`, and `DFSReferral.ServerType`. Control flow decodes fixed hex buffers and asserts parsed version, server type, flags, DFS path, alternate path, target path, TTL, special name, and expanded names.

State and persistence: no persisted state; each test constructs a fresh buffer and response object. Dependencies include `SMBBuffer` and DFS referral message classes. Integration points are SMB2 IOCTL DFS referral decoding and resolver inputs. Risks covered include version 3 domain referrals, version 4 root/link referrals, UTF-16 string offsets, null alternate/path fields, and header flags. Test signal is strong for known wire examples but narrow to one-entry responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/SMB2GetDFSReferralResponseTest.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/StubResponder.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/StubResponder.groovy

Purpose: FIFO response registry for SMB packet test stubs. API surface is `register(Class, SMB2Packet)` and `respond(Object)`. Control flow stores packet responses in a `Map<Class, Queue<SMB2Packet>>`; response lookup uses the exact runtime class of the request and returns `poll()` from that class queue.

State and persistence: in-memory mutable map of queues, no persistence and no concurrency control. It integrates with stubbed `Connection.send` implementations in DFS-style tests. Risks: exact-class matching means subclasses/interfaces are not supported; exhausted queues return `null` rather than a custom failure; unregistered classes throw `IllegalArgumentException`. Test signal is helper-level only, but it enables deterministic multi-packet flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/StubResponder.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdtyp/SecurityDescriptorSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdtyp/SecurityDescriptorSpec.groovy

Purpose: validates binary Windows security descriptor decode/encode. Important APIs/types are `SecurityDescriptor.read`, `SecurityDescriptor.write`, `SID.fromString`, `ACL`, `AceTypes.accessDeniedAce`, `AceTypes.accessAllowedAce`, `AccessMask`, `AceFlags`, `AceType`, and `SecurityDescriptor.Control`. Control flow decodes a fixed hex descriptor, checks owner/group SIDs, DACL revision, six ACEs, masks, inherited flags, padding handling, and null SACL, then builds an equivalent descriptor and asserts exact serialized bytes.

State and persistence: transient buffers only. Dependencies are SMB buffer utilities and MS-DTYP SID/ACL/ACE models. Integration risk is high because descriptor layout uses offsets, variable SID lengths, ACE padding, and endian-sensitive masks. Test signal is strong for a realistic DACL round trip, but it covers only these ACE classes and one control flag combination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdtyp/SecurityDescriptorSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2ErrorSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2ErrorSpec.groovy

Purpose: tests `SMB2Error.read` handling of empty error data. It builds minimal `SMBBuffer` payloads with status structure fields and zero byte count. One case includes the trailing reserved error-data byte; the Windows 10 1709 case omits it.

State and persistence: no state beyond a fresh header and buffer. Dependencies are `SMB2PacketHeader`, `SMB2Error`, and `SMBBuffer`. Integration point is SMB2 error packet decoding from servers that vary in reserved-byte emission. Risk covered is parser over-read or failure on zero-length error payloads. Test signal is narrow but important for compatibility with real Windows behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2ErrorSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2MessageFlagSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2MessageFlagSpec.groovy

Purpose: validates conversion from raw SMB2 flag bitmask to `EnumSet<SMB2MessageFlag>`. Control flow passes `0x10000001` through `EnumWithValue.EnumUtils.toEnumSet` and asserts exactly `SMB2_FLAGS_DFS_OPERATIONS` and `SMB2_FLAGS_SERVER_TO_REDIR`.

State and persistence: none. Dependencies are `SMB2MessageFlag` and shared enum-with-value utilities. Integration point is header flag parsing and serialization. Risk covered is high-bit flag handling in a `long` bitmask and avoiding accidental extra flags. Test signal is focused and small; it does not cover reverse serialization or unknown bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2MessageFlagSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2PacketHeaderSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2PacketHeaderSpec.groovy

Purpose: verifies SMB2 header writing of credit request for selected dialects. Important APIs are `SMB2PacketHeader.setCreditRequest`, `setCreditCharge`, `setDialect`, `setMessageType`, and `writeTo(SMBBuffer)`. Control flow writes a negotiate header for SMB 2.1, 2.0.2, and 2XX, seeks to byte offset 14, and checks the 16-bit credit request value.

State and persistence: no persisted state; one header and buffer per iteration. Integration point is SMB2 wire header generation. Risk covered is dialect-dependent header field placement, especially credit request versus channel sequence behavior. Test signal is good for this field but not full header layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/SMB2PacketHeaderSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/AbstractPacketReadSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/AbstractPacketReadSpec.groovy

Purpose: shared Spock base for SMB2 message parser tests. It owns a `@Shared SMB2MessageConverter` and exposes `convert(byte[] bytes)`, which wraps bytes in `SMB2PacketData` and delegates to `converter.readPacket(null, packetData)`.

State and persistence: shared converter state only for the test instance; no persistence. Dependencies are `SMB2MessageConverter`, `SMB2PacketData`, and Spock. Integration point is every subclass that decodes raw captured SMB2 packets. Risk is that all parser specs inherit the same null request-packet context, so they primarily cover response parsing paths that do not need request correlation. Test signal is infrastructural.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/AbstractPacketReadSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponseSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponseSpec.groovy

Purpose: tests parsing of `SMB2ChangeNotifyResponse` packets. It decodes a captured response and asserts five `FileNotifyInfo` file names, including alternate data stream style names and a metadata name with unusual UTF-16 content. A second captured packet with `STATUS_NOTIFY_CLEANUP` asserts an empty notification list.

State and persistence: transient packet data only. Dependencies are `ByteArrayUtils`, `AbstractPacketReadSpec`, and change-notify model classes. Integration point is watch/change notification behavior for SMB shares. Risks covered include linked notification records, Unicode file-name decoding, cleanup status handling, and zero-output cases. Test signal is strong for parser resilience against real server payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ChangeNotifyResponseSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2CreateResponseSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2CreateResponseSpec.groovy

Purpose: validates `SMB2CreateResponse` decoding. One captured packet lacks maximal content and asserts `FileTime` creation time plus persistent handle bytes from `fileId`. Another captured packet has `STATUS_PENDING` and asserts the converter still returns an `SMB2CreateResponse` with the pending status code.

State and persistence: no state beyond parsed packets. Dependencies include `FileTime`, `NtStatus`, `ByteArrayUtils`, and the shared converter base. Integration point is file open/create response parsing and async/pending create semantics. Risks covered are incomplete context payloads, handle extraction, timestamp conversion, and non-success status packets still mapping to the expected message type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2CreateResponseSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponseSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponseSpec.groovy

Purpose: exercises query-directory response parsing from a large captured SMB2 packet. It converts bytes to `SMB2QueryDirectoryResponse`, then decodes `outputBuffer` via `FileInformationFactory.parseFileInformationList` using the `FileIdBothDirectoryInformation` decoder. Assertions include class type, 18 entries, dot and dot-dot names, a normal child entry, and a later garbled-looking Unicode name.

State and persistence: transient buffers only. Dependencies are SMB2 converter, MS-FSCC file-information decoders, and byte utilities. Integration point is directory listing over SMB. Risks covered include chained variable-size directory records, alignment, output-buffer slicing, and Unicode decoding. Test signal is strong for a real-world payload, but expected names are sparse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2QueryDirectoryResponseSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadRequestSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadRequestSpec.groovy

Purpose: validates exact SMB2 read request serialization for byte-range lock compatibility. Important APIs are `SMB2ReadRequest` constructor, `getHeader().setMessageId`, and `write(SMBBuffer)`. Control flow builds file-id halves from hex, sets dialect/session/tree/message IDs, serializes a read at offset 0 with max payload 15, and compares both payload body and whole packet against expected hex.

State and persistence: no persisted state. Dependencies are `SMB2FileId`, `SMB2Dialect`, `SMBBuffer`, and byte utilities. Integration point is read request wire generation. Risk covered is requesting more than the exact user range, which can conflict with server byte-range locks. Test signal is precise but currently only one active row; a larger payload row is commented out.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadRequestSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadResponseSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadResponseSpec.groovy

Purpose: tests SMB2 read response decoding. It parses a large captured read response containing log-like byte data and asserts the decoded `dataLength` is 21401. It also parses an EOF response and verifies the header status is `NtStatus.STATUS_END_OF_FILE.value`.

State and persistence: transient parsed packets only. Dependencies are `NtStatus`, `ByteArrayUtils`, and the shared packet converter. Integration point is file read response handling, especially large payload lengths and EOF status propagation. Risks covered include data-offset/data-length interpretation, payload preservation independent of textual contents, and correct non-success status decoding. Test signal is good for these two response shapes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2ReadResponseSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponseSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponseSpec.groovy

Purpose: validates `SMB2TreeConnectResponse` parsing from captured bytes. The test asserts empty share capabilities, maximal access mask conversion to `AccessMask` enum set from `0x001f01ff`, share flags conversion from `0x800`, and disk-share classification.

State and persistence: none beyond parsed response. Dependencies are `AccessMask`, `SMB2ShareCapabilities`, `SMB2ShareFlags`, `EnumWithValue`, and the converter base. Integration point is share connection setup and capability/access interpretation. Risks covered include access-mask enum conversion, share-flag parsing, and correct share-type helper behavior. Test signal is focused on one normal tree-connect response.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2TreeConnectResponseSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2WriteResponseSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2WriteResponseSpec.groovy

Purpose: tests decoding of `SMB2WriteResponse` from raw SMB2 bytes. Control flow uses the shared converter and asserts the message class and `bytesWritten == 8192`.

State and persistence: no state. Dependencies are byte parsing utilities and SMB2 message converter infrastructure. Integration point is SMB write completion handling. Risk covered is correct extraction of the count field from the write response body and class dispatch from command code. Test signal is narrow but directly protects upload/write accounting behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/mssmb2/messages/SMB2WriteResponseSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/functions/NtlmFunctionsSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/functions/NtlmFunctionsSpec.groovy

Purpose: cryptographic test vectors for NTLMv1/v2 helper functions across multiple security providers. Important types include `NtlmV1Functions`, `NtlmV2Functions`, `NtlmFunctions`, `TargetInfo`, `NtlmChallenge`, `PredictableRandom`, `JceSecurityProvider`, `BCSecurityProvider`, and Bouncy Castle provider. Control flow checks LMOWFv1, RC4 encryption, MS-NLMP NTLMv1 examples, NTLMv2 hash/response temp/computed response examples, deterministic client challenge bytes, and target-info parsing.

State and persistence: a static predictable random source supplies deterministic bytes; no persistence. Dependencies are crypto providers and official protocol example data. Integration point is authentication, signing/sealing key material, and NTLM response generation. Risks are high: provider-specific digest/cipher behavior and deterministic test vectors must remain exact. Test signal is strong for spec examples, limited to known inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/functions/NtlmFunctionsSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmChallengeSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmChallengeSpec.groovy

Purpose: validates decoding of NTLM challenge messages supplied by `SampleMessages`. It constructs `NtlmChallenge`, reads byte arrays through the message API, and asserts fields for NTLMv1, NTLMv1 with client challenge/extended session security, and NTLMv2. Important checks include target name, negotiate flags, server challenge bytes, target info, and version data.

State and persistence: test data is held in the `SampleMessages` trait; parsing is per-test. Dependencies are NTLM message types and buffer utilities. Integration point is SPNEGO/NTLM authentication challenge handling. Risks covered include security-buffer offsets, negotiated flag sets, target-info AV pairs, and version decoding. Test signal is strong for protocol sample coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmChallengeSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmNegotiateFlagSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmNegotiateFlagSpec.groovy

Purpose: parameterized Spock tests for NTLM negotiate flag bit handling. It verifies individual `NtlmNegotiateFlag` values are detected in raw integer flag words and that enum sets are serialized back into the expected flag values.

State and persistence: none. Dependencies are NTLM flag enums and enum-with-value utilities. Integration point is NTLM negotiate/challenge/authenticate message parsing and writing. Risks covered include bit position mistakes, high-bit signedness issues, and divergence between parse and encode paths. Test signal is focused on flags rather than full messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/NtlmNegotiateFlagSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/SampleMessages.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/SampleMessages.groovy

Purpose: shared Spock/Groovy fixture containing NTLM protocol sample data. It defines Windows version metadata, expected negotiate flag sets for NTLMv1, NTLMv1 with client challenge, and NTLMv2, plus byte arrays for sample challenge messages and response computations.

State and persistence: constant in-memory fixture fields only. Dependencies are `WindowsVersion`, `NtlmNegotiateFlag`, enum sets, and byte-array literals. Integration point is reused by NTLM message/function specs to keep protocol vectors consistent. Risks are fixture drift and accidental mutation because Groovy `def` fields can be mutable. Test signal is indirect: this file has no assertions but is critical for reproducible authentication tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/ntlm/messages/SampleMessages.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/protocol/commons/buffer/BufferSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/protocol/commons/buffer/BufferSpec.groovy

Purpose: core buffer behavior tests for `Buffer.PlainBuffer`. It covers unsigned integer read/write for multiple sizes and both endian modes, out-of-range write exceptions, too-large uint64 read exceptions, string write/read using named charsets, and `InputStream` unsigned-byte behavior.

State and persistence: each case uses a fresh in-memory buffer. Dependencies are `Endian`, `Buffer`, Java `Charset`, and Spock data tables. Integration point is nearly all SMB/MS protocol serialization and parsing. Risks covered include endian mistakes, unsigned range validation, overflow handling, charset length handling, and sign extension when reading bytes via stream APIs. Test signal is broad and foundational for wire-format correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/protocol/commons/buffer/BufferSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/JceMessageDigestSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/JceMessageDigestSpec.groovy

Purpose: verifies that `JceSecurityProvider` can load an MD4 message digest from the regular JRE/JDK configuration used by tests. The test constructs the provider and requests MD4 digest support.

State and persistence: no state beyond provider lookup. Dependencies are Java Cryptography Architecture and SMBJ security provider abstraction. Integration point is NTLM hash generation, which needs MD4. Risk covered is missing provider registration or runtime environment incompatibility. Test signal is environment-sensitive and intentionally small; failures point to provider availability rather than algorithm correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/JceMessageDigestSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256Spec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256Spec.groovy

Purpose: validates counter-mode HMAC-SHA256 key derivation. The spec instantiates `KDFCounterHMacSHA256` and checks derived bytes for fixed key/label/context/length inputs against known expected output.

State and persistence: no persistent state; all inputs are in-memory byte arrays. Dependencies are JCE HMAC support and SMBJ derivation-function implementation. Integration point is SMB 3.x signing/encryption key derivation. Risks covered include counter placement, label/context concatenation, output truncation, and provider-specific HMAC behavior. Test signal is compact but high-value because a single byte mismatch breaks interoperability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256Spec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/SMBClientSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/SMBClientSpec.groovy

Purpose: tests `SMBClient` connection caching and lifecycle behavior using `StubTransportLayerFactory` and `DefaultPacketProcessor`. It asserts the same host/port reuses a connection, different ports or hosts produce different connections, closed connections are not reused, and multiple logical opens to the same host do not prematurely disconnect the underlying connection.

State and persistence: state is the client's in-memory connection table/reference counts; no persistence. Dependencies are SMB client config and test transport stubs. Integration point is connection pooling used by higher-level session/share APIs. Risks covered include stale closed connections, host/port keying, and disconnect reference management. Test signal is good for cache semantics without real network I/O.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/SMBClientSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/common/SmbPathSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/common/SmbPathSpec.groovy

Purpose: Spock tests for SMBJ common UNC path parsing and manipulation. It covers `SmbPath.parse`, constructor behavior, equality/hashCode, UNC rendering, host/share comparison, slash normalization, child path construction, and parent calculation.

State and persistence: immutable path values only. Dependencies are the common `SmbPath` model and Spock tables. Integration point is client/session/share routing and DFS path resolution. Risks covered include mixed slash styles, case/host/share equality semantics, missing path components, and parent calculations at root/share boundaries. Test signal is broad for the older SMBJ path model but separate from the NIO `smbfs.SmbPath` tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/common/SmbPathSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/ConnectionSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/ConnectionSpec.groovy

Purpose: integration-style tests for connection close, negotiation, authentication flags, error propagation, and DFS resolver selection. It builds `SMBClient` with stub transport/authentication, records `SMBEventBus` events, and asserts forced close emits only `ConnectionClosed`, normal close emits `SessionLoggedOff` then `ConnectionClosed`, unsupported negotiation throws `SMBApiException`, tree-connect session expiration is surfaced, authenticated sessions are not guests, and DFS resolver is enabled only when config and negotiated capabilities allow it.

State and persistence: in-memory event list, connection/session state, and config flags. Dependencies include packet processors, stub auth/transport, `SMBEventBus`, `NtStatus`, negotiated capabilities, and `DFSPathResolver`. Risks covered are lifecycle ordering, status-code propagation, and capability-gated resolver wiring.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/ConnectionSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SMBSessionBuilderSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SMBSessionBuilderSpec.groovy

Purpose: tests session setup construction and authentication negotiation paths in `SMBSessionBuilder`. It uses stubbed connection/session setup responses and authenticators to verify selected authentication context, guest/anonymous flags, and session construction behavior around SMB2 session setup.

State and persistence: transient session-builder state, selected auth context, and response fields; no persistence. Dependencies are SMB session setup messages, auth interfaces, security providers, connection stubs, and Spock mocks. Integration point is login/authentication before share access. Risks covered include incorrect session flags, authenticator selection, and session-id propagation. Test signal is important because session establishment controls subsequent signing/encryption and permissions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SMBSessionBuilderSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SequenceWindowSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SequenceWindowSpec.groovy

Purpose: tests SMB2 message-id/credit sequence allocation. It exercises `SequenceWindow` behavior for reserving available credits, expanding with granted credits, exhaustion behavior, and window accounting.

State and persistence: in-memory counters/window state only. Dependencies are the connection sequence-window class and Spock. Integration point is SMB2 credit-based flow control and message-id assignment for all requests. Risks covered include off-by-one IDs, over-allocation, failure to honor credits, and incorrect available-count reporting. Test signal is focused and important for concurrency and high-throughput SMB operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/SequenceWindowSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/BufferByteChunkProviderSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/BufferByteChunkProviderSpec.groovy

Purpose: validates `BufferByteChunkProvider` over `Buffer.PlainBuffer`. It checks empty availability, available-byte counting after writes, full reads into arrays, partial reads when fewer bytes remain than requested, and no-op behavior when nothing is left.

State and persistence: provider consumes an in-memory protocol buffer; no persistence. Dependencies are `Buffer`, `Endian`, and byte chunk provider APIs. Integration point is SMB write/upload streaming from protocol buffers. Risks covered include read-position advancement, partial final chunk handling, and zero-byte reads. Test signal is focused on buffer-backed chunk semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/BufferByteChunkProviderSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/ByteBufferByteChunkProviderSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/ByteBufferByteChunkProviderSpec.groovy

Purpose: tests `ByteBufferByteChunkProvider` writing chunks to an output stream. It uses random byte buffers, duplicate buffers for expected comparison, and verifies one full chunk, partial chunk writes, and availability after consuming the first chunk from a buffer larger than `ByteChunkProvider.CHUNK_SIZE`.

State and persistence: in-memory `ByteBuffer` position/remaining state only. Dependencies are Java NIO buffers and SMBJ byte chunk provider APIs. Integration point is file upload/write request chunking from `ByteBuffer`. Risks covered include position mutation, chunk-size boundaries, and correct remaining-byte reporting. Test signal is good for normal buffer-backed streaming.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/ByteBufferByteChunkProviderSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/FileByteChunkProviderSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/FileByteChunkProviderSpec.groovy

Purpose: validates file-backed chunk streaming. It creates temporary files with random bytes and checks full chunk output, partial chunk output, availability after the first chunk when data remains, and starting reads at a supplied file offset.

State and persistence: temporary filesystem files are created for test data; provider tracks file input position. Dependencies are Java `File`, random byte generation, output streams, and `ByteChunkProvider.CHUNK_SIZE`. Integration point is SMB upload/write from local files. Risks covered include file-offset seek behavior, partial final chunks, available-byte accounting, and stream cleanup. Test signal is useful but random inputs make failures less directly inspectable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/FileByteChunkProviderSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/InputStreamByteChunkProviderSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/InputStreamByteChunkProviderSpec.groovy

Purpose: tests lifecycle behavior of `InputStreamByteChunkProvider`. It constructs the provider around a Spock `InputStream` mock, closes the provider, and verifies the underlying stream is closed exactly once.

State and persistence: provider owns an input stream reference; no persistence. Dependencies are Java `InputStream` and Spock mocks. Integration point is SMB upload/write from arbitrary streams. Risk covered is resource leak on provider close. Test signal is narrow; it does not cover chunk reading, partial reads, or exception propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/io/InputStreamByteChunkProviderSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/paths/SymlinkPathResolverSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/paths/SymlinkPathResolverSpec.groovy

Purpose: tests symlink-aware path resolution behavior. It exercises `SymlinkPathResolver` with mocked/stubbed share and file-link data to verify how symbolic-link targets are transformed into SMB paths and how relative/absolute target forms are handled.

State and persistence: transient path-resolution state only; no persistence. Dependencies are SMBJ path/share abstractions, symlink/reparse-point models, and Spock. Integration point is resolving server-side symlinks before file operations. Risks covered include incorrect target normalization, loops or unresolved links, and mixing UNC-style separators. Test signal is important for path correctness where servers expose symlinks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/paths/SymlinkPathResolverSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/server/StubSmbServer.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/server/StubSmbServer.groovy

Purpose: local SMB server fixture used by transport/integration tests. It opens a listening socket, accepts client connections, reads/writes direct TCP SMB packets, and delegates packet handling to configurable responder logic for negotiate/session/tree-connect style flows.

State and persistence: owns socket/server-thread lifecycle, port, running flag, and packet responder state; no disk persistence. Dependencies are Java networking, SMB packet/message classes, and test packet processors. Integration point is tests that need a real TCP connection without a real SMB server. Risks include thread/socket leaks, race conditions around startup/shutdown, and incomplete protocol coverage. Test signal is fixture-level and valuable for transport tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/server/StubSmbServer.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileOutputStreamSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileOutputStreamSpec.groovy

Purpose: integration-style tests for SMBJ `File` output stream behavior. Setup authenticates through a stub transport, opens a remote file with create/write options, and uses packet processor callbacks to return create and write responses. Tests verify closing after a `PrintWriter` close and closure after Groovy `withWriter`.

State and persistence: transient SMB connection/session/share/file state and a `ByteArrayOutputStream` sink; no real remote persistence. Dependencies include SMB create/write messages, `SMBClient`, `SmbConfig`, auth context, stub transport/auth, and `DiskShare`. Risks covered include stream/writer close ordering, file-handle close behavior, and write response handling. Test signal is good for high-level output-stream lifecycle but not broad write error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileOutputStreamSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileReadSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileReadSpec.groovy

Purpose: integration-style tests for SMBJ remote file reads. Setup builds deterministic file bytes and expected digest, opens a file through a stub SMB transport, and responds to `SMB2ReadRequest` with slices from the backing byte array. Tests cover direct `read` loops, buffer offsets, input-stream reads, IBM JVM mode behavior, input-stream buffer offsets, and `skip` before/after reading.

State and persistence: transient file bytes, digest state, connection/session/share/file state. Dependencies include SMB read/create messages, `ByteArrayUtils`, digest streams, stub auth/transport, and packet processors. Risks covered include offset arithmetic, EOF handling, buffer-offset writes, skip semantics, and read payload sizing. Test signal is strong for high-level read APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/FileReadSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/RingBufferSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/RingBufferSpec.groovy

Purpose: comprehensive tests for `RingBuffer` write/read behavior. It covers writing whole arrays, writing selected ranges, invalid range errors, single-byte appends, appending to existing data, wrap-around after reads, full-buffer exceptions, fixed-size reads, zero-length reads, reads larger than available data, size accounting, reuse after reads, and write-position wrap-around edge cases.

State and persistence: in-memory circular buffer state (`read`/`write` positions and size); no persistence. Dependencies are only Spock and byte arrays. Integration point is SMB share stream buffering. Risks covered are classic circular-buffer off-by-one, overflow, under-read, wrap-around split-copy, and zero-byte behavior. Test signal is strong for buffer correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/share/RingBufferSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportSpec.groovy

Purpose: verifies that `SMBClient` can connect through `AsyncDirectTcpTransportFactory` to the local `StubSmbServer`. Setup starts the stub server; cleanup stops it. The test builds an `SMBClient` with async transport and connects to localhost on the server port.

State and persistence: live local socket/server state during the test; no disk persistence. Dependencies are async TCP transport, SMB client config, and stub server fixture. Integration point is transport-layer connection establishment. Risks covered include async transport factory wiring, socket connect behavior, and server fixture compatibility. Test signal is limited to connect success, not sustained I/O or error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/transport/tcp/async/AsyncDirectTcpTransportSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenInitSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenInitSpec.groovy

Purpose: tests SPNEGO `NegTokenInit` ASN.1 parsing/writing. It reads fixture bytes for negotiate-token init messages and asserts mechanism OIDs, mechanism token payloads, and other negotiation fields, then validates serialization where covered.

State and persistence: fixture bytes loaded from test resources and transient ASN.1 token objects. Dependencies are SPNEGO token classes, buffer utilities, and OID/ASN.1 handling. Integration point is authentication negotiation before NTLM challenge/response. Risks covered include DER length/tag parsing, OID order, optional field handling, and mechanism-token preservation. Test signal is good for known SPNEGO handshakes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenInitSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenTargSpec.groovy -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenTargSpec.groovy

Purpose: tests SPNEGO `NegTokenTarg` parsing with an embedded NTLM challenge. It loads `spnego/negTokenTarg_ntlmchallenge`, reads the token from a little-endian plain buffer, extracts the response token, and feeds it to `NtlmChallenge` for validation.

State and persistence: resource bytes only. Dependencies are `NegTokenTarg`, `NtlmChallenge`, and protocol buffers. Integration point is the handoff from SPNEGO target token parsing to NTLM challenge decoding. Risks covered include ASN.1 response-token extraction, nested token boundaries, and compatibility with NTLM challenge parser. Test signal is focused on one real fixture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/spnego/NegTokenTargSpec.groovy -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/test/PredictableRandom.java -->
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/test/PredictableRandom.java

Purpose: deterministic `Random` subclass for tests that need reproducible nonce/challenge bytes. API surface is `init(byte[] bytes)` to set the source byte array and reset index, plus overridden `nextBytes(byte[] bytes)` that copies sequential bytes into the destination.

State and persistence: mutable `randomBytes` and `idx` fields in memory only. Dependencies are `java.util.Random`. Integration point is NTLM crypto tests where client challenges must match protocol examples. Risks include no bounds checks beyond array copy behavior, no thread-safety, and deterministic output unsuitable outside tests. Test signal is helper-level; correctness is inferred through NTLM vector tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/test/PredictableRandom.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/DFSPathTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/DFSPathTest.java

Purpose: JUnit tests for `DFSPath` parsing and path matching. It constructs DFS paths from UNC-style strings and validates host/share/path components, root/link style interpretation, and matching behavior used by referral caches.

State and persistence: immutable path values only. Dependencies are JUnit assertions and DFS path model classes. Integration point is DFS referral lookup and path-prefix comparison. Risks covered include separator handling, case/path component boundaries, and incorrect root/share extraction. Test signal is focused on DFS path semantics independent of network behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/DFSPathTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/ReferralCacheNodeTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/ReferralCacheNodeTest.java

Purpose: tests DFS referral cache node behavior. It validates adding child referral nodes, resolving matching paths, choosing target referrals, and cache-tree traversal semantics for DFS roots and links.

State and persistence: in-memory referral cache tree only; no persistence. Dependencies include DFS path/referral/cache types and JUnit. Integration point is `DFSPathResolver` caching of referral responses to avoid repeated network IOCTLs. Risks covered include prefix matching, parent/child lookup, stale or wrong referral target selection, and path normalization. Test signal is important for DFS cache correctness but isolated from live SMB sessions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdfsc/ReferralCacheNodeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/MsDataTypesTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/MsDataTypesTest.java

Purpose: JUnit tests for Microsoft data type helpers. It verifies serialization/parsing behavior for small MS-DTYP primitives used by SMB protocol structures, such as UUID/GUID, file time, or numeric wrappers depending on implementation coverage.

State and persistence: in-memory values and buffers only. Dependencies are MS-DTYP classes and JUnit assertions. Integration point is protocol structure parsing throughout SMBJ. Risks covered include endian/layout mismatches and conversion errors in shared primitive types. Test signal is foundational but scoped to representative cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/MsDataTypesTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/SIDTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/SIDTest.java

Purpose: tests Windows SID string/binary conversion. It asserts `SID.fromString` and serialization/parsing behavior for known SID forms, including identifier authority and sub-authority components.

State and persistence: immutable SID values and transient buffers. Dependencies are `SID`, JUnit, and buffer utilities. Integration point is security descriptor parsing, ACL entries, and access-control display. Risks covered include authority width, sub-authority endian handling, invalid string forms, and equality semantics. Test signal is targeted and important for security descriptor correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msdtyp/SIDTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/mserref/NtStatusTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/mserref/NtStatusTest.java

Purpose: parameterized tests for NT status severity classification. It checks selected `NtStatus` values report `STATUS_SEVERITY_SUCCESS` or `STATUS_SEVERITY_ERROR` as expected.

State and persistence: enum constants only. Dependencies are JUnit 5 parameterized tests and `NtStatus`. Integration point is error handling and exception mapping across SMB responses. Risks covered include incorrect severity-bit masking, which would misclassify protocol statuses. Test signal is small but useful for status helper correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/mserref/NtStatusTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msfscc/fileinformation/FileAllInformationTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/msfscc/fileinformation/FileAllInformationTest.java

Purpose: tests parsing or composition of `FileAllInformation`, the aggregate MS-FSCC file information structure. It verifies that substructures such as basic, standard, internal, EA, access, position, mode, alignment, name, and related fields are read with correct offsets.

State and persistence: transient byte buffers and model objects. Dependencies are MS-FSCC file information classes and JUnit. Integration point is SMB query-info responses. Risks covered include field ordering, padding, variable-length names, and substructure boundaries. Test signal is important because this aggregate structure is easy to misalign.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/msfscc/fileinformation/FileAllInformationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/ShareSourceImplTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/ShareSourceImplTest.java

Purpose: tests `ShareSourceImpl`, the NIO filesystem bridge that supplies SMB share handles. It uses mocks to validate share retrieval, reuse, and close/disconnect behavior around `DiskShare` or session interactions.

State and persistence: in-memory mocked client/session/share references; no persistence. Dependencies are JUnit, Mockito, and smbfs/share abstractions. Integration point is `SmbFileSystem` access to SMBJ sessions and shares. Risks covered include leaking shares, returning stale references, and incorrect close delegation. Test signal is focused on adapter lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/ShareSourceImplTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbDirectoryStreamTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbDirectoryStreamTest.java

Purpose: tests NIO directory stream behavior for SMB paths. It validates iteration over directory entries, filter behavior, close behavior, and exception handling around an SMB directory listing source.

State and persistence: transient mocked directory entries and stream closed state. Dependencies are Java NIO `DirectoryStream`, JUnit, Mockito, and smbfs path classes. Integration point is `Files.newDirectoryStream` over SMB shares. Risks covered include iterator reuse, close idempotence, filter application, and translating SMB/listing errors to NIO expectations. Test signal is useful for filesystem-provider compliance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbDirectoryStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemProviderTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemProviderTest.java

Purpose: comprehensive JUnit/Mockito tests for the NIO `SmbFileSystemProvider`. It covers missing filesystem errors, invalid share URIs, filesystem creation through a factory, parsing authentication context from URI credentials, environment override precedence, `char[]` passwords, invalid password types, duplicate filesystem keys, password-insensitive keying, unrelated filesystem creation, lookup/removal, and path/root resolution from URIs.

State and persistence: provider maintains an in-memory filesystem registry keyed by URI identity; mocks capture auth contexts. Dependencies are Java NIO exceptions, URI parsing, `SMBClient.DEFAULT_PORT`, Mockito captors, and provider constants. Integration point is `FileSystems.newFileSystem`/`getFileSystem`/`getPath`. Risks covered include credential parsing, URL decoding, password leakage into keys, registry lifecycle, and path extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemProviderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemTest.java

Purpose: tests the NIO `SmbFileSystem` implementation. It validates root/path construction, separator behavior, open/closed state, provider/share accessors, supported file attribute views, and path factory behavior.

State and persistence: in-memory filesystem instance with close state and associated share source/provider references; no disk persistence. Dependencies are Java NIO `FileSystem` contracts, JUnit, Mockito, and smbfs classes. Integration point is Java `Files` APIs over SMB. Risks covered include NIO contract violations, incorrect separator/root behavior, and lifecycle misuse after close. Test signal is broad for filesystem object semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbFileSystemTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbPathTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbPathTest.java

Purpose: detailed NIO `SmbPath` contract tests. It covers equality across filesystem/root/name combinations, string rendering with backslashes, parsing slash/backslash inputs, invalid empty path elements, filesystem/root/file-name/parent/name-count/name/subpath accessors, absolute detection, startsWith/endsWith, resolve, resolveSibling, relativize, and invalid relativize cases.

State and persistence: immutable path instances backed by an in-memory `SmbFileSystem`; no persistence. Dependencies are JUnit 5, Guava `EqualsTester`, Mockito, and Java NIO path semantics. Integration point is all smbfs path operations used by `Files`. Risks covered include absolute/relative mixing, root boundaries, separator normalization, parent/subpath indexing, and relativize correctness. Test signal is strong.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbfs/SmbPathTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/SmbConfigTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/SmbConfigTest.java

Purpose: tests `SmbConfig` builder validation. It verifies default config creation and asserts invalid combinations throw, especially requiring signing while disabling signing and disabling signing while allowing SMB 3.x dialects.

State and persistence: immutable config objects only. Dependencies are JUnit and SMBJ config/dialect/signing settings. Integration point is client construction and security policy enforcement. Risks covered include accepting insecure or contradictory configuration that would later fail negotiation or weaken session security. Test signal is small but important for early validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/SmbConfigTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ConnectionTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ConnectionTest.java

Purpose: JUnit tests for lower-level `Connection` behavior. It uses stub transport/packet processors to validate connection setup, negotiated protocol data, send/receive behavior, close behavior, or error propagation depending on scenario coverage.

State and persistence: in-memory connection state, negotiated protocol, sequence/window state, and stub transport connectivity. Dependencies are SMBJ connection classes, test packet processors, stub auth/transport, and JUnit/Mockito. Integration point is the central object used by sessions and shares. Risks covered include incorrect lifecycle flags, stale transport state, and status propagation. Test signal complements the Spock `ConnectionSpec` with Java-side coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ConnectionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketEncryptorTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketEncryptorTest.java

Purpose: tests SMB packet encryption behavior. It validates `PacketEncryptor` output headers/body transformation using fixed keys, nonce/signature fields, dialect/session context, and expected encrypted/decrypted packet data.

State and persistence: transient crypto keys and packet buffers only. Dependencies are SMB3 transform header/message classes, security provider crypto primitives, and JUnit. Integration point is SMB 3.x encrypted sessions. Risks covered include nonce handling, transform header fields, algorithm selection, session-id binding, and ciphertext/authentication tag correctness. Test signal is high-value for interoperability and security.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketEncryptorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketSignatoryTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketSignatoryTest.java

Purpose: tests SMB packet signing. It verifies signature generation and verification behavior for selected dialect/security settings, using known packet data and signing keys.

State and persistence: in-memory keys and packets only. Dependencies are signing algorithms, SMB2 headers, security provider, and JUnit. Integration point is message integrity for authenticated SMB sessions. Risks covered include zeroing the signature field before signing, dialect-specific algorithm selection, session binding, and verification failures. Test signal is important for security regressions but limited to fixture vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/PacketSignatoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ProtocolNegotiatorTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ProtocolNegotiatorTest.java

Purpose: tests SMB protocol negotiation. It validates dialect selection, negotiate request/response handling, negotiated protocol fields, capabilities, signing/encryption requirements, and unsupported dialect/status outcomes.

State and persistence: transient negotiation inputs and resulting negotiated protocol object. Dependencies are SMB2 negotiate messages, dialect enums, config, security mode/capability fields, and JUnit/Mockito. Integration point is the first step of every SMB connection. Risks covered include choosing an unsupported dialect, misreading max read/write/transact sizes, mishandling server capabilities, and weak signing policy. Test signal is central for connection compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/connection/ProtocolNegotiatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/session/SessionTest.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/session/SessionTest.java

Purpose: JUnit tests for session/share/file behavior. It asserts share names cannot contain backslashes and verifies `Session.open` defaults to `SMB2CreateDisposition.FILE_OPEN` when no create disposition is provided by inspecting the `SMB2CreateRequest` passed to a mocked share.

State and persistence: session object with mocked connection/share responses; no persistence. Dependencies are session, disk share/file open APIs, SMB create messages, and Mockito answers. Integration point is application-level share and file open calls. Risks covered include invalid share path injection and accidental default create-disposition changes that could create/truncate files. Test signal is focused but protects a dangerous default.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/session/SessionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/PacketProcessor.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/PacketProcessor.java

Purpose: test packet-processing abstraction and default SMB response generator. API surface includes `PacketProcessor.process(SMB2Packet)`, `NoOpPacketProcessor`, wrapper support for lambdas/custom processors, and `DefaultPacketProcessor` handling negotiate, session setup, logoff, tree connect, tree disconnect, and fallback error responses.

State and persistence: stateless processors except wrapper delegate references. Dependencies are SMB2 packet/message classes, `NtStatus`, dialect/capability fields, and security-mode/session setup data. Integration point is stub transport and high-level client tests. Risks include default responses diverging from what client setup expects, hiding errors with overly permissive responses, and incomplete command coverage. Test signal is helper infrastructure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/PacketProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubAuthenticator.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubAuthenticator.java

Purpose: authentication test double for SMB session setup. It provides a factory and authenticator implementation that can satisfy SMBJ authentication flows without real NTLM/Kerberos negotiation.

State and persistence: minimal in-memory factory/authenticator state; no credential persistence. Dependencies are SMBJ authenticator interfaces, authentication context, and session setup message types. Integration point is connection/session tests that need a successful login path. Risks include masking real authentication edge cases and hard-coding success behavior. Test signal is helper-level; it enables deterministic tests of connection/share logic independent of crypto auth.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubTransportLayerFactory.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubTransportLayerFactory.java

Purpose: in-memory transport factory used to run SMB client flows without sockets. `createTransportLayer` returns `StubTransportLayer`, whose `write` method processes a packet with a `PacketProcessor`, wraps it as `StubPacketData`, and feeds it back to the registered receiver. It also tracks `connected`, supports connect/disconnect/isConnected, and uses `StubMessageConverter` to return already-built packets.

State and persistence: in-memory connected flag, packet receiver, processor, and packet data; no persistence. Dependencies are protocol transport interfaces, SMB2 converter/data/header classes, and packet handlers. Integration point is most SMBJ unit/integration tests. Risks include synchronous behavior hiding real transport timing, converter bypasses, and limited error modeling. Test signal is infrastructure-critical.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/StubTransportLayerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/Utils.java -->
# sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/Utils.java

Purpose: small testing utility for creating `SmbConfig` instances backed by a `StubTransportLayerFactory`. API surface is `config(PacketProcessor)` and `configBuilder(PacketProcessor)`.

State and persistence: no state; returns new builders/configs. Dependencies are `SmbConfig`, `PacketProcessor`, and `StubTransportLayerFactory`. Integration point is Java tests that need a client config with deterministic packet responses. Risks are low; helper changes can affect many tests by altering default transport behavior. Test signal is indirect through callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/java/com/hierynomus/smbj/testing/Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/resources/logback-test.xml -->
# sources/user-network-fs/smbj/src/test/resources/logback-test.xml

Purpose: test logging configuration for the SMBJ module. It defines Logback appenders/loggers used while running tests, typically routing output to console with controlled levels.

State and persistence: runtime logging configuration only; no application state. Dependencies are Logback XML schema/classes and test runtime classpath discovery. Integration point is all tests in the module because `logback-test.xml` is auto-detected. Risks include overly verbose logs obscuring failures, suppressing useful diagnostics, or changing package log levels in ways that affect timing-sensitive tests. Test signal is configuration-level, not executable assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/test/resources/logback-test.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/IOExceptionHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/IOExceptionHelper.cs

Purpose: C# helper for extracting Windows error information from `IOException`. API surface is `GetWin32ErrorCode(IOException ex)` returning a `ushort` derived from the exception HResult, and `GetExceptionHResult(IOException ex)` exposing the raw HResult.

State and persistence: stateless static methods only. Dependencies are .NET `System.IO.IOException` and HResult conventions. Integration point is NT filesystem adapter error translation from .NET exceptions to SMB/Win32-style error codes. Risks include truncating or misinterpreting non-Win32 HResults, platform differences, and relying on exception internals. Test signal is absent in this file; callers need coverage for representative IO errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/IOExceptionHelper.cs -->
