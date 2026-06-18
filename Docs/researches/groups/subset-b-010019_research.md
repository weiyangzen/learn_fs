# Research group subset-b-010019

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/GSSProvider.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/GSSProvider.cs

## Purpose
`GSSProvider` is the server-side GSS/SPNEGO coordinator for SMB authentication. It advertises configured mechanisms, accepts SPNEGO `negTokenInit` / `negTokenResp` tokens, and also supports Windows-compatible raw NTLMSSP blobs in SMB security fields.

## Important APIs and Types
`GSSContext` stores the selected `IGSSMechanism` and its opaque mechanism context. `GSSProvider.GetSPNEGOTokenInitBytes()` emits a SPNEGO initial token containing every configured mechanism OID. `AcceptSecurityContext()` is the main state machine. `GetContextAttribute()`, `DeleteSecurityContext()`, `GetNTLMChallengeMessage()`, and `NTLMAuthenticate()` bridge downstream SMB server code to mechanism-specific auth state. `NTLMSSPIdentifier` is the NTLM OID.

## Control Flow
The acceptor first tries `SimpleProtectedNegotiationToken.ReadToken()`. For `negTokenInit`, it selects the preferred mechanism if available, otherwise the first supported mechanism from the offered list. Preferred mechanisms receive the embedded mechanism token immediately; fallback mechanisms return `SEC_I_CONTINUE_NEEDED` with a supported-mechanism response. `negTokenResp` messages require an existing context and forward `ResponseToken` to the selected mechanism. If SPNEGO parsing fails, a valid raw NTLMSSP signature is accepted and routed to the NTLM mechanism.

## State, Dependencies, and Integration
State is per-authentication context and delegated to the mechanism implementation. The provider depends on SPNEGO token classes, NTLM message utilities, `NTStatus`, and `ByteUtils`. SMB1/SMB2 session setup code can use this provider without knowing whether SPNEGO or raw NTLM carried the exchange.

## Risks and Test Signals
SPNEGO parser exceptions are swallowed before raw NTLM fallback, so malformed SPNEGO may be reported only as invalid token. Mechanism-list MIC is not validated here. Tests should cover preferred/fallback mechanism selection, raw NTLM negotiate/authenticate, null context response rejection, status-to-negState mapping, and legacy helper behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/GSSProvider.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/IGSSMechanism.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/IGSSMechanism.cs

## Purpose
`IGSSMechanism` defines the small mechanism contract consumed by `GSSProvider`. It abstracts NTLM or future Kerberos-like mechanisms behind GSS-style operations.

## Important APIs and Types
`AcceptSecurityContext(ref object context, byte[] inputToken, out byte[] outputToken)` mirrors `GSS_Accept_sec_context`. `DeleteSecurityContext(ref object context)` releases mechanism state. `GetContextAttribute(object context, GSSAttributeName attributeName)` exposes negotiated identity/session attributes. `Identifier` returns the mechanism OID used in SPNEGO negotiation.

## Control Flow
The interface itself has no implementation, but the expected flow is multi-step: a provider creates or passes an opaque context object, the mechanism consumes one incoming token per call, and the mechanism reports success, continuation, or failure through `NTStatus`.

## State, Dependencies, and Integration
State is deliberately opaque (`object`) so implementations can store NTLM challenge/session data without leaking concrete types. `NTLMAuthenticationProviderBase` is the primary implementation in this subset. `GSSProvider` uses `Identifier` for selection and forwards context lifecycle calls to the selected mechanism.

## Risks and Test Signals
The untyped context makes implementation errors runtime-only. Tests should verify each mechanism tolerates null initial context, rejects out-of-order tokens, returns stable identifiers, clears context on deletion, and exposes attributes consistently after successful authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/IGSSMechanism.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/DerEncodingHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/DerEncodingHelper.cs

## Purpose
`DerEncodingHelper` centralizes the subset of ASN.1 DER length/string handling needed by SPNEGO token readers and writers.

## Important APIs and Types
`DerEncodingTag` names the tags used by this implementation: octet string, object identifier, enum, general string, and sequence. `ReadLength()` and `WriteLength()` implement short and long-form DER lengths. `GetLengthFieldSize()` predicts encoded length size for buffer allocation. `EncodeGeneralString()` and `DecodeGeneralString()` map SPNEGO hint names to ASCII bytes.

## Control Flow
Readers consume from a caller-owned offset by reference, interpreting long-form length bytes as big-endian. Writers build long-form fields by repeatedly taking base-256 bytes, reversing, and prefixing with `0x80 | lengthField.Length`; short lengths are written as a single byte.

## State, Dependencies, and Integration
The class is stateless and relies on `ByteReader`/`ByteWriter`. SPNEGO init, init2, response, and generic token wrappers use it for exact buffer sizing before serialization.

## Risks and Test Signals
No bounds or canonical-DER checks are performed here; callers depend on lower-level readers to throw when offsets exceed buffers. Indefinite length is not supported, which is correct for DER but should be tested. Use round-trip tests for lengths around 127, 128, 255, 256, and multibyte values, plus malformed/truncated SPNEGO input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/DerEncodingHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationToken.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationToken.cs

## Purpose
`SimpleProtectedNegotiationToken` is the abstract base for SPNEGO tokens. It adds/removes the generic GSS-API application header and dispatches encoded token bodies to init, init2, or response classes.

## Important APIs and Types
`ApplicationTag` is `0x60`, and `SPNEGOIdentifier` is the SPNEGO OID. `GetBytes()` is implemented by concrete token classes. `GetBytes(bool includeHeader)` optionally prepends the RFC 2743 mechanism-independent token header. `ReadToken()` parses a token from bytes and returns `SimpleProtectedNegotiationTokenInit`, `SimpleProtectedNegotiationTokenInit2`, `SimpleProtectedNegotiationTokenResponse`, or null.

## Control Flow
When the first tag is the application tag, the parser reads total length, validates the object identifier tag and SPNEGO OID, then dispatches on the next context-specific token tag. A server-initiated init token is interpreted as `NegTokenInit2`; normal client init is interpreted as `NegTokenInit`. Bare `negTokenResp` without a GSS header is also accepted.

## State, Dependencies, and Integration
The class is stateless. It integrates `DerEncodingHelper`, `ByteReader`, `ByteWriter`, and `ByteUtils` with `GSSProvider` and `NTLMAuthenticationClient`.

## Risks and Test Signals
`ReadToken()` returns null for structural mismatches but can throw for truncated input. It does not verify that consumed bytes match declared total length. Tests should cover header/no-header response parsing, SPNEGO OID mismatch, server-initiated init2 dispatch, and malformed lengths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationToken.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit.cs

## Purpose
`SimpleProtectedNegotiationTokenInit` implements RFC 4178 `negTokenInit` serialization and parsing for the SPNEGO initiator token.

## Important APIs and Types
Fields include `MechanismTypeList`, `MechanismToken`, and `MechanismListMIC`. Constants define the `negTokenInit` tag and child tags for mechanism list, required flags, mechanism token, and MIC. Static helpers read/write mechanism lists and expose `GetMechanismTypeListBytes()` for MIC calculation.

## Control Flow
The constructor reads a wrapper construction length, requires a sequence tag, then loops through context-specific fields until the sequence end. Mechanism lists are sequences of OID elements, mechanism tokens and MICs are octet strings, and `ReqFlags` throws `NotImplementedException`. Serialization computes exact nested lengths, writes the outer tag/sequence, and emits only non-null optional fields.

## State, Dependencies, and Integration
Instances are mutable token DTOs. `GSSProvider` uses them to advertise mechanisms and process client SPNEGO init. `NTLMAuthenticationClient` uses them to wrap an NTLM negotiate message and to compute the mechanism-list bytes needed for MIC.

## Risks and Test Signals
`MechanismTypeList` is optional in the class but server logic assumes non-null/countable when accepting init tokens. Required flags are explicitly unsupported. Tests should cover empty lists, missing mechanism token, MIC round trips, long DER lengths, and parser behavior for unexpected tags or malformed nested sequences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit2.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit2.cs

## Purpose
`SimpleProtectedNegotiationTokenInit2` implements the Microsoft SPNEGO `NegTokenInit2` extension used for server-initiated negotiation hints.

## Important APIs and Types
It inherits `SimpleProtectedNegotiationTokenInit` and adds `HintName` and `HintAddress`. It reassigns `NegHintsTag` to `0xA3` and moves `MechanismListMICTag` to `0xA4`. Helper methods read/write hint sequences, `GeneralString` hint names, octet-string addresses, and the init2 MIC field.

## Control Flow
Parsing mirrors `negTokenInit` but recognizes the additional hints field and the shifted MIC tag. Serialization calls the base field-length logic, adds hint length when either hint is present, then writes mechanism fields, hints, and MIC in sequence. The default constructor sets the standard placeholder hint name `not_defined_in_RFC4178@please_ignore`.

## State, Dependencies, and Integration
The class is used when `SimpleProtectedNegotiationToken.ReadToken(..., serverInitiatedNegotiation: true)` encounters a `negTokenInit` tag. `NTLMAuthenticationClient` can consume server-offered mechanism lists and hints before emitting a client init token.

## Risks and Test Signals
The `new` MIC constant and writer hide the base member, so callers using base-type static members can pick the wrong tag. GeneralString is ASCII-only. Tests should cover init2 hint-only tokens, hint plus mechanism list, `A4` MIC round trips, and rejection of invalid hint sequence tags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenInit2.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenResponse.cs

## Purpose
`SimpleProtectedNegotiationTokenResponse` implements RFC 4178 `negTokenResp` for SPNEGO acceptor/initiator continuation and completion messages.

## Important APIs and Types
`NegState` models accept-completed, accept-incomplete, reject, and request-mic. Token fields are `NegState`, `SupportedMechanism`, `ResponseToken`, and `MechanismListMIC`; constants define their context-specific tags.

## Control Flow
The parser reads the construction and inner sequence, then loops over optional fields. `NegState` is a DER enum wrapped by tag `0xA0`; supported mechanism is an OID; response token and MIC are octet strings. `GetBytes()` computes nested field sizes and emits optional fields in protocol order.

## State, Dependencies, and Integration
Instances are mutable SPNEGO DTOs. `GSSProvider` creates response tokens from mechanism output and maps `NTStatus.STATUS_SUCCESS` to `AcceptCompleted`, `SEC_I_CONTINUE_NEEDED` to `AcceptIncomplete`, and other statuses to `Reject`. `NTLMAuthenticationClient` reads server response tokens and emits final NTLM authenticate tokens with a mech-list MIC.

## Risks and Test Signals
Parsing is strict about tags but not about declared/consumed length equality. The code supports RequestMic structurally but provider logic does not enforce MIC negotiation policy. Tests should verify status mapping, bare response parsing, MIC preservation, and malformed optional fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/SPNEGO/SimpleProtectedNegotiationTokenResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/LoginCounter.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/LoginCounter.cs

## Purpose
`LoginCounter` provides in-memory rate limiting for repeated failed authentication attempts per user.

## Important APIs and Types
`LoginEntry` stores a window start timestamp and attempt count. The constructor accepts `maxLoginAttemptsInWindow` and `loginWindowDuration`. `HasRemainingLoginAttempts(userID)` checks without incrementing; `HasRemainingLoginAttempts(userID, incrementCount)` optionally records an attempt.

## Control Flow
The method locks the dictionary, looks up or creates an entry, resets expired windows, increments only when requested, and returns whether the current attempt count is below the configured maximum.

## State, Dependencies, and Integration
State is process-local and not persisted. `IndependentNTLMAuthenticationProvider` uses lowercased usernames to lock out invalid usernames or failed passwords after many attempts. The lock on `m_loginEntries` makes dictionary mutation thread-safe for concurrent SMB logins.

## Risks and Test Signals
The threshold check uses `< max`, so the attempt that reaches the limit returns false. Entries are never pruned, which can grow with many usernames. Restarting the process clears lockouts. Tests should cover check-without-increment, boundary attempt counts, window expiration, case normalization by callers, and concurrent increments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/LoginCounter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AVPairUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AVPairUtils.cs

## Purpose
`AVPairUtils` reads and writes NTLM AV_PAIR target-info sequences used in challenge messages and NTLMv2 client challenges.

## Important APIs and Types
`GetAVPairSequence()` builds NetBIOS domain/computer name pairs. `GetAVPairSequenceBytes()`, `GetAVPairSequenceLength()`, and `WriteAVPairSequence()` serialize pairs plus the EOL terminator. `ReadAVPairSequence()` parses until `AVPairKey.EOL`.

## Control Flow
Serialization writes key and length as little-endian 16-bit values followed by the raw value. Deserialization peeks at the next key and repeatedly consumes pairs until EOL; EOL itself is not returned in the list.

## State, Dependencies, and Integration
The helper is stateless and depends on `KeyValuePairList`, endian readers/writers, and byte readers. `ChallengeMessage`, `NTLMv2ClientChallenge`, `IndependentNTLMAuthenticationProvider`, and SMB1 legacy NTLMv2 login all depend on its target-info encoding.

## Risks and Test Signals
Malformed sequences without EOL or with lengths beyond the buffer will throw from readers. There is no duplicate-key policy. Tests should include round trips for Unicode names, empty pair lists, unknown AV keys, missing EOL, and interoperability with Microsoft NTLM target-info vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AVPairUtils.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AuthenticationMessageUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AuthenticationMessageUtils.cs

## Purpose
`AuthenticationMessageUtils` provides common NTLM message parsing helpers for security-buffer descriptors, signature checks, response-type detection, and message type extraction.

## Important APIs and Types
`ReadAnsiStringBufferPointer()`, `ReadUnicodeStringBufferPointer()`, and `ReadBufferPointer()` decode NTLM security buffers. `WriteBufferPointer()` writes length/max-length/offset descriptors. `IsSignatureValid()` checks `NTLMSSP\0`. `IsNTLMv1ExtendedSessionSecurity()`, `IsNTLMv2NTResponse()`, and `GetMessageType()` classify messages.

## Control Flow
Security-buffer readers read length, max length, and payload offset, returning empty arrays for zero length. Extended-session-security detection expects a 24-byte LM response with nonzero first 8 bytes and 16 zero padding bytes. NTLMv2 detection checks length and the two structure-version bytes at response offset 16.

## State, Dependencies, and Integration
The helper is stateless and used by every NTLM structure plus `GSSProvider` and `NTLMAuthenticationProviderBase`.

## Risks and Test Signals
Buffer descriptor offsets are trusted; invalid offsets become lower-level read exceptions. `ReadAnsiStringBufferPointer()` uses `ASCIIEncoding.Default`, which can be platform-sensitive. Tests should cover malformed lengths, zero-length buffers, all three NTLM message types, and v1/v2 response classification edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AuthenticationMessageUtils.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/MD4.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/MD4.cs

## Purpose
`MD4` is a bundled MD4 digest implementation used to compute NT hashes for NTLM. It lives under `System.Security.Cryptography` for local convenience.

## Important APIs and Types
Public helpers compute byte or hex hashes from strings, bytes, or a single byte. Internally `EngineUpdate()`, `EngineDigest()`, and `Transform()` implement RFC 1320 padding, block buffering, and the three MD4 rounds.

## Control Flow
Input bytes are buffered into 64-byte blocks. Finalization appends `0x80`, zero padding to 56 mod 64, and the little-endian bit length. `Transform()` decodes 16 little-endian 32-bit words, applies FF/GG/HH rounds, and accumulates context state. Each public hash method uses a fresh `MD4` instance and resets after digest.

## State, Dependencies, and Integration
State is instance-local: four context words, a 64-byte buffer, a 16-word work array, and byte count. `NTLMCryptography.NTOWFv1()` and session-base-key derivation depend on this exact MD4 behavior.

## Risks and Test Signals
MD4 is cryptographically obsolete but required by NTLM. The string helper uses UTF-8, while NTLM callers correctly pass UTF-16LE bytes themselves. Tests should use RFC 1320 MD4 vectors and NTLM NTOWF vectors, including empty string and long multi-block inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/MD4.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/NTLMCryptography.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/NTLMCryptography.cs

## Purpose
`NTLMCryptography` implements the LM/NTLM response, key derivation, signing, sealing, MIC, DES, RC4, MD4, MD5, and HMAC-MD5 primitives required by NTLM authentication.

## Important APIs and Types
Key APIs include `ComputeLMv1Response()`, `ComputeNTLMv1Response()`, `ComputeNTLMv1ExtendedSessionSecurityResponse()`, `ComputeLMv2Response()`, `ComputeNTLMv2Proof()`, `LMOWFv1()`, `NTOWFv1()`, `NTOWFv2()`, `KXKey()`, `ValidateAuthenticateMessageMIC()`, sign/seal key derivation, `ComputeMechListMIC()`, and `ComputeMessageSignature()`.

## Control Flow
v1 responses DESL-encrypt an 8-byte challenge with LM/NT hashes. Extended session security hashes server/client challenges with MD5 before DESL. v2 derives an HMAC-MD5 response key over uppercased user plus domain, then computes LMv2 or NT proof over server challenge and the client challenge structure. KXKEY follows flag-dependent MS-NLMP branches. Signing derives magic-constant keys, HMACs sequence number plus message, RC4-encrypts the first eight hash bytes, and prepends signature version.

## State, Dependencies, and Integration
The class is stateless except for caller-supplied `RC4KeyState` mutation during signing. Client and server NTLM providers both depend on it for authentication and session keys.

## Risks and Test Signals
Randomness is supplied by callers, often `Random`, not CSPRNG. DES weak-key support uses reflection into runtime internals. `ValidateAuthenticateMessageMIC()` mutates the supplied authenticate buffer by zeroing the MIC. Tests need MS-NLMP vectors for v1/v2/KXKEY/MIC/signature, weak DES keys, and MIC mutation awareness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/NTLMCryptography.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/RC4.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/RC4.cs

## Purpose
`RC4` implements the RC4 stream cipher and exposes reusable key state for NTLM sealing/signing operations.

## Important APIs and Types
`Encrypt(byte[] key, byte[] data)` and `Decrypt(byte[] key, byte[] data)` initialize fresh state. `InitializeStateFromKey()` performs RC4 KSA and returns `RC4KeyState`. `Encrypt(RC4KeyState state, byte[] data)` mutates ongoing PRGA state. `RC4KeyState` stores the S-box and i/j indices.

## Control Flow
Initialization fills S with 0..255, permutes it with the key, and returns state. Encryption increments i, updates j, swaps S entries, derives the stream byte from the permuted state, and XORs input bytes. Decrypt is identical to encrypt.

## State, Dependencies, and Integration
Stateful mode is used by `NTLMCryptography.ComputeMessageSignature()` so consecutive signatures can share the sealing stream. Key-exchange decryption/encryption uses fresh state.

## Risks and Test Signals
RC4 is obsolete but required by NTLM. Empty keys would divide by zero. Stateful encryption is not thread-safe. Tests should include known RC4 vectors, fresh encrypt/decrypt symmetry, stateful multi-call equivalence to one-shot encryption, and key-exchange session-key decryption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/RC4.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/IndependentNTLMAuthenticationProvider.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/IndependentNTLMAuthenticationProvider.cs

## Purpose
`IndependentNTLMAuthenticationProvider` is a standalone server-side NTLM `IGSSMechanism` that validates challenge responses against a password lookup delegate.

## Important APIs and Types
`GetUserPassword` supplies passwords or null for missing accounts. `AuthContext` stores server challenge, negotiated identity, workstation, OS version, session key, and guest flag. `GetChallengeMessage()`, `CreateChallengeMessage()`, `Authenticate()`, `DeleteSecurityContext()`, and `GetContextAttribute()` implement mechanism behavior.

## Control Flow
On negotiate, it parses `NegotiateMessage`, generates an 8-byte server challenge, creates `AuthContext`, and returns a challenge with flags derived from the client request. On authenticate, it parses `AuthenticateMessage`, records identity fields, handles anonymous/guest login, checks `LoginCounter`, fetches the password, and validates v1, v1 extended-session-security, or v2 responses. Successful authentication derives the session key, decrypting `EncryptedRandomSessionKey` when key exchange is negotiated.

## State, Dependencies, and Integration
Per-context state lives in `AuthContext`; cross-context failed-attempt state lives in `LoginCounter`. It integrates with `GSSProvider` via `NTLMAuthenticationProviderBase`, and exposes GSS attributes for SMB sessions.

## Risks and Test Signals
`GenerateServerChallenge()` uses `Random`, not a cryptographic RNG. Guest login is enabled by a `Guest` password equal to empty string. MIC validation is not performed. Tests should cover invalid message parsing, lockout boundaries, guest/anonymous policy, v1/v2 success/failure, key exchange, and GSS attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/IndependentNTLMAuthenticationProvider.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/NTLMAuthenticationProviderBase.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/NTLMAuthenticationProviderBase.cs

## Purpose
`NTLMAuthenticationProviderBase` adapts raw NTLMSSP messages to the generic `IGSSMechanism` contract.

## Important APIs and Types
It exposes the NTLMSSP OID through `Identifier`. `AcceptSecurityContext()` validates the NTLM signature, reads the message type, and dispatches to abstract `GetChallengeMessage()` or `Authenticate()`. Subclasses must also implement context deletion and context attribute retrieval.

## Control Flow
Type 1 negotiate messages create/replace context and emit a challenge. Type 3 authenticate messages consume the existing context and return the authentication status without an output token. Any invalid signature, unsupported message type, or challenge message sent in the wrong direction returns `SEC_E_INVALID_TOKEN`.

## State, Dependencies, and Integration
The base class itself is stateless. `IndependentNTLMAuthenticationProvider` supplies the actual context and validation logic. `GSSProvider` registers implementations through the `IGSSMechanism` interface.

## Risks and Test Signals
There is no explicit check that authenticate has a non-null context; subclasses must enforce it. Tests should verify type dispatch, invalid signature rejection, challenge-message rejection, identifier equality with `GSSProvider.NTLMSSPIdentifier`, and that output tokens are null on final authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/NTLMAuthenticationProviderBase.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/AuthenticateMessage.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/AuthenticateMessage.cs

## Purpose
`AuthenticateMessage` models the NTLM Type 3 AUTHENTICATE_MESSAGE and serializes/deserializes credentials, flags, optional version, and optional MIC.

## Important APIs and Types
Fields include LM/NT challenge responses, domain, user, workstation, encrypted random session key, negotiate flags, `NTLMVersion`, and `MIC`. `HasMicField()` detects MIC based on NTLMv2 AV flags. `GetBytes()` serializes the message. `CalculateMIC()` computes the HMAC-MD5 over negotiate, challenge, and authenticate bytes. `GetMicFieldOffset()` locates the MIC field.

## Control Flow
Parsing reads fixed security-buffer descriptors, decodes Unicode string fields, reads negotiate flags, optional version, and MIC if the NTLMv2 client challenge contains AV flags with bit `0x02`. Serialization lays out the fixed header, optional version/MIC, then payload strings/responses/session key, updating security-buffer pointers.

## State, Dependencies, and Integration
Client helpers build this object; server providers parse it. MIC and session key interactions depend on `NTLMCryptography`, `NTLMv2ClientChallenge`, and AV pairs.

## Risks and Test Signals
Serialization uses UTF-16 byte lengths via `string.Length * 2`; non-BMP characters need careful testing. MIC detection depends on AV pair parsing and `AVPairKey.Flags`. Tests should cover anonymous, v1, v2 with/without MIC, key-exchange field omission, and MIC offset when version is present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/AuthenticateMessage.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/ChallengeMessage.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/ChallengeMessage.cs

## Purpose
`ChallengeMessage` models the NTLM Type 2 CHALLENGE_MESSAGE used by servers to send negotiate flags, target name, server challenge, target info, and optional version.

## Important APIs and Types
Fields include `TargetName`, `NegotiateFlags`, `ServerChallenge`, `TargetInfo`, and `Version`. The constructor parses a byte buffer; `GetBytes()` serializes fixed fields plus variable target-name and target-info payloads.

## Control Flow
Parsing reads the NTLM signature/type, target-name security buffer, flags, 8-byte server challenge, target-info buffer, and optional version at offset 48 when the flag is set. Serialization chooses fixed length 48 or 56, writes signature/type/flags/challenge/version, serializes AV pairs, then writes target name and target info through buffer pointers.

## State, Dependencies, and Integration
Server-side providers create challenges; client-side `NTLMAuthenticationHelper` parses them. `AVPairUtils` supplies target-info sequence handling.

## Risks and Test Signals
The parser assumes Unicode target names and trusts buffer pointers. It does not validate reserved bytes or signature/type itself beyond field assignment. Tests should round-trip server-created challenges, parse Windows challenge vectors, handle missing target info, and reject/trap truncated buffers in callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/ChallengeMessage.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/AVPairKey.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/AVPairKey.cs

## Purpose
`AVPairKey` enumerates NTLM target-info AV pair keys used in challenge and client-challenge structures.

## Important APIs and Types
Values cover EOL, NetBIOS computer/domain names, DNS names, tree name, flags, timestamp, single-host data, target name, and channel bindings.

## Control Flow
The enum has no behavior. It drives `AVPairUtils`, `NTLMv2ClientChallenge`, MIC detection in `AuthenticateMessage`, and target-info creation in providers/helpers.

## State, Dependencies, and Integration
It is a protocol constant set shared throughout NTLM serialization/deserialization.

## Risks and Test Signals
`Flags` and `Timestamp` are both assigned `0x0006`; in MS-NLMP timestamp is normally a distinct key. This can cause timestamp AV pairs to be interpreted as flags and affects MIC detection. Tests should cover every assigned value against protocol constants, especially flags/timestamp behavior and unknown-key preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/AVPairKey.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/MessageTypeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/MessageTypeName.cs

## Purpose
`MessageTypeName` enumerates NTLMSSP message type numbers.

## Important APIs and Types
`Negotiate = 0x01`, `Challenge = 0x02`, and `Authenticate = 0x03` match Type 1, Type 2, and Type 3 NTLM messages.

## Control Flow
The enum has no behavior; parsers cast the little-endian 32-bit type field to this enum and dispatch accordingly.

## State, Dependencies, and Integration
`AuthenticationMessageUtils.GetMessageType()`, `NTLMAuthenticationProviderBase`, and the three message structures depend on these constants.

## Risks and Test Signals
Unknown values are representable by casts and must be rejected by dispatching code. Tests should verify wire values, invalid-type rejection in provider base, and structure constructors setting the expected message type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/MessageTypeName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/NegotiateFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/NegotiateFlags.cs

## Purpose
`NegotiateFlags` defines NTLM negotiate capability and feature flags used across Type 1, Type 2, and Type 3 messages.

## Important APIs and Types
The `[Flags]` enum covers encoding, target-name request, signing/sealing, LAN Manager session key, NTLM session security, anonymous, supplied names, target type, extended session security, identify, non-NT session key, target info, version, 128-bit/56-bit encryption, and key exchange.

## Control Flow
The enum itself has no control flow. Providers and helpers combine bitmasks to choose authentication variants, key derivation, target-info presence, message version fields, and signing/sealing options.

## State, Dependencies, and Integration
Every NTLM message type and crypto branch depends on these constants. SMB1 session setup maps negotiated server capabilities and selected authentication method into these flags.

## Risks and Test Signals
Incorrect bit values silently break interoperability. Tests should assert all constants against MS-NLMP, verify mutually exclusive `LanManagerSessionKey`/`ExtendedSessionSecurity` handling, and cover flag propagation from negotiate to challenge to authenticate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/NegotiateFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMVersion.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMVersion.cs

## Purpose
`NTLMVersion` represents the optional 8-byte NTLM VERSION structure.

## Important APIs and Types
Fields are product major/minor version, build, and current revision. `Length` is 8 and `NTLMSSP_REVISION_W2K3` is `0x0F`. Static factories expose `WindowsXP` and `Server2003`. `WriteBytes()` serializes the structure and `ToString()` returns major.minor.build.

## Control Flow
The byte constructor reads major/minor/build from the first four bytes and revision from byte 7, skipping the reserved three bytes. The writer mirrors that layout.

## State, Dependencies, and Integration
Message structures include this object when `NegotiateFlags.Version` is set. Client and server helpers currently advertise `Server2003`.

## Risks and Test Signals
Reserved bytes are left zero by default when writing but are not validated when reading. Tests should round-trip both static versions, parse known version bytes, verify optional inclusion in negotiate/challenge/authenticate messages, and assert `Length`-based offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMVersion.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMv2ClientChallenge.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMv2ClientChallenge.cs

## Purpose
`NTLMv2ClientChallenge` models the NTLMv2 client challenge blob appended to an NT proof string.

## Important APIs and Types
Fields include current/max version, timestamp, 8-byte client challenge, reserved fields, and AV pairs. Constructors build from domain/computer names, from target-info plus optional SPN, or parse bytes. `GetBytes()` serializes the structure and `GetBytesPadded()` appends the four zero bytes required for NTLMv2 proof calculation.

## Control Flow
Parsing reads fixed fields at offsets 0..27 and then delegates AV pair parsing at offset 28. Serialization writes fixed fields, FILETIME timestamp, client challenge, reserved fields, and the AV pair sequence.

## State, Dependencies, and Integration
Client authentication uses it to form NTLMv2 responses; server authentication parses it to validate proofs and detect MIC flags. Dependencies include `AVPairUtils`, `FileTimeHelper`, and endian/byte helpers.

## Risks and Test Signals
Constructors reuse the target-info list by reference and append SPN directly, mutating caller-owned collections. The timestamp epoch constant is not otherwise used. Tests should cover proof-vector serialization, padded bytes, SPN insertion side effects, malformed AV pairs, and MIC flag parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMv2ClientChallenge.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NegotiateMessage.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NegotiateMessage.cs

## Purpose
`NegotiateMessage` models NTLM Type 1 NEGOTIATE_MESSAGE.

## Important APIs and Types
Fields are signature, message type, negotiate flags, optional domain name, optional workstation, and optional version. `GetBytes()` serializes the message; the byte constructor parses it.

## Control Flow
Parsing reads signature/type/flags, then ANSI buffer pointers for domain and workstation, and optional version at offset 32. Serialization clears domain/workstation unless their supplied flags are set, computes fixed length 32 or 40, writes fixed fields, then writes domain and workstation payloads.

## State, Dependencies, and Integration
Client helpers generate negotiate messages; server providers parse them. It depends on NTLM buffer-pointer helpers and `NTLMVersion`.

## Risks and Test Signals
Serialization writes UTF-16 payloads while parsing uses ANSI readers for domain/workstation, which is unusual for OEM-supplied fields and should be tested for interoperability. Tests should cover supplied/unsupplied names, version flag offsets, and parsing of Windows Type 1 vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NegotiateMessage.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/IAuthenticationClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/IAuthenticationClient.cs

## Purpose
`IAuthenticationClient` abstracts client-side security context negotiation for SMB session setup.

## Important APIs and Types
`InitializeSecurityContext(byte[] securityBlob)` consumes a server security blob and returns the next credentials blob, or null for invalid input. `GetSessionKey()` returns the negotiated session key. `ResetSecurityContext(string spn)` prepares the same credentials for another server/SPN, primarily DFS.

## Control Flow
Implementations are expected to be stateful: first call emits an initial token, later calls consume challenges and emit authenticators.

## State, Dependencies, and Integration
`NTLMAuthenticationClient` implements this contract for SMB1 extended security and likely SMB2 clients elsewhere. DFS logic can reset SPN-specific context without recreating credentials.

## Risks and Test Signals
The interface does not expose completion state or error details beyond null. Tests for implementers should cover first-call/second-call sequencing, null or malformed blobs, session-key availability only after success, and SPN reset behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/IAuthenticationClient.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/NTLMAuthenticationClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/NTLMAuthenticationClient.cs

## Purpose
`NTLMAuthenticationClient` implements client-side NTLM over raw SMB security blobs or SPNEGO/GSS wrapping.

## Important APIs and Types
Constructor captures domain, username, password, SPN, and `AuthenticationMethod`. `InitializeSecurityContext()` alternates between negotiate and authenticate phases. `GetSessionKey()` returns the NTLM session key. `ResetSecurityContext()` clears negotiation state for a new SPN.

## Control Flow
On first call, if the server supplied a security blob, it parses SPNEGO init/init2 and requires the NTLM OID. It creates an NTLM negotiate message and optionally wraps it in `negTokenInit`. On the second call, it parses a SPNEGO response when present, extracts the challenge, builds an authenticate message through `NTLMAuthenticationHelper`, stores the session key, and if wrapped, emits a `negTokenResp` containing the authenticate token and mech-list MIC.

## State, Dependencies, and Integration
State includes the previous negotiate bytes, session key, SPN, and a phase boolean. SMB1 extended session setup uses this class; DFS can reset it for referrals.

## Risks and Test Signals
It assumes a two-message NTLM exchange and returns null for unsupported SPNEGO mechanisms. MIC is computed over a one-entry NTLM mechanism list. Tests should cover raw mode, SPNEGO mode, unsupported mechanism rejection, reset, malformed challenge blobs, and session-key propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/NTLMAuthenticationClient.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ConnectionState.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/ConnectionState.cs

## Purpose
`ConnectionState` groups a connected socket with its NetBIOS-over-TCP receive buffer for asynchronous SMB1 client I/O.

## Important APIs and Types
The constructor stores a `Socket` and creates an `NBTConnectionReceiveBuffer`. Read-only `ClientSocket` and `ReceiveBuffer` properties expose them to callback code.

## Control Flow
There is no behavior beyond construction and property access. `SMB1Client.ConnectSocket()` creates this state and passes it to `BeginReceive`; callbacks lock and mutate the receive buffer.

## State, Dependencies, and Integration
State is per TCP connection. It depends on `System.Net.Sockets` and `SMBLibrary.NetBios`. Disposal is managed by `SMB1Client`, not by this container.

## Risks and Test Signals
The class does not own cleanup semantics, so callback paths must dispose the receive buffer consistently. Tests are mostly integration-level: socket disconnect, receive buffer disposal on errors, and no reuse of disposed state after reconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ConnectionState.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsPath.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsPath.cs

## Purpose
`DfsPath` is a small UNC path model for DFS referral rewriting and share classification.

## Important APIs and Types
The constructor parses UNC-like strings into slash/backslash-delimited components. `ToUncPath()` and `ToString()` emit a canonical `\\server\share...` form. `ReplacePrefix()` rewrites case-insensitive path prefixes. Properties expose `ServerName`, `ShareName`, `HasOnlyOneComponent`, `IsSysVolOrNetLogon`, and `IsIpc`.

## Control Flow
Construction rejects null, empty, or componentless paths. Replacement verifies the old prefix length and component equality, then concatenates the new prefix and remaining suffix; non-matches return the original object.

## State, Dependencies, and Integration
State is an internal component list. DFS referral resolution can use it to convert namespace paths to referral target paths and classify special shares.

## Risks and Test Signals
`ServerName` assumes at least one component, guaranteed only through constructors. Returning `this` on non-match means callers should not assume a new object. Tests should cover slash variants, case-insensitive prefix replacement, one-component paths, IPC$/SYSVOL/NETLOGON detection, and invalid input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsPath.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsReferralHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsReferralHelper.cs

## Purpose
`DfsReferralHelper` sends DFS referral requests through an `ISMBFileStore`.

## Important APIs and Types
`DfsReferralFileId` is the SMB2 sentinel file ID with both halves set to all ones. `MaxOutputBufferSize` is 8192. `GetDfsReferral()` builds a `RequestGetDfsReferral`, calls `DeviceIOControl()` with `FSCTL_DFS_GET_REFERRALS`, and parses `ResponseGetDfsReferral`.

## Control Flow
The helper sets referral level 4, serializes the requested DFS path, submits the IOCTL, and only constructs a response object when status is success and output bytes are non-null.

## State, Dependencies, and Integration
The helper is stateless. It bridges client file-store abstractions to DFS protocol structures and SMB2 IOCTL constants, but can be called through SMB1/SMB2 file stores if they implement `DeviceIOControl`.

## Risks and Test Signals
For SMB1, file handles are normally ushort FIDs, while this helper uses an SMB2 `FileID` sentinel; compatibility depends on the store implementation. Tests should cover successful referral parsing, non-success status passthrough, null output, buffer-size limits, and SMB1 versus SMB2 store behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/DFS/DfsReferralHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Enums/AuthenticationMethod.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Enums/AuthenticationMethod.cs

## Purpose
`AuthenticationMethod` enumerates the NTLM variants supported by the client helpers.

## Important APIs and Types
Values are `NTLMv1`, `NTLMv1ExtendedSessionSecurity`, and `NTLMv2`.

## Control Flow
The enum has no behavior. Client code switches on it to set negotiate flags and compute the correct response and session keys.

## State, Dependencies, and Integration
`SMB1Client`, `NTLMAuthenticationClient`, and `NTLMAuthenticationHelper` accept this enum. The default login path uses NTLMv2.

## Risks and Test Signals
The enum does not include Kerberos or external SSPI modes. Tests should verify each value selects the expected flags/responses and that unsupported combinations, such as NTLMv1 extended session security without SMB extended security, throw or fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Enums/AuthenticationMethod.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/IPAddressHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/IPAddressHelper.cs

## Purpose
`IPAddressHelper` selects a preferred address from DNS results.

## Important APIs and Types
`SelectAddressPreferIPv4(IPAddress[] hostAddresses)` returns the first IPv4 address, or the first address if no IPv4 entry exists.

## Control Flow
The method scans the array for `AddressFamily.InterNetwork`; fallback is index zero.

## State, Dependencies, and Integration
The helper is stateless. `SMB1Client.Connect(string serverName, ...)` uses it after `Dns.GetHostAddresses()` so IPv4 is preferred for SMB transport.

## Risks and Test Signals
Empty arrays would throw, but `SMB1Client` checks for zero length before calling. Tests should cover IPv4-first, IPv6-only fallback, mixed IPv6/IPv4 ordering, and caller behavior for empty DNS results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/IPAddressHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NTLMAuthenticationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NTLMAuthenticationHelper.cs

## Purpose
`NTLMAuthenticationHelper` builds client-side NTLM negotiate and authenticate messages, including session-key derivation and MIC calculation.

## Important APIs and Types
`GetNegotiateMessage()` has overloads for credential-based anonymous detection and explicit flags. `GetAuthenticateMessage()` parses the challenge, creates LM/NT responses for v1, v1 extended session security, or v2, derives the session key, encrypts it when key exchange is negotiated, calculates MIC, and returns an AUTHENTICATE_MESSAGE.

## Control Flow
Negotiate flags always request Unicode/OEM, signing, NTLM session security, target name, always-sign, version, and 128/56-bit encryption; non-anonymous requests key exchange. Authenticate parsing validates a Type 2 challenge, generates an 8-byte client challenge, mirrors server encoding/seal/key-exchange flags, branches on authentication method, constructs responses and key material, optionally encrypts a random session key, then computes MIC over negotiate/challenge/authenticate.

## State, Dependencies, and Integration
The helper is stateless but uses time, machine name, and random client challenges. `NTLMAuthenticationClient` and `SMB1Client` depend on it for extended-security NTLM.

## Risks and Test Signals
Random challenges/session keys use `Random`, not a CSPRNG. NTLMv2 LM response uses `challengeMessage.TargetName` as domain in one branch. Tests need MS-NLMP vectors for all methods, anonymous handling, key exchange, MIC validation, malformed challenge rejection, and SPN target-info insertion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NTLMAuthenticationHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NamedPipeHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NamedPipeHelper.cs

## Purpose
`NamedPipeHelper` opens an SMB named pipe and performs the initial DCERPC bind.

## Important APIs and Types
`BindPipe(INTFileStore namedPipeShare, string pipeName, Guid interfaceGuid, uint interfaceVersion, out object pipeHandle, out int maxTransmitFragmentSize)` opens the pipe, constructs a `BindPDU`, sends it via `FSCTL_PIPE_TRANSCEIVE`, parses a `BindAckPDU`, and returns the negotiated transmit fragment size.

## Control Flow
It creates the pipe with read/write data access and share read/write. It sets RPC data representation to ASCII, little-endian, IEEE floating point, configures 5680 byte fragment sizes, adds one presentation context with the target interface and NDR transfer syntax, transceives the bind PDU, and validates the bind ACK.

## State, Dependencies, and Integration
The caller owns the returned pipe handle and must close it. `ServerServiceHelper` uses this helper before issuing `NetrShareEnum`.

## Risks and Test Signals
Failures after `CreateFile` do not close the pipe handle. Only one transfer syntax/context is attempted. Tests should cover create failure, non-ACK response, max-fragment propagation, handle cleanup expectations, and interoperability with srvsvc named pipe.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NamedPipeHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/ServerServiceHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/ServerServiceHelper.cs

## Purpose
`ServerServiceHelper` queries the Windows Server Service RPC endpoint over an SMB named pipe to list shares.

## Important APIs and Types
`ListShares(INTFileStore namedPipeShare, ShareType? shareType, out NTStatus status)` calls the overload with server `*`. The overload binds to `srvsvc`, sends `NetrShareEnum` level 1, handles fragmented RPC responses, maps access-denied or unsupported results to NTSTATUS, and filters share names by optional type.

## Control Flow
After `NamedPipeHelper.BindPipe`, it builds a request PDU with little-endian RPC representation and `NetrShareEnum` opnum. It transceives the first fragment, then keeps reading from the pipe until `LastFragment` is set, concatenates response data, parses `NetrShareEnumResponse`, and extracts `ShareInfo1Entry.NetName` values.

## State, Dependencies, and Integration
The helper is stateless but opens/closes a pipe handle through the supplied file store. `SMB1Client.ListShares()` uses it after tree-connecting to `IPC$`.

## Risks and Test Signals
The pipe handle is closed only after all fragments are collected, not on early failures. Large responses depend on `maxTransmitFragmentSize`. Tests should cover share-type filtering, fragmented responses, access denied mapping, invalid PDU handling, and close-on-success behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/ServerServiceHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBClient.cs

## Purpose
`ISMBClient` defines the high-level SMB client contract for connecting, authenticating, listing shares, tree connecting, echoing, and exposing negotiated transfer sizes.

## Important APIs and Types
Methods include address/name `Connect`, `Disconnect`, two `Login` overloads, `Logoff`, `ListShares`, `TreeConnect`, and `Echo`. Properties expose `MaxReadSize`, `MaxWriteSize`, and `IsConnected`.

## Control Flow
The interface prescribes a lifecycle: connect transport, login, optionally list shares or tree connect, use file stores, logoff, disconnect.

## State, Dependencies, and Integration
Implementations such as `SMB1Client` hold transport/session state and return `ISMBFileStore` instances for share operations. Higher-level code can target this interface without caring about SMB dialect-specific classes.

## Risks and Test Signals
The interface does not expose dialect, signing, encryption, DFS, or cancellation semantics. Tests for implementations should verify lifecycle preconditions, status returns, max-size values after negotiation, and consistent disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBClient.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBFileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBFileStore.cs

## Purpose
`ISMBFileStore` extends `INTFileStore` with SMB tree-specific lifecycle and negotiated transfer-size properties.

## Important APIs and Types
`Disconnect()` disconnects the tree/share. `MaxReadSize` and `MaxWriteSize` expose recommended chunk sizes for read/write calls inherited from `INTFileStore`.

## Control Flow
The interface has no implementation. Consumers obtain an instance from `ISMBClient.TreeConnect()` and use inherited file APIs until disconnect.

## State, Dependencies, and Integration
`SMB1FileStore` implements this interface by delegating sizes and message send/wait behavior to its owning `SMB1Client`.

## Risks and Test Signals
`Disconnect()` is separate from closing file handles, so callers must manage handles before tree disconnect. Tests should verify max-size propagation, disconnected-tree behavior, and mapping of store operations to transport failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/ISMBFileStore.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/NameServiceClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/NameServiceClient.cs

## Purpose
`NameServiceClient` performs a NetBIOS node-status query to discover a server's NetBIOS file-server name.

## Important APIs and Types
`NetBiosNameServicePort` is 137. The constructor stores the server IP address. `GetServerName()` sends a node-status request and returns the first name with `FileServerService` suffix. `SendNodeStatusRequest()` handles UDP send/receive and response parsing.

## Control Flow
The client builds a `NodeStatusRequest` for wildcard `*`, connects a UDP socket to the target endpoint, sends request bytes, blocks for a response, parses `NodeStatusResponse`, then scans returned names for the file server suffix.

## State, Dependencies, and Integration
State is the target IP address. `SMB1Client` uses this as fallback when a generic `*SMBSERVER` NetBIOS session request is rejected.

## Risks and Test Signals
There is no timeout configuration, disposal wrapper, or exception handling in this class; UDP receive can block according to socket defaults. Tests should cover response parsing with multiple names, no file-server suffix, unreachable host behavior, and integration with SMB1 NetBIOS fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/NameServiceClient.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1Client.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1Client.cs

## Purpose
`SMB1Client` implements the `ISMBClient` lifecycle for SMB1/CIFS over direct TCP or NetBIOS-over-TCP.

## Important APIs and Types
Public APIs cover connection, login with selected NTLM method, logoff, share listing, tree connect, echo, and negotiated max read/write sizes. Internal helpers include dialect negotiation, NetBIOS name fallback, asynchronous socket receive processing, message wait queues, and SMB1 packet sending.

## Control Flow
`Connect()` resolves addresses, opens a socket, optionally performs NetBIOS session setup, then negotiates the `NT LM 0.12` dialect. Non-extended security stores a raw server challenge; extended security stores the server security blob. `Login()` builds client capabilities and either sends legacy `SessionSetupAndXRequest` with LM/NT responses or runs a SPNEGO/NTLM loop using `NTLMAuthenticationClient` until success or error. Received packets are asynchronously decoded into SMB1 messages and enqueued; synchronous operations wait for matching command responses with a timeout.

## State, Dependencies, and Integration
The client owns socket state, negotiated capabilities, user ID, session key, incoming queues, and NetBIOS session response state. It creates `SMB1FileStore` for tree operations and uses `ServerServiceHelper` over `IPC$` for share enumeration.

## Risks and Test Signals
Request matching only checks command name, not MID/PID, while max multiplex count is forced to 1. Random client challenges use `Random`. Logoff sets `m_isLoggedIn` to status-not-success, likely inverted. Tests should cover both transports, dialect capability parsing, legacy and extended-security login, timeout/disconnect behavior, queue matching, tree connect, and logoff state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1Client.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1FileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1FileStore.cs

## Purpose
`SMB1FileStore` implements `ISMBFileStore` operations for a connected SMB1 tree.

## Important APIs and Types
Implemented operations include create, close, read, write, directory query via `TRANS2_FIND_FIRST2/NEXT2`, file information query/set, filesystem information query, security descriptor query, IOCTL/device control including pipe transceive, and tree disconnect. Max read/write sizes delegate to the owning client.

## Control Flow
Each method constructs the relevant SMB1 command or transaction subcommand, sends it with the tree ID, waits for the expected response command, parses success payloads, and returns the SMB status. Directory enumeration loops with find-next until end-of-search. Info-level passthrough controls whether native file information classes are used or converted to legacy query information levels. `FSCTL_PIPE_TRANSCEIVE` is routed to a named-pipe transaction; other IOCTLs use NT_TRANSACT IOCTL.

## State, Dependencies, and Integration
The file store keeps an `SMB1Client` reference and tree ID. It depends on many SMB1 command/transaction structures, query information helpers, security descriptor types, and NTSTATUS conventions. `NamedPipeHelper`, `ServerServiceHelper`, and DFS helpers call through this abstraction.

## Risks and Test Signals
Several inherited operations throw `NotImplementedException` (`FlushFileBuffers`, byte-range locks, handle-based directory query, filesystem set, change notify, cancel). `ToFileStatus()` mappings for create dispositions appear counterintuitive for open-if/overwrite cases. Tests should cover all implemented request/response pairs, timeout versus disconnect mapping, large directory enumeration, info-level fallback, pipe transceive, unsupported methods, and create-disposition status mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB1FileStore.cs -->
