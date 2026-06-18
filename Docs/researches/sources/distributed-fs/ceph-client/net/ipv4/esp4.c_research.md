# sources/distributed-fs/ceph-client/net/ipv4/esp4.c

## Purpose
`esp4.c` implements the IPv4 Encapsulating Security Payload transform for the XFRM/IPsec stack. It registers the IPv4 ESP protocol handler and XFRM type, initializes crypto state for ESP security associations, encrypts outbound packets, decrypts inbound packets, handles ESP NAT-T and optional ESP-in-TCP encapsulation, processes ICMP errors for PMTU/redirects, and exports common ESP helpers used by offload code.

## Important APIs, Types, and Functions
The XFRM type is `esp_type`, with `.init_state = esp_init_state`, `.destructor = esp_destroy`, `.input = esp_input`, and `.output = esp_output`. IPv4 protocol registration is `esp4_protocol`, whose receive handler is `xfrm4_rcv`, input handler is `xfrm_input`, and error handler is `esp4_err()`.

Scratch state is stored in `struct esp_skb_cb` in `skb->cb`, with temporary crypto request memory allocated by `esp_alloc_tmp()`. `struct esp_output_extra` stores ESN high sequence bits and the ESP header offset while ESN temporarily moves header fields for AEAD associated data.

Exported helpers are `esp_output_head()`, `esp_output_tail()`, and `esp_input_done2()`. Internal helpers include `esp_output_encap()`, `esp_output_udp_encap()`, `esp_output_tcp_encap()`, `esp_output_done()`, `esp_output_done_esn()`, `esp_input_set_header()`, `esp_input_done_esn()`, `esp_remove_trailer()`, `esp_init_aead()`, and `esp_init_authenc()`.

## Control Flow
Outbound processing starts in `esp_output()`. It records the original next-header protocol from `skb_mac_header()`, marks the packet as ESP, computes optional traffic-flow-confidentiality padding, block-size padding, authentication length, ciphertext length, and trailer length, then calls `esp_output_head()` to make tailroom or append a page fragment and fill the ESP trailer. The function then writes SPI and sequence number, adjusts skb data to include the network header, and calls `esp_output_tail()` for AEAD encryption.

`esp_output_head()` handles encapsulation first if `x->encap` is set. UDP encapsulation writes a UDP header and updates the outer protocol field when appropriate; TCP encapsulation validates the associated ESP-in-TCP socket and writes the length field. The function then tries low-copy trailer placement in skb tailroom or a new page frag, falling back to `skb_cow_data()` when cloned, fragmented, or lacking space.

`esp_output_tail()` builds scatterlists over the ESP header, IV, payload, trailer, and ICV. For ESN it moves the ESP header backward by four bytes so high sequence bits become associated data, sets a completion callback that restores the header, derives the IV from the 64-bit sequence value, and calls `crypto_aead_encrypt()`. Synchronous completion restores ESN headers and frees scratch memory; asynchronous completion resumes XFRM output or hands ESP-in-TCP packets to the TCP ULP path.

Inbound processing starts in `esp_input()`. It validates that the skb contains the ESP header and IV, computes encrypted length, ensures writable linear/frags as needed, allocates scratch request memory, moves ESN headers when required, builds a scatterlist over the whole ESP packet, clears checksum state, and calls `crypto_aead_decrypt()`. Completion flows through `esp_input_done2()`, which frees scratch memory, removes and validates padding/trailer, handles NAT-T source mapping changes through `km_new_mapping()`, adjusts checksum semantics for transport-mode encapsulation, pulls the ESP header/IV, resets the transport header for tunnel/IPTFS, and drops dummy `IPPROTO_NONE` packets.

State initialization selects either native AEAD (`esp_init_aead()`) or authenc composition (`esp_init_authenc()`), allocates a `crypto_aead`, sets key and ICV size, computes XFRM header and trailer lengths, and validates encapsulation types. Module init registers the XFRM type and IPv4 protocol in order; exit deregisters both.

## State and Persistence Behavior
Per-SA crypto state is kept in `x->data` as a `struct crypto_aead *` and freed by `esp_destroy()`. Packet-local state is in skb control blocks and temporary allocations that hold IVs, AEAD requests, scatterlists, and optional ESN metadata. The file does not persist state outside memory.

Sequence numbers come from `XFRM_SKB_CB(skb)->seq.output` for normal output and `XFRM_SKB_CB(skb)->seq.input` for ESN input. Encapsulation parameters are read under `x->lock` to avoid races with SA updates. ESP-in-TCP output may consume the skb asynchronously and return `-EINPROGRESS`.

## Dependencies and Integration Points
The implementation depends on the kernel crypto AEAD API, scatterlist helpers, skb frag/page reference management, XFRM core, IPv4 protocol registration, UDP/TCP encapsulation headers, ESP-in-TCP ULP support, PF_KEY/netlink algorithm descriptions, ICMP PMTU/redirect handling, and route cache update helpers.

It integrates with offload code through exported `esp_output_head()`, `esp_output_tail()`, and `esp_input_done2()`. It integrates with key management through `km_new_mapping()` when NAT-T peer mapping changes. ICMP errors are mapped to `ipv4_update_pmtu()` and `ipv4_redirect()` after locating the matching XFRM state by SPI.

## Risks and Edge Cases
The highest-risk areas are skb geometry and crypto scatterlist construction. Cloned skbs, shared frags, frag lists, insufficient tailroom, page-frag recycling, non-inplace output, asynchronous AEAD completion, and ESP-in-TCP consumption all have distinct memory ownership paths.

ESN handling is subtle because the code temporarily rewrites the ESP header to include high sequence bits in AEAD associated data and must restore it before the packet continues. Bad restoration would corrupt SPI/sequence fields or break replay protection.

Input validation must reject too-short ESP packets, invalid encrypted length, garbage padding, missing IV, dummy packets, and malformed encapsulation. NAT-T accepts source address/port changes by notifying key management, which is intentional but security-sensitive.

Crypto initialization must reject missing algorithms, overlong generated algorithm names, invalid authenc ICV sizes, unsupported encapsulation, and key/authsize setup failure while ensuring sensitive composed keys are freed with `kfree_sensitive()`.

## Test Signals
Test vectors should cover AEAD and authenc SAs, tunnel/transport/BEET/IPTFS header length accounting, ESN and non-ESN encryption/decryption, async crypto completion, NAT-T UDP encapsulation, ESP-in-TCP enabled and unavailable cases, PMTU ICMP handling, redirects, page-frag trailer allocation, `skb_cow_data()` fallback, and malformed padding/truncated packets.

Regression signals include no leaks of crypto scratch memory, correct skb ownership on `-EINPROGRESS`, checksum state after NAT-T transport mode, correct protocol restoration after decrypt, proper `IPPROTO_NONE` dummy drop, and successful module register/unregister rollback when protocol registration fails.
