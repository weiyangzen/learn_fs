# sources/distributed-fs/ceph-client/include/net/sctp/auth.h

## Purpose
This SCTP-AUTH header defines shared-key and HMAC primitives used to authenticate selected SCTP chunks according to the SCTP authentication extension.

## Important APIs, Types, And Functions
`struct sctp_hmac` identifies supported HMAC algorithms and output lengths. `struct sctp_auth_bytes` is a refcounted variable-length byte vector for key material. `struct sctp_shared_key` binds a key id, key bytes, refcount, deactivation flag, and list node. APIs create, copy, hold, release, activate, deactivate, delete, and destroy keys, select HMAC algorithms, verify HMAC ids, decide whether chunk IDs require send/receive authentication, compute HMACs, and initialize/free endpoint auth state.

## Control Flow
Endpoint keys are configured by socket options, copied into associations, and combined with peer random/chunk/HMAC parameters during association setup. When outbound or inbound chunks require authentication, lookup and default-HMAC selection feed `sctp_auth_calculate_hmac()`.

## State And Persistence
Key material persists in endpoint and association key lists with explicit refcounts. Active key ids and deactivated keys are long-lived association state; raw `sctp_auth_bytes` may be shared.

## Dependencies And Integration Points
It integrates with `sctp_endpoint`, `sctp_association`, SCTP chunk parameter parsing, user API key objects, and crypto HMAC implementations declared through SCTP constants.

## Risks And Test Signals
Risks include key lifetime races, accepting unsupported HMAC ids, authenticating the wrong chunk set, deactivated-key misuse, and memory disclosure of key material. Test signals include SCTP_AUTH socket-option tests, authenticated COOKIE/ASCONF cases, unsupported algorithm negotiation, and key add/delete/deactivate sequences.
