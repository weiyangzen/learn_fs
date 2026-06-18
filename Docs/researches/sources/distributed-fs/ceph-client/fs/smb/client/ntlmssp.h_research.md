# sources/distributed-fs/ceph-client/fs/smb/client/ntlmssp.h

## Purpose
`ntlmssp.h` defines NTLMSSP authentication wire constants, flags, AV pair identifiers, packed message structures, and builder/parser prototypes used by CIFS session setup.

## Important APIs, types, and functions
Constants include `NTLMSSP_SIGNATURE`, message types `NtLmNegotiate`, `NtLmChallenge`, `NtLmAuthenticate`, and negotiate flags for Unicode/OEM strings, signing, sealing, NTLM, anonymous, domain/workstation supplied, extended security, target info, version, 128-bit, key exchange, and 56-bit support. `enum av_field_type` names NTLM target-info AV pairs. Packed wire structures include `SECURITY_BUFFER`, `NEGOTIATE_MESSAGE`, `struct ntlmssp_version`, `struct negotiate_message`, `CHALLENGE_MESSAGE`, and `AUTHENTICATE_MESSAGE`. Prototypes cover `decode_ntlmssp_challenge()`, `build_ntlmssp_negotiate_blob()`, `build_ntlmssp_smb3_negotiate_blob()`, and `build_ntlmssp_auth_blob()`.

## Control flow
The header has no implementation flow, but it defines the layout that the NTLMSSP builder/parser code follows: client sends negotiate, server returns challenge with target info and nonce, client sends authenticate with LM/NT responses, identity strings, optional version, session key, and negotiated flags.

## State and persistence behavior
No local state is stored here. The structures describe transient authentication blobs. Sensitive material referenced by these blobs, such as session keys and challenge responses, lives in session/auth code and must be handled as secret memory there.

## Dependencies and integration points
The header depends on CIFS crypto key sizing and kernel endian types. It integrates with SMB session setup, NTLMv2 response generation, signing/sealing negotiation, and SMB2/3 negotiate blob construction.

## Risks
Risks are packed layout drift from the MS-NLMP wire format, endian mistakes in flags/message types, insufficient validation of `SECURITY_BUFFER` offsets/lengths by parser implementations, downgrade-prone negotiate flag choices, and incorrect handling of version fields between SMB1 and SMB2+ builders.

## Test signals
Test NTLMSSP negotiate/challenge/authenticate against Windows and Samba, validate blob offsets and lengths under short/oversized inputs, exercise Unicode and OEM names, domain/workstation supplied flags, target-info AV parsing, SMB2+ version-bearing negotiate blobs, key-exchange/sign/seal flag combinations, and malformed challenge rejection.
