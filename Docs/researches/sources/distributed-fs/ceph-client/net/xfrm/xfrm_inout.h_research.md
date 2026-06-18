# sources/distributed-fs/ceph-client/net/xfrm/xfrm_inout.h

Purpose: `xfrm_inout.h` contains shared inline helpers for saving inner IP header metadata before encapsulation/decapsulation and rebuilding BEET-mode headers afterward.

Important APIs: `xfrm4_extract_header()` stores IPv4 header length, ID, fragment offset, TOS, TTL, options length, and clears IPv6 flow label state in `XFRM_MODE_SKB_CB`. `xfrm6_extract_header()` stores IPv6 header length, synthesized DF state, DS field, hop limit, and flow label. `xfrm6_beet_make_header()` and `xfrm4_beet_make_header()` rebuild minimal IPv6/IPv4 BEET outer/inner headers from saved control-block values.

Control flow and integration: Output path calls extract helpers before moving headers for tunnel/BEET encapsulation. Input path uses saved metadata while removing encapsulation and restoring inner headers. BEET helpers are called by both `xfrm_input.c` and `xfrm_output.c`.

State and persistence: The helpers persist metadata only within `skb->cb` for the lifetime of a packet as it moves through XFRM mode processing.

Dependencies: They depend on IPv4/IPv6 header structures, DS field helpers, and `XFRM_MODE_SKB_CB`. IPv6 extraction is compiled conditionally and warns if called without IPv6 support.

Risks: `skb->cb` ownership is fragile; callers must not overwrite XFRM mode fields between extract and rebuild. Incorrect optlen or flow-label handling can break BEET interoperability. IPv6-disabled builds rely on WARN paths to catch invalid calls.

Test signals: Validate IPv4/IPv6 transport, tunnel, and BEET SAs; include IPv4 options, fragmentation fields, DSCP/ECN, TTL/hop-limit, and IPv6 flow labels. Use packet captures to ensure reconstructed headers preserve expected fields.
