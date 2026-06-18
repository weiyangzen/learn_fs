# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_srh.c

Purpose: Implements the IPv6 xtables `srh` match for Segment Routing Header revision 0 and revision 1 fields.

Important APIs/types/functions: Uses `srh_mt6`, `srh1_mt6`, `srh_mt6_check`, `srh1_mt6_check`, `struct ip6t_srh`, `struct ip6t_srh1`, `struct ipv6_sr_hdr`, `NF_SRH_INVF`, and `ipv6_masked_addr_cmp`.

Control flow: Both revisions locate a routing header, read and length-check it, require SRH type 4, and reject inconsistent `segments_left > first_segment`. Revision 0 matches next header, header length comparisons, segments-left comparisons, last-entry comparisons, and tag. Revision 1 repeats those and adds previous SID, next SID, and last SID masked-address matching with offset calculations based on `segments_left` and `first_segment`. Checkentry rejects unknown match and inversion flags.

State and persistence: Stateless beyond per-rule match data.

Dependencies/integration: Depends on IPv6 segment-routing definitions and xtables revisioned match registration.

Risks and test signals: Risks include SID offset arithmetic, insufficient validation that requested SID slots fit within `hdrlen`, inversion macro readability, and draft-field naming (`first_segment` as last-entry). Tests should cover revision negotiation, malformed/truncated SRH, non-type-4 routing headers, invalid `segments_left`, each comparison operator and inversion, masked SID matching, and boundary values at first/last segment.
