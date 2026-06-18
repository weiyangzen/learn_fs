# sources/distributed-fs/ceph-client/net/xfrm/xfrm_ipcomp.c

Purpose: `xfrm_ipcomp.c` implements IP Payload Compression Protocol processing for XFRM states. It compresses outbound payloads, decompresses inbound payloads, manages async acomp requests, and initializes per-SA compression transforms.

Important APIs and types: Exported APIs are `ipcomp_input()`, `ipcomp_output()`, `ipcomp_destroy()`, and `ipcomp_init_state()`. `struct ipcomp_data` stores compression threshold and `crypto_acomp` transform. `struct ipcomp_skb_cb` overlays skb control block with XFRM cb plus request pointer. `struct ipcomp_req_extra` stores owning state and scatterlists after the acomp request.

Control flow: Inbound `ipcomp_input()` pulls the IPComp header, disables checksum offload, and calls `ipcomp_decompress()`. Request setup linearizes/cows skb as needed, builds source/destination scatterlists, allocates scratch pages, and starts `crypto_acomp_decompress()`. Completion calls `ipcomp_input_done2()` and resumes XFRM input. Outbound `ipcomp_output()` bypasses compression below threshold; otherwise it compresses, installs an IPComp header with CPI from state SPI, updates the previous protocol byte, and resumes XFRM output if async. `ipcomp_post_acomp()` rebuilds skb frags from destination pages and frees unused pages/request.

State and persistence: Per-SA `x->data` holds transform and threshold until state destroy. Async requests temporarily own pages and the request pointer in skb cb.

Dependencies and integration: Depends on Linux acomp crypto API, `xfrm_algo.c` compression descriptors, `xfrm_input_resume()`, `xfrm_output_resume()`, IPComp header definitions, skb fragment APIs, and XFRM state lifecycle.

Risks: Scatterlist/page ownership is delicate; error paths must free allocated pages and requests. skb control block overlay must remain within `skb->cb`. Compression is incompatible with encapsulation and rejects states with `x->encap`. Length validation prevents decompression truncation from producing invalid packets.

Test signals: Add IPComp SAs with deflate, missing calg rejection, encap rejection, below-threshold bypass, async and sync crypto completion, decompression length errors, memory-pressure request allocation failures, nonlinear skb input/output, and state destroy while no requests remain.
