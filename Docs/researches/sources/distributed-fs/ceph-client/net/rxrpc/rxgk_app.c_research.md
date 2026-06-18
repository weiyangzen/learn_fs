<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_app.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk_app.c

## Purpose
`rxgk_app.c` contains application-specific RxGK token handling for YFS. It decrypts token containers, looks up server secrets, decodes default YFS tickets, and instantiates rxrpc keys that expose session key material to the generic RxGK transport-key logic.

## Important APIs, Types, And Functions
The file implements `rxgk_yfs_decode_ticket()` and `rxgk_extract_token()`. It uses `struct rxgk_key`, `RXGK_TokenContainer`, XDR length helpers, `rxrpc_look_up_server_security()`, `rxgk_set_up_token_cipher()`, `rxgk_decrypt_skb()`, `key_alloc()`, and `key_instantiate_and_link()`.

## Control Flow
`rxgk_extract_token()` parses kvno, enctype, and encrypted-token length from the response, looks up the matching service key, sets up the Kerberos AEAD for server token decryption, decrypts the token region in place, and delegates ticket parsing to the security module's default decoder. The YFS decoder validates minimum ticket shape, reads enctype and session-key length, copies the ticket into an XDR-formatted rxrpc key payload, maps ticket fields into token metadata, copies session key and original ticket, instantiates an anonymous rxrpc key, marks it `no_leak_key`, and returns it.

## State And Persistence
The decoder allocates temporary sensitive payload buffers and returns a live `struct key` containing `struct rxrpc_key_token` data. It does not persist state in the connection directly; callers install the returned key after authenticator verification.

## Dependencies And Integration Points
This file bridges RxGK response verification, rxrpc key type parsing, server keyrings, Kerberos crypto, and YFS ticket format. It is called from `rxgk_verify_response()` through `rxgk_extract_token()`.

## Risks And Edge Cases
Length and XDR rounding checks are security-critical. The code currently uses `current_cred()` and TODO comments for socket credentials/ownership. Unsupported or missing server keys map to protocol aborts. Sensitive buffers are freed with `kfree_sensitive()`.

## Test Signals
Test short token/ticket lengths, bad key lengths, unsupported enctypes, missing/expired server keys, successful YFS ticket decode, instantiated key payload fields, sensitive free paths, and credential/key permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_app.c -->
