# sources/distributed-fs/ceph-client/net/tls/tls.h

## Purpose
Defines internal kTLS interfaces, cipher metadata helpers, software/device offload prototypes, strparser contracts, record sequence helpers, and TLS record header/AAD construction helpers shared by TLS core, software, and device offload code.

## Important APIs, Types, And Functions
`struct tls_cipher_desc` describes nonce, IV, key, salt, tag, record sequence sizes and offsets, cipher name, offload capability, and crypto-info size. `get_cipher_desc` bounds cipher lookup. `crypto_info_iv/key/salt/rec_seq` compute typed offsets into user crypto-info structs. `struct tls_rec` models software TLS records with plaintext/encrypted sk_msgs, AEAD scatterlists, content type, AAD, IV, and inline AEAD request. The header declares context lifecycle, protocol initialization, software send/receive/resource APIs, device send/splice/write-space/offload APIs, cmsg processing, decrypt, fallback init, strparser APIs, and TX push helpers.

## Control Flow And State
Inline helpers manipulate record sequence state and record formatting. `tls_advance_record_sn` increments TX sequence and IV where TLS 1.2 GCM requires it, aborting on wrap. `tls_xor_iv_with_seq` handles TLS 1.3/ChaCha nonce behavior. `tls_fill_prepend` writes the TLS record header and explicit IV/nonce fields. `tls_make_aad` builds AEAD additional data differently for TLS 1.2 and 1.3. Under `CONFIG_TLS_DEVICE`, real device-offload prototypes are exposed; otherwise inline stubs return success for init/cleanup and `-EOPNOTSUPP` for offload setup.

## Dependencies And Integration Points
Depends on public `net/tls.h`, TLS protocol structures, `skmsg`, byte order helpers, AEAD users, and TLS strparser state. It is the central private API boundary between `tls_main`, `tls_sw`, `tls_strp`, `tls_device`, and `tls_device_fallback`.

## Risks And Test Signals
Risks include cipher descriptor offset mistakes, record sequence wrap handling, TLS 1.2 vs TLS 1.3 header/AAD differences, config-stub mismatches, and shared helper changes affecting both software and hardware paths. Test signals include cipher setup for every supported cipher, TLS 1.2 and 1.3 send/receive, record sequence boundary tests, software-only builds, device-offload builds, and fallback encryption validation.
