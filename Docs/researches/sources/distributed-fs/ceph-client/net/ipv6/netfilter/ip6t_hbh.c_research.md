# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_hbh.c

Purpose: Implements IPv6 xtables `hbh` and `dst` matches for Hop-by-Hop and Destination Options headers.

Important APIs/types/functions: Shared callback `hbh_mt6`, validator `hbh_mt6_check`, `struct ip6t_opts`, `ipv6_find_hdr`, `ipv6_optlen`, and two `xt_match` registrations. `MODULE_ALIAS("ip6t_dst")` supports destination-options autoload.

Control flow: Runtime chooses Hop-by-Hop or Destination header based on which registration invoked the match, locates the header, verifies length, optionally matches exact header length, and if requested walks options strictly by type and length. Pad1 is handled as a one-byte option; other options use length+2. Non-strict matching is explicitly unsupported and rejected.

State and persistence: Stateless beyond per-rule option sequence and flags.

Dependencies/integration: Depends on IPv6 extension-header parser and xtables match ABI. The implementation relies on `hbh_mt6_reg` array order.

Risks and test signals: Risks are strict option walk bounds, reliance on registration array order, and unsupported non-strict flags. Tests should cover hbh/dst selection, zero-length or truncated options, Pad1/PadN, wildcard option lengths, length inversion, and checkentry rejection for non-strict/unknown flags.
