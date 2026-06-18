# sources/distributed-fs/ceph-client/net/ipv4/esp4_offload.c

## Purpose
`esp4_offload.c` adds IPv4 ESP GRO, GSO, and XFRM type offload support. It lets decrypted ESP packets participate in GRO, segments ESP GSO packets according to XFRM outer mode, and prepares outbound ESP packets for hardware crypto offload or software fallback.

## Important APIs, Types, and Functions
The file registers `esp4_offload` with `inet_add_offload(IPPROTO_ESP)` and `esp_type_offload` with `xfrm_register_type_offload(AF_INET)`. Important callbacks are `esp4_gro_receive()`, `esp4_gso_segment()`, `esp_input_tail()`, `esp_xmit()`, and `esp4_gso_encap()`.

Segmentation helpers are `xfrm4_tunnel_gso_segment()`, `xfrm4_transport_gso_segment()`, `xfrm4_beet_gso_segment()`, and `xfrm4_outer_mode_gso_segment()`. The file reuses normal ESP helpers from `esp4.c`: `esp_output_head()`, `esp_output_tail()`, and `esp_input_done2()`.

## Control Flow
GRO receive starts at `esp4_gro_receive()`. It pulls to the GRO offset, parses SPI and sequence, ensures or creates a security path, looks up the inbound XFRM state unless crypto offload already marked the skb `CRYPTO_DONE`, rejects states for the wrong direction, stores the state in the secpath, marks `XFRM_GRO`, records SPI metadata, detects UDP encapsulation, and invokes `xfrm_input()`. GRO returns `ERR_PTR(-EINPROGRESS)` because XFRM owns completion.

GSO segmentation starts at `esp4_gso_segment()`. It requires `xfrm_offload()` metadata and `SKB_GSO_ESP`, validates SPI against the last secpath state, pulls the ESP header and IV, adjusts feature masks when hardware ESP or hardware ESP checksum support is unavailable, marks `XFRM_GSO_SEGMENT`, and dispatches by XFRM outer mode. Tunnel mode calls Ethernet/IP segmentation for the inner family, transport mode calls the next protocol offload, and BEET mode accounts for BEET pseudo headers or IPv6 extension headers before invoking the inner protocol segmenter.

Outbound offload transmit starts at `esp_xmit()`. It checks whether the skb device matches the SA offload device and whether `NETIF_F_HW_ESP` is available. If not, it sets `CRYPTO_FALLBACK` and uses the software `esp_output_head()` / `esp_output_tail()` path. If hardware offload is available, it computes padding and sequence information, updates the ESP and IPv4 headers, attaches `SKB_EXT_SEC_PATH`, marks `XFRM_XMIT`, and returns with encryption deferred to the device.

`esp_input_tail()` is used for inbound offloaded packets after hardware crypto. It validates the ESP header and IV, clears checksum state unless `CRYPTO_DONE` is present, and feeds the packet into `esp_input_done2()` for common trailer removal and post-decrypt processing.

## State and Persistence Behavior
State is packet-local and runtime-only. The callbacks read and update `struct xfrm_offload` flags such as `CRYPTO_DONE`, `XFRM_GRO`, `XFRM_GSO_SEGMENT`, `CRYPTO_FALLBACK`, `XFRM_XMIT`, and sequence fields. They use the skb secpath to find the active `struct xfrm_state` and may attach `SKB_EXT_SEC_PATH` for hardware transmit.

No durable state is written. Device capabilities, `x->xso.dev`, `skb->dev->gso_partial_features`, and netdevice feature masks determine whether packets take hardware offload or software fallback.

## Dependencies and Integration Points
The file depends on IPv4 inet offload registration, generic GRO/GSO helpers, XFRM offload metadata, secpath management, skb extension support, crypto AEAD properties for IV/auth lengths, IPv4 header checksum helpers, and mode-specific XFRM semantics. It integrates with `esp4.c` through shared post-crypto helpers and with device drivers through `NETIF_F_HW_ESP` and `NETIF_F_HW_ESP_TX_CSUM`.

## Risks and Edge Cases
GRO must restore the skb offset and mark flush/no-same-flow on parse or lookup failure. Missing `secpath_reset()` on failures would leak state. Direction checks are important because wrong-direction offloaded SAs should fall back to normal error/audit behavior.

GSO risks include incorrect feature masking, wrong inner protocol selection for BEET, mishandling IPv6 inner headers, accepting mismatched SPI, or pulling too little data for IV length. Hardware UDP-encapsulated ESP is special because the code must correct the IPv4 protocol field outside the normal XFRM stack path.

Transmit fallback must preserve sequence accounting across GSO segments, update high sequence bits on wrap, linearize when device features require it, and reset secpath after software crypto. Hardware transmit must attach secpath extension successfully or fail without sending malformed packets.

## Test Signals
Useful tests include GRO with normal and `CRYPTO_DONE` packets, invalid SPI parsing, wrong-direction SA rejection, secpath depth exhaustion, UDP-encapsulated GRO, GSO segmentation for tunnel/transport/BEET, BEET IPv4 pseudo-header and IPv6 inner cases, feature masks with and without hardware ESP checksum, fallback software encryption, GSO sequence increment by `gso_segs`, sequence wrap high-bit increment, hardware UDP encapsulation protocol correction, and module init/exit registration ordering.
