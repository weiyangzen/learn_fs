# sources/distributed-fs/ceph-client/net/xfrm/xfrm_output.c

Purpose: `xfrm_output.c` is the common outbound XFRM/IPsec encapsulation engine. It prepares transport/tunnel/BEET/route-optimization/custom mode headers, applies state validation and replay/lifetime accounting, invokes protocol output or offload, handles netfilter post-routing loops, and emits PMTU errors.

Important APIs: Exported functions include `xfrm_output_resume()`, `xfrm_output()`, `xfrm4_tunnel_check_size()`, `xfrm6_tunnel_check_size()`, and `xfrm_local_error()`. Internal helpers cover skb head/tail expansion, dst stack popping, IPv4/IPv6 transport output, BEET and tunnel encapsulation, outer mode dispatch, GSO segmentation, packet offload direct output, and inner protocol recording for offload.

Control flow: `xfrm_output()` clears AF skb control blocks, handles packet offload early, resets secpath for software output, prepares offload secpath when allowed, segments GSO if needed, fixes partial checksums, then enters `xfrm_output_resume()`. `xfrm_output_one()` ensures skb space, applies state mark, calls `xfrm_outer_mode_output()` or mode callback `prepare_output`, validates state/expiry/replay under lock, updates lifetimes, invokes `x->type->output()` or `type_offload->encap()`, pops the dst stack, and repeats until a tunnel boundary. Resume then runs local_out, dst_output, and NF_INET_POST_ROUTING as needed.

State and persistence: Outbound processing updates SA byte/packet lifetime counters and `lastused`, advances replay sequence state through protocol output, manipulates skb dst/secpath/headers, and stores offload metadata such as `inner_ipproto`.

Dependencies and integration: Depends on XFRM state/mode/type callbacks, IPv4/IPv6 routing and PMTU helpers, netfilter, GSO, hardware offload from `xfrm_device.c`, `xfrm_inout.h`, and custom mode callbacks such as IP-TFS.

Risks: Header pointer arithmetic is fragile across transport, tunnel, BEET, IPv6 extension headers, and custom modes. PMTU behavior must avoid black holes while respecting DF semantics. Packet offload direct output must not bypass required software filtering in transport/local cases. Async protocol output must resume without double-freeing skbs.

Test signals: Cover IPv4/IPv6 transport, tunnel, BEET, route optimization, IP-TFS custom mode, nested bundles, post-routing reroute, GSO and partial checksum, packet and crypto offload, expired states, replay overflow, PMTU/local errors, IPv4 options/IPv6 extension headers, and async output resume from ESP/IPComp.
