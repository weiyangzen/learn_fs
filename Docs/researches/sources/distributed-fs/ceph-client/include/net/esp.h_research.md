# sources/distributed-fs/ceph-client/include/net/esp.h

Read `sources/distributed-fs/ceph-client/include/net/esp.h` completely for this pass (50 lines, 1209 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/esp.h_research.md`.

Purpose: declares shared ESP/IPsec helpers and per-packet output state for IPv4 and IPv6 ESP processing.

Important APIs/types/functions: `ip_esp_hdr()` returns the ESP header at the skb transport header. `esp_output_fill_trailer()` fills optional traffic-flow-confidentiality padding, ESP padding bytes 1..N, pad length, and next-header protocol. `struct esp_info` carries ESP header pointer, 64-bit sequence number, TFC length, tail length, padding length, crypto length, total length, fragment count, next protocol, and in-place crypto flag. Function prototypes cover `esp_output_head()`, `esp_output_tail()`, `esp_input_done2()`, and IPv6 variants `esp6_output_head()`, `esp6_output_tail()`, `esp6_input_done2()`.

Control flow: XFRM ESP output prepares `esp_info`, builds head/tail space, fills trailers, performs encryption/authentication, and finalizes skb output. Input async completion paths call `esp_input_done2()`/`esp6_input_done2()` after crypto processing. The same state shape supports IPv4 and IPv6 ESP implementations.

State and persistence: `esp_info` is per-packet transient state. `esp_output_fill_trailer()` mutates skb tailroom. Persistent IPsec SA state lives in `struct xfrm_state`, not in this header.

Dependencies and integration points: depends on skbuffs, ESP wire header declarations, and XFRM state. It integrates with IPv4/IPv6 ESP modules, crypto API callbacks, NAT-T/tunnel paths, and IPsec sequence/TFC/padding handling.

Risks: trailer filling assumes `plen >= 2` and enough writable tailroom. Padding bytes and pad length must match ESP RFC expectations. In-place versus non-in-place crypto affects skb fragment handling. Sequence number and TFC lengths must match XFRM/SA state or peers reject packets.

Test signals: IPv4/IPv6 ESP tunnel and transport mode, padding length boundaries, TFC padding, async crypto completion, fragmented skb handling, in-place/non-in-place paths, sequence number encoding, decryption/authentication failure handling, and interop with strongSwan/libreswan.
