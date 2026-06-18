# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.c

## Purpose
`zcrypt_ep11misc.c` implements EP11 helper services used by zcrypt and pkey. It validates EP11 AES/ECC key blobs, queries EP11 card/domain information, generates AES key blobs, imports clear AES keys through a temporary KEK and unwrap operation, derives protected keys from EP11 AES/ECC blobs, and scans APQNs for EP11 capability and wrapping-key matches.

## Important APIs, Types, And Functions
Exported APIs are `ep11_kb_wkvp()`, `ep11_check_aes_key_with_hdr()`, `ep11_check_ecc_key_with_hdr()`, `ep11_check_aes_key()`, `ep11_get_card_info()`, `ep11_get_domain_info()`, `ep11_genaeskey()`, `ep11_clr2keyblob()`, `ep11_kblob2protkey()`, `ep11_findcard2()`, plus init/exit. Internal helpers split/decode key blobs (`ep11_kb_split()`, `ep11_kb_decode()`), allocate EP11 CPRBs, write short ASN.1-like tags, prepare payload/URB headers, validate reply CPRB/payloads, perform generic info queries, single encrypt/decrypt operations, key unwrap, and key wrap.

## Control Flow
EP11 requests are built as `struct ep11_cprb` plus payload. `prep_head()` writes the outer sequence and function/domain fields; `prep_urb()` wraps request and reply CPRBs for `zcrypt_send_ep11_cprb()`. Reply handling first checks CPRB `ret_code`, then validates the payload sequence, function/domain fields, and embedded return value. Key generation chooses API ordinal V4 by default for extractable protected-key-capable blobs, V1 when flags do not request newer behavior, and V6 with an empty pinblob in secure-execution guests. Clear-key import generates a temporary AES-256 KEK, encrypts the clear key using CBC padding and a fixed IV, then unwraps the encrypted key into the requested EP11 blob. Protected-key derivation calls EP11 wrap with `CKM_IBM_CPACF_WRAP` and parses the returned protected-key info.

## State And Persistence
The file owns an EP11 CPRB mempool and a serialized device-status buffer for `ep11_findcard2()`. Sensitive request, reply, temporary KEK, encrypted key, and wrapped-key buffers are scrubbed where relevant before freeing. No disk persistence exists; durable cryptographic state remains on AP hardware.

## Dependencies And Integration Points
It depends on AP/zcrypt dispatch through `zcrypt_send_ep11_cprb()`, pkey constants for protected key types, token constants shared with CCA helpers, `ap_is_se_guest()` for secure-execution behavior, and AES block sizing. `zcrypt_cex4.c` uses the card/domain info APIs for sysfs.

## Risks And Test Signals
Risks include ASN.1 length handling limited to two-byte lengths, firmware reply parsing assumptions, fixed IV use for the internal KEK wrapping sequence, accidental mutation of old-style EP11 header overlay in `ep11_kblob2protkey()`, and mempool pressure under no-allocation callers. Test signals include validation of old/new AES and ECC blob headers, EP11 query parsing, API ordinal selection in secure-execution guests, clear-key import round trips, protected-key export for AES and ECC, and APQN filtering by API ordinal and WKVNP/WKVP.
