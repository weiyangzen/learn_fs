# sources/distributed-fs/ceph-client/include/net/gre.h

Purpose: declares Generic Routing Encapsulation header formats, protocol registration, parsing, device helpers, and inline transmit header construction.

Important APIs/types: `gre_base_hdr` contains flags and encapsulated protocol; `gre_full_hdr` adds checksum/reserved/key/sequence fields. `struct gre_protocol` supplies receive and error handlers. `gre_add_protocol()` and `gre_del_protocol()` register handlers by GRE version. Device helpers detect `gretap` and `ip6gretap`, while `gretap_fb_dev_create()` creates a fallback device. `gre_parse_header()` extracts tunnel packet info. Inline helpers map between IP tunnel flags and GRE flags, calculate header length, and build an skb GRE header.

Control flow and state: transmit code computes optional fields from tunnel flags, pushes the header, sets inner protocol and transport header, writes optional sequence/key/checksum from the end backward, and configures checksum offload if needed. Protocol handler state is registered externally.

Dependencies and integration: depends on skbuffs and `ip_tunnels.h`; integrates with IP tunnel devices, GSO types `SKB_GSO_GRE*`, checksum offload, rtnetlink, and receive protocol dispatch.

Risks: optional-field ordering and header length must match flags exactly. Checksum behavior differs for GSO GRE checksum and CHECKSUM_PARTIAL. Tests should cover all flag combinations, checksum and no-checksum GRE, key/sequence parsing, gretap device kind, malformed short headers, and tunnel offload metadata.
