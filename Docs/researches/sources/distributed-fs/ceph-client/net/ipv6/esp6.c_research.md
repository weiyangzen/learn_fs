# sources/distributed-fs/ceph-client/net/ipv6/esp6.c

## Purpose
Implements software IPv6 IPsec Encapsulating Security Payload (ESP) for XFRM. It performs outbound encryption/authentication, inbound decryption/authentication, padding/trailer handling, ESN header manipulation, UDP and optional TCP ESP encapsulation, error handling, and XFRM type/protocol registration.

## Important APIs, Types, and Functions
Key structures are `struct esp_skb_cb` and `struct esp_output_extra`. Allocation/layout helpers include `esp_alloc_tmp()`, `esp_tmp_iv()`, `esp_tmp_req()`, and `esp_req_sg()`. Output path functions are `esp6_output()`, exported `esp6_output_head()`, exported `esp6_output_tail()`, encapsulation helpers, and async callbacks. Input path functions are `esp6_input()`, exported `esp6_input_done2()`, `esp_remove_trailer()`, and ESN restore/set helpers. State setup uses `esp_init_aead()`, `esp_init_authenc()`, and `esp6_init_state()`.

## Control Flow
Outbound ESP selects inner protocol, computes TFC/padding/auth trailer lengths, optionally adds UDP/TCP encapsulation, appends trailer in skb tailroom or page frags, writes SPI/sequence, handles ESN by temporarily shifting the ESP header, builds source/destination scatterlists, derives IV from sequence, runs AEAD encryption, fixes encapsulation checksum, and resumes XFRM or queues ESP-in-TCP. Inbound ESP validates minimum header/IV, ensures writable data, shifts ESN high bits into associated data when needed, decrypts in place, removes auth/padding/trailer, processes NAT-T source updates, adjusts checksum state, pulls ESP header/IV, and returns next header or drops dummy packets.

## State and Persistence
Per-SA state is the `crypto_aead` transform in `x->data`, header/trailer length metadata in `x->props`, optional `x->xfrag` page-frag cache, encapsulation template, and replay sequence information from XFRM control blocks. Per-packet temporary memory holds IV, AEAD request, ESN extra, and scatterlists.

## Dependencies and Integration Points
Depends on XFRM, crypto AEAD/authenc, skbuff scatterlists, IPv6 routing/error updates, UDP/TCP ESP encapsulation, inet6 socket lookup for ESP-in-TCP, and exported helpers consumed by `esp6_offload.c`.

## Risks and Test Signals
Risks include scatterlist sizing, page-frag lifetime, ESN header restore on sync/async errors, checksum handling for UDP NAT-T, ESP-in-TCP queue ownership, padding validation, and offload interop. Test signals include AEAD and authenc SAs, ESN wrap, transport/tunnel/BEET/IPTFS modes, UDP and TCP encapsulation, async crypto providers, malformed pad length, NAT mapping notification, PMTU redirect handling, and XFRM stats on protocol errors.
