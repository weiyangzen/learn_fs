# sources/distributed-fs/ceph-client/net/ipv6/ah6.c

## Purpose
Implements IPv6 IPsec Authentication Header (AH) transformation support for XFRM. It registers an IPv6 XFRM type and protocol handler for `IPPROTO_AH`, authenticates outbound packets, validates inbound packets, normalizes mutable IPv6 fields during Integrity Check Value (ICV) computation, and handles AH-related ICMPv6 PMTU/redirect errors.

## Important APIs, Types, and Functions
Key structures are `struct ah_skb_cb`, which stores async hash scratch state in `skb->cb`, and `struct tmp_ext`, which saves mutable/restorable IPv6 addresses and extension headers. Core helpers include `ah_alloc_tmp()`, `zero_out_mutable_opts()`, `ipv6_clear_mutable_options()`, `ah6_output()`, `ah6_input()`, `ah6_output_done()`, `ah6_input_done()`, `ah6_err()`, `ah6_init_state()`, and `ah6_destroy()`. The module exports behavior through `struct xfrm_type ah6_type` and `struct xfrm6_protocol ah6_protocol`.

## Control Flow
Outbound processing reserves writable skb data, saves the first IPv6 header bytes and extension headers, zeros mutable fields/options, writes AH SPI/sequence metadata, builds scatterlists over packet data plus optional ESN high sequence bits, and runs `crypto_ahash_digest()`. Synchronous completion restores saved headers and copies the truncated ICV; asynchronous completion follows the same path in `ah6_output_done()`. Inbound processing validates AH length, copies the original ICV, zeros the in-packet ICV and mutable fields, hashes the packet plus optional ESN high bits, compares via `crypto_memneq()`, removes the AH header, restores the original IPv6 header chain, and resumes XFRM input.

## State and Persistence
Per-SA state is `struct ah_data` stored in `x->data`, including the crypto ahash transform and full/truncated ICV lengths. Per-packet temporary allocations hold saved header bytes, original authentication data, computed ICV, ahash request, and scatterlists. No on-disk persistence exists; module lifetime state is limited to protocol/type registration.

## Dependencies and Integration Points
Depends on XFRM, crypto ahash, IPv6 routing/error handling, scatterlist/skbuff helpers, PF_KEY algorithm descriptions, and optional Mobile IPv6 Home Address Option handling. AH integrates with IPv6 receive dispatch through `xfrm6_rcv`, XFRM input/output resume paths, `ip6_update_pmtu()`, and `ip6_redirect()`.

## Risks and Test Signals
Risk concentrates in extension-header normalization, malformed mutable options, ESN byte-order handling, async crypto lifetime, skb linearization/cow failures, and MIPv6 address rearrangement. Useful tests include AH transport/tunnel/BEET vectors, inbound bad-ICV rejection, ESN wrap cases, packets with routing/destination/hop options, async crypto providers, PMTU ICMP handling, and KASAN/KCSAN coverage around temporary buffer sizing.
