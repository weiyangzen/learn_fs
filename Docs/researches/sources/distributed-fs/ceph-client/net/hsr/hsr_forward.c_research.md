<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_forward.c

## Purpose
Implements HSR/PRP frame classification, tag/trailer creation and removal, duplicate-aware forwarding, RedBox forwarding policies, and local delivery.

## APIs, Types, and Functions
Exports `hsr_forward_skb()`, `hsr_create_tagged_frame()`, `prp_create_tagged_frame()`, `hsr_get_untagged_frame()`, `prp_get_untagged_frame()`, `hsr_drop_frame()`, `prp_drop_frame()`, `hsr_fill_frame_info()`, and `prp_fill_frame_info()`. Key helpers include `is_supervision_frame()`, `is_proxy_supervision_frame()`, `create_stripped_skb_hsr()`, `prp_fill_rct()`, `hsr_fill_tag()`, `hsr_deliver_master()`, `hsr_xmit()`, `hsr_forward_do()`, `check_local_dest()`, `handle_std_frame()`, and `fill_frame_info()`.

## Control Flow, State, and Persistence
`hsr_forward_skb()` fills a transient `hsr_frame_info`, registers ingress time, forwards to eligible ports, updates master/interlink TX stats, and frees all held skb variants. Classification detects supervision frames, proxy supervision, node source, VLAN encapsulation, HSR tags, PRP trailers, standard frames, local destination, and SAN origin. Forwarding iterates all ports except the receive port, skips inappropriate local/nonlocal destinations, respects hardware duplicate generation, registers outgoing duplicates, handles supervision frames locally, applies protocol-specific drop rules, creates tagged frames for slaves and untagged frames for master/interlink, then either injects locally via `netif_rx()` or transmits with `dev_queue_xmit()`. State mutations occur in skb clones, port/device stats, sequence numbers for standard master/interlink frames, and node duplicate records via `hsr_framereg.c`.

## Dependencies and Integration
Depends on HSR header layouts, PRP RCT helpers, VLAN parsing, skb cloning/copying, hardware offload feature flags, node database helpers, address substitution helpers, and protocol ops installed by `hsr_device.c`.

## Risks and Test Signals
Risks include malformed skb header lengths, checksum offset adjustments when adding/removing HSR tags, PRP trailer size validation, forwarding loops if duplicate registration fails open, RedBox drop policy mistakes, and interactions with hardware HSR tag/duplicate offloads. Test signals include supervision frame validation, HSR v0/v1 tag handling, PRP RCT creation/removal, VLAN frames, local unicast/multicast delivery, duplicate discard, SAN frames, RedBox proxy rules, offloaded forwarding, and malformed frame drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_forward.c -->
