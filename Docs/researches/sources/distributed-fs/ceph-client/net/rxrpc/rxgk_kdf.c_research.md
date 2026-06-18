<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_kdf.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk_kdf.c

## Purpose
`rxgk_kdf.c` derives RxGK transport keys and per-usage crypto transforms from Kerberos session keys. It also owns `struct rxgk_context` destruction and token-decryption cipher setup.

## Important APIs, Types, And Functions
Important functions include `rxgk_put()`, `rxgk_generate_transport_key()`, and `rxgk_set_up_token_cipher()`. Internal helpers include `rxgk_free()`, `rxgk_derive_transport_key()`, and `rxgk_set_up_ciphers()`. Usage constants select client/server packet encryption, MIC, response encryption, and server token encryption keys.

## Control Flow
Transport-key generation allocates a context, finds the Kerberos enctype, derives TK with PRF+ over epoch, cid, start time, and key number, derives response encryption plus direction-specific TX/RX MIC or encryption transforms according to service/client role and security level, computes byte lifetime and jiffies expiry, and returns a referenced context. Token cipher setup prepares the server-token AEAD from a service secret and enctype.

## State And Persistence
`struct rxgk_context` owns AEAD and shash transform pointers until its refcount reaches zero. It records remaining byte lifetime and expiry time for rekey decisions. Temporary key material buffers are zeroed/freed through sensitive free paths where appropriate.

## Dependencies And Integration Points
The file depends on Kerberos crypto helpers, rxrpc connection role/security-level fields, key tokens from rxrpc key type, and the rekey/packet paths in `rxgk.c`.

## Risks And Edge Cases
Direction-specific usage constants must be paired correctly for clients versus services or packets become unverifiable. Crypto transform block/auth sizes are checked against Kerberos tables. Byte-life semantics accept both exponent-like values and literal counts. Lifetime conversion must avoid jiffies overflow.

## Test Signals
Test every supported enctype and security level, client/server direction interop, transform allocation failures, byte-life and expiry-triggered rekey, token cipher setup with unsupported enctype, and refcounted cleanup of partially initialized contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_kdf.c -->
