<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxkad.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxkad.c

## Purpose
`rxkad.c` implements the legacy Kerberos/DES-based RxKAD AF_RXRPC security class. It parses server keys, initializes connection ciphers, signs or encrypts packets, verifies received packets, performs challenge/response authentication, decrypts Kerberos tickets, and creates server-side data keys.

## Important APIs, Types, And Functions
The file exports `rxkad` and `rxkad_kernel_respond_to_challenge()`. Major functions include `rxkad_preparse_server_key()`, `rxkad_init_connection_security()`, `rxkad_alloc_txbuf()`, `rxkad_prime_packet_security()`, `rxkad_secure_packet()`, `rxkad_verify_packet()`, `rxkad_issue_challenge()`, `rxkad_validate_challenge()`, `rxkad_respond_to_challenge()`, `rxkad_decrypt_ticket()`, `rxkad_decrypt_response()`, `rxkad_verify_response()`, `rxkad_clear()`, `rxkad_init()`, and `rxkad_exit()`.

## Control Flow
Client connection initialization allocates `pcbc(fcrypt)`, loads the session key, validates security level, and primes checksum IVs from epoch/cid/security index. TX buffers reserve 8-byte-aligned security headers for AUTH or ENCRYPT. Securing a packet computes the wire checksum from call/channel/sequence, then either encrypts only the level-1 header or encrypts the entire level-2 secure payload. Verification recomputes the checksum, decrypts the appropriate secure region in place, checks sequence/call-derived header checks, and trims payload length. Server challenge sends a nonce. Response generation builds an encrypted response plus ticket; verification looks up the service key, decrypts the ticket to obtain a session key/expiry, decrypts response fields, validates checksum, nonce, level, epoch/cid/security index, and call counters, then stores a server data key.

## State And Persistence
Connection state includes `conn->rxkad.cipher`, checksum IV, nonce, and security level. Global module state pins `rxkad_ci` and `rxkad_ci_req` for response decryption under `rxkad_ci_mutex`. Server keys store DES cipher payload and raw secret; response verification may instantiate connection-specific data keys.

## Dependencies And Integration Points
The file depends on Linux crypto skcipher APIs, rxrpc key types, generic security dispatch, packet output, OOB/kernel challenge response APIs, abort codes, and the rxrpc call/connection/channel model.

## Risks And Edge Cases
DES/FCrypt and PCBC are legacy and configuration-sensitive. Packet lengths must be 8-byte aligned before crypto. Ticket parsing enforces printable principal fields, lifetime, issue time, and maximum ticket length. Global response-decrypt cipher serialization is protected by a mutex. RxKAD does not support userspace `sendmsg()` challenge responses.

## Test Signals
Cover plain/auth/encrypt send and receive, checksum mismatch aborts, malformed secure headers, challenge version/min-level checks, expired/future tickets, unknown kvno, call-counter synchronization, cipher allocation failures, module init/exit cleanup, and interoperability with AFS RxKAD peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxkad.c -->
