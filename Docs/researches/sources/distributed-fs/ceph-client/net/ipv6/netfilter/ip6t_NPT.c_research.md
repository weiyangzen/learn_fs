# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_NPT.c

Purpose: Implements stateless IPv6 Network Prefix Translation targets `SNPT` and `DNPT` for the mangle table.

Important APIs/types/functions: Uses `struct ip6t_npt_tginfo`, `ip6t_npt_checkentry`, `ip6t_npt_map_pfx`, `icmpv6_bounced_ipv6hdr`, target callbacks `ip6t_snpt_tg` and `ip6t_dnpt_tg`, and an `xt_target` array.

Control flow: Checkentry rejects prefixes longer than /64 and prefixes with nonzero host bits, then precomputes a checksum adjustment. The target rewrites source or destination prefix bits, applies checksum-neutral adjustment into a suitable 16-bit word, sends ICMPv6 parameter problem and drops if all candidate words are unusable, and also rewrites embedded IPv6 headers in bounced ICMPv6 errors when they reference the translated source prefix.

State and persistence: Per-rule target info stores prefixes, lengths, and computed adjustment. No global runtime state.

Dependencies/integration: Registers with xtables for `NFPROTO_IPV6`, table `mangle`, and hooks appropriate to source or destination prefix translation. Uses IPv6 address helpers and ICMPv6 error emission.

Risks and test signals: Risks include checksum-neutrality mistakes, ICMPv6 embedded-header rewrite only affecting local copies when not writable, and prefix validation edge cases. Tests should cover /0-/64 mappings, mangle hook restrictions, all-zero/mangled checksum words, ICMPv6 error translation, and round-trip SNPT/DNPT checksum stability.
