# sources/distributed-fs/ceph-client/fs/smb/client/smb1encrypt.c

## Purpose
`smb1encrypt.c` implements SMB1 message signing and signature verification using the NTLM/CIFS session key and MD5-based SMB1 signing rules.

## Important APIs, types, and functions
The exported functions are `cifs_sign_rqst` and `cifs_verify_signature`. Internal `cifs_calc_signature` initializes an MD5 context with `server->session_key.response` and delegates request hashing to `__cifs_calc_signature`.

## Control flow
Signing skips packets without the security-signature flag or when negotiation is needed. Before session establishment it writes the dummy `BSRSPYL` signature. After session establishment it writes the current sequence number into the SMB header, advances expected response and next request sequence numbers, calculates the signature, and copies the first eight bytes into the header. Verification ignores pre-session packets and oplock-release lock requests, saves the server signature, writes the expected response sequence into the header, recalculates the signature under the server lock, and compares with `crypto_memneq`.

## State and persistence
The file mutates transient SMB request/response headers and runtime `server->sequence_number`. It consumes the runtime session key established during session setup. No durable state is written.

## Dependencies and integration points
It depends on kernel MD5 helpers, FIPS mode, crypto constant-time comparison, common CIFS signature hashing, SMB1 header structures, and server locking. It is used by SMB1 transport send/receive paths through `smb1_operations`.

## Risks and test signals
Risks include sequence-number drift on send failures or cancel requests, signing disabled in FIPS mode, missing session key material, dummy signature handling during setup, and verification over a mutated response buffer. Test signals include signed and unsigned mounts, FIPS mode, failed sends after sequence increments, session setup dummy signatures, oplock-break responses, and tampered response signatures returning `-EACCES`.
