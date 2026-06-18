<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_common.h -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk_common.h

## Purpose
`rxgk_common.h` defines shared RxGK context state, XDR helpers, prototypes for app/KDF modules, and inline SKB crypto helpers used by RxGK packet and token processing.

## Important APIs, Types, And Functions
Important definitions include `struct rxgk_context`, `RXGK_TK_NEEDS_REKEY`, `xdr_round_up()`, `xdr_round_down()`, `xdr_object_len()`, prototypes for `rxgk_yfs_decode_ticket()`, `rxgk_extract_token()`, `rxgk_put()`, `rxgk_generate_transport_key()`, `rxgk_set_up_token_cipher()`, and inline helpers `rxgk_decrypt_skb()` and `rxgk_verify_mic_skb()`.

## Control Flow
The inline helpers convert SKB ranges to scatterlists, call Kerberos decrypt/MIC verification helpers, update caller-provided offset/length on success, and translate crypto errors into RxGK abort codes such as `RXGK_SEALEDINCON`, `RXGK_PACKETSHORT`, and `RXGK_INCONSISTENCY`.

## State And Persistence
`struct rxgk_context` is the persistent per-key-number transport context. It stores refcount, key number, expiry, byte lifetime, Kerberos enctype/key pointer, TX/RX AEADs, TX/RX checksum transforms, and response encryption transform.

## Dependencies And Integration Points
The header depends on kernel Kerberos crypto APIs and is shared by `rxgk.c`, `rxgk_app.c`, and `rxgk_kdf.c`. Its error-code mapping directly affects connection abort behavior from packet verification and token decryption.

## Risks And Edge Cases
Scatterlist arrays are fixed at 16 entries; unusually fragmented SKBs beyond that rely on `skb_to_sgvec()` failure handling. Offset/length mutation must happen only after successful crypto. Context lifetime requires every `rxgk_get_key()` reference to be paired with `rxgk_put()`.

## Test Signals
Compile coverage across RxGK files, fragmented SKB decrypt/MIC cases, checksum mismatch abort-code mapping, packet-short mapping, context refcount KASAN/KCSAN checks, and XDR rounding boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_common.h -->
