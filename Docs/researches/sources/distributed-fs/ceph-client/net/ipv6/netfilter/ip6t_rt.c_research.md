# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_rt.c

Purpose: Implements the IPv6 xtables `rt` match for Routing Header fields and type-0 address lists.

Important APIs/types/functions: Uses `rt_mt6`, `rt_mt6_check`, `segsleft_match`, `struct ip6t_rt`, `ipv6_find_hdr`, `ipv6_optlen`, `skb_header_pointer`, and `struct rt0_hdr`.

Control flow: Runtime locates a routing header, validates full length, matches segments-left range, optional header length and routing type, optional reserved field zero for type 0, and optionally address lists. Address list matching supports strict full-list equality or non-strict subsequence matching depending on flags. Checkentry rejects unknown inversion flags, too many addresses, and type-0-only options unless an uninverted `--rt-type 0` is present.

State and persistence: Stateless.

Dependencies/integration: xtables IPv6 extension-header parsing and legacy ip6tables routing-header ABI.

Risks and test signals: Risks are deprecated type-0 semantics, address-list bounds, and correct hotdrop on truncated skbs. Tests should cover no routing header, malformed length, segleft range/inversion, type mismatch, reserved field checks, strict/non-strict address lists, and checkentry type-0 constraints.
