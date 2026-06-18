# sources/distributed-fs/ceph-client/include/net/erspan.h

Read `sources/distributed-fs/ceph-client/include/net/erspan.h` completely for this pass (321 lines, 9251 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/erspan.h_research.md`.

Purpose: implements ERSPAN header constants and inline builders for GRE-encapsulated mirrored packets, covering Type II/version 1 and Type III/version 2 ERSPAN metadata.

Important APIs/types/functions: constants define ERSPAN versions, masks for VLAN/COS/encapsulation/session/index and v2 SGT/P/FT/HWID/DIR/GRA/O fields, metadata sizes, and offsets. `enum erspan_encap_type` describes original encapsulation. `struct erspan_base_hdr` is bitfield-packed for endian-specific base header layout. Helpers include `set_session_id()`, `get_session_id()`, `set_vlan()`, `get_vlan()`, `set_hwid()`, `get_hwid()`, `erspan_hdr_len()`, `tos_to_cos()`, `erspan_build_header()`, `erspan_get_timestamp()`, `enum erspan_bso`, `erspan_detect_bso()`, and `erspan_build_header_v2()`.

Control flow: tunnel/mirroring transmit code reserves and pushes ERSPAN metadata before the mirrored Ethernet frame. Version 1 builder derives COS from outer IP TOS/traffic class, detects 802.1Q in-frame VLAN preservation, sets session ID and truncation bit, and writes the 20-bit index. Version 2 builder similarly sets base fields, detects short/oversized BSO, writes timestamp in 100-usec granularity, SGT/P/FT/direction/granularity/O fields, and HWID. Header length helper tells GRE/tunnel code how much metadata follows.

State and persistence: no stored state. Builders mutate skb headroom in-place and encode current wall-clock timestamp for v2 metadata. Session ID, index, direction, hwid, and truncation are caller-provided.

Dependencies and integration points: depends on IP/IPv6/skbuff helpers, Ethernet/VLAN header layout, ktime, byteorder bitfields, and UAPI `linux/erspan.h` for `struct erspan_md2`. Integrates with GRE/ERSPAN tunnel devices, TC mirred/sample, and packet capture/monitoring systems.

Risks: bitfield layout is endian-sensitive. Builders assume enough skb headroom and that `skb->data` points at the mirrored Ethernet frame before push. Version 1 and 2 metadata sizes differ. VLAN detection only checks 802.1Q EtherType at the expected position. Timestamp wraps in about four days. BSO cannot detect bad FCS/alignment because FCS is absent from skb data.

Test signals: packet capture decode for ERSPAN v1/v2, endian build checks, VLAN and non-VLAN mirrored frames, IPv4/IPv6 COS derivation, session/VLAN/HWID round trips, truncation and direction bits, short/oversized BSO classification, timestamp granularity/wrap behavior, and skb headroom failure tests in tunnel code.
