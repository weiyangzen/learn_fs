<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk.c

## Purpose
`rxgk.c` implements YFS RxGK, a GSSAPI/Kerberos-based AF_RXRPC security class. It handles server-key parsing, connection security initialization, rekeying, packet signing/encryption/verification, challenge/response generation, userspace/kernel challenge responses, response verification, and cleanup.

## Important APIs, Types, And Functions
The file exports `rxgk_yfs`, `rxgk_kernel_query_challenge()`, and `rxgk_kernel_respond_to_challenge()`. Major internals include `rxgk_preparse_server_key()`, `rxgk_rekey()`, `rxgk_get_key()`, `rxgk_init_connection_security()`, `rxgk_alloc_txbuf()`, `rxgk_secure_packet()`, `rxgk_verify_packet()`, `rxgk_issue_challenge()`, `rxgk_validate_challenge()`, `rxgk_challenge_to_recvmsg()`, `rxgk_construct_response()`, `rxgk_sendmsg_respond_to_challenge()`, `rxgk_verify_authenticator()`, `rxgk_verify_response()`, and `rxgk_clear()`.

## Control Flow
Connection initialization derives the first transport key from the client token or server response. TX allocation reserves crypto/header space according to security level. Securing a packet obtains the current key, validates the rxrpc key, writes the low key number into the wire checksum field, and either leaves data plain, attaches a MIC, or encrypts an RxGK header plus payload. Verification obtains the key indicated by the packet key number, possibly rekeying, then verifies MICs or decrypts and validates sealed headers. Server challenge sends a random nonce; client response builds token, ticket, and encrypted authenticator with optional appdata. Server response verification decrypts the token, instantiates a session key, derives transport keys, decrypts the authenticator, validates nonce/level/epoch/cid/call counters, and installs `conn->key`.

## State And Persistence
RxGK persistent state lives in `conn->rxgk`: key ring slots, current key number, enctype, nonce, and start time. Each `struct rxgk_context` holds usage refs, key number, expiry, byte lifetime, Kerberos enctype, source key, AEAD/shash transforms, and rekey flags. Connection security locks protect slow rekey generation and fast key use.

## Dependencies And Integration Points
The file depends on crypto Kerberos helpers, `rxgk_common.h` KDF/decrypt helpers, app-specific ticket decoding in `rxgk_app.c`, response transmission in `output.c`, OOB/recvmsg challenge delivery, keyring server-key lookup, and the generic security dispatcher.

## Risks And Edge Cases
Only 16 key-number bits are exposed on wire, so rekey logic accepts current, previous, or next low-word values. Rekey rollover can mark connections non-reusable. Authenticator parsing must reject short, misaligned, stale, or inconsistent call counters. Temporary errors during token processing deliberately cause response retry rather than immediate abort.

## Test Signals
Cover all supported Kerberos enctypes, plain/auth/encrypt packet paths, key expiry and byte-life rekey, previous/current/next key-number receive, challenge OOB userspace appdata, kernel challenge response, malformed token/authenticator aborts, call-counter synchronization, and cleanup refcounting of `rxgk_context` ciphers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk.c -->
