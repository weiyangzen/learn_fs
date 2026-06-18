# sources/distributed-fs/ceph-client/fs/smb/server/ntlmssp.h

## Purpose
Defines NTLMSSP constants and packed wire structures used by ksmbd authentication. It describes negotiate, challenge, authenticate, AV pair, NTLMv2 response, and per-session NTLMSSP state layouts.

## Important APIs, Types, and Functions
- Constants define the NTLMSSP signature, server target name (`KSMBD`), crypto/session key sizes, encrypted password sizes, message type values, and all major NTLMSSP negotiate flags.
- `enum av_field_type` lists target-info AV pair ids such as NetBIOS/DNS names, flags, timestamp, target name, and channel bindings.
- `struct security_buffer` is the packed length/maximum/offset triple used throughout NTLMSSP messages.
- `struct target_info` represents variable-length AV pair entries.
- `struct negotiate_message`, `struct challenge_message`, and `struct authenticate_message` model NTLMSSP type 1, type 2, and type 3 packets, with flexible trailing string buffers where appropriate.
- `struct ntlmv2_resp` models the fixed prefix of an NTLMv2 response blob.
- `struct ntlmssp_auth` stores per-authentication/session state: whether the session key is per SMB session, client/server flags, challenge ciphertext, and server challenge key.

## Control Flow
Authentication code parses a type 1 negotiate message, records client flags, creates a type 2 challenge with target information and random challenge bytes, then validates a type 3 authenticate message. The negotiated flags select Unicode/OEM strings, signing/sealing, key exchange, NTLM version behavior, and target info handling. `ntlmssp_auth` carries the challenge and flags across the multi-step session setup exchange.

## State and Persistence
This header defines only packet and transient authentication state. `ntlmssp_auth` is per connection/session setup and is not persistent. Challenge material and ciphertext are sensitive and should be cleared by implementation cleanup paths.

## Dependencies and Integration Points
The structures are consumed by auth/session setup code and inform key sizes in `user_session.h`. Endianness is explicit with `__le16`/`__le32`/`__le64`, and `__packed` preserves wire layout. The resulting session key feeds SMB signing/encryption key derivation in SMB2/SMB3 code.

## Risks and Edge Cases
- Flexible trailing fields require strict bounds checking by parsers; this header only defines layout.
- `sizeof(NTLMSSP_SIGNATURE)` includes the NUL terminator, so message signature arrays are one byte longer than the visible string; parser/generator code must match existing convention.
- Security buffer offsets are client-controlled on inbound messages and must be validated against total blob length.
- Negotiate flag combinations can request unsupported signing/sealing/key exchange behavior; auth code must reject or downgrade consistently with SMB dialect policy.

## Test Signals
Tests should parse valid and malformed NTLMSSP type 1/2/3 blobs, out-of-range security buffers, Unicode and OEM names, NTLMv2 responses with AV pairs, anonymous/identify flags, signing/sealing negotiation, key exchange, and channel binding AV pairs. Fuzzing session setup security blobs is high value.
