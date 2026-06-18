# sources/distributed-fs/ceph-client/net/xfrm/xfrm_input.c

Purpose: `xfrm_input.c` is the common inbound XFRM/IPsec processing state machine. It registers address-family callbacks, parses SPI/sequence values, looks up SAs, validates replay/expiry/mode, invokes protocol decrypt/authenticate input, removes encapsulation, and reinjects decapsulated packets.

Important APIs and types: Exported APIs include `xfrm_input_register_afinfo()`, `xfrm_input_unregister_afinfo()`, `secpath_set()`, `xfrm_parse_spi()`, `xfrm_input()`, `xfrm_input_resume()`, `xfrm_trans_queue_net()`, `xfrm_trans_queue()`, and `xfrm_input_init()`. Per-CPU `xfrm_trans_tasklet` queues transport reinjection work. `xfrm_input_afinfo[is_ipip][family]` stores callbacks under RCU.

Control flow: Normal input sets or copies secpath, parses AH/ESP/IPComp SPI and sequence, applies tunnel mark overrides, looks up state by mark/daddr/SPI/protocol/family, checks direction, updates skb mark, and records the state in secpath. It then validates state validity, encap type, replay, expiry, and tunnel mode under `x->lock`. Crypto is performed through `x->type->input()` or hardware offload `input_tail()`, with `-EINPROGRESS` resuming through `xfrm_input_resume()`. After replay advance and lifetime updates, mode-specific input removes transport/tunnel/BEET encapsulation or calls mode callbacks such as IP-TFS. Tunnel and GRO paths feed `gro_cells_receive()`, while transport mode calls AF `transport_finish()`.

State and persistence: Inbound packet state is recorded in skb secpath and XFRM skb control blocks. SA lifetime counters, `lastused`, replay windows, and integrity failure stats are updated. Per-CPU reinjection queues buffer packets temporarily.

Dependencies and integration: It depends on XFRM state lookup/replay/audit, AF protocol callbacks from IPv4/IPv6 code, GRO cells, offload metadata, `xfrm_inout.h`, netfilter conntrack reset, and mode callbacks.

Risks: This is a security boundary. Mistakes can bypass policy, accept replayed packets, leak device references on async paths, mishandle secpath depth, or reconstruct invalid inner headers. Encapsulation type matching is important for UDP/TCP ESP encapsulation correctness.

Test signals: Cover AH/ESP/IPComp, transport/tunnel/BEET/IP-TFS, IPv4/IPv6, UDP/TCP encapsulation, async crypto, hardware offload success/failure flags, replay failures, expired/acquire states, wrong direction, missing state audit, secpath max depth, GRO decap, and AF callback registration/unregistration.
