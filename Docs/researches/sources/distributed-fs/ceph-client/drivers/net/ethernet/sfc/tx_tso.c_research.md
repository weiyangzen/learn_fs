# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/tx_tso.c

Purpose: implements legacy SFC TSOv1 segmentation using firmware TSO option descriptors, predating the newer EF10 TSOv2 descriptor path.

Important types/functions: `struct tso_state` tracks output sequence/IP ID, packet space, current input DMA mapping, header offsets/lengths, and header DMA ownership. `efx_enqueue_skb_tso()` is the exported enqueue path. Helpers validate protocol, map headers/fragments, build TSO option descriptors, split payload into MSS-sized packets, and attach skb/DMA ownership to final descriptors.

Control flow: the path verifies TCP over IPv4/IPv6, maps the linear header area, starts the first output packet, then repeatedly fills packet payload from skb head or page frags. At each segment boundary it emits a TSO option descriptor and header descriptor using original headers plus updated sequence/IP ID values. The final payload descriptor owns the skb; the last header descriptor owns the header DMA unmap. Failure unmaps the active fragment and header mapping and returns an error so the caller can unwind descriptors.

State and dependencies: uses queue insert counters and NIC-specific `tx_limit_len()`, DMA mapping APIs, TCP/IP header helpers, and EF10 descriptor bit definitions. It has no persistent state beyond descriptors enqueued to the TX ring.

Risks and test signals: risks are header DMA ownership across multiple segments, fragment boundary handling, TCP flag masking on non-final segments, IPv4 ID progression, and queue overflow assumptions. Test IPv4/IPv6 GSO with payload in head and frags, boundary-crossing fragments, single-segment fallback avoidance, induced DMA failure, and comparison with software GSO packet counts.
