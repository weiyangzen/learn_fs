# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_REJECT.c

Purpose: Provides the IPv6 `REJECT` xtables target for filter/NFT compatibility, sending ICMPv6 errors or TCP resets before dropping packets.

Important APIs/types/functions: Target callback `reject_tg6`, validator `reject_tg6_check`, `struct ip6t_reject_info`, `nf_send_unreach6`, `nf_send_reset6`, and `xt_target reject_tg6_reg`.

Control flow: Runtime switches on `reject->with`, emits the requested ICMPv6 unreachable/policy/reject-route error or TCP reset using current hook and socket context, then always returns `NF_DROP`. Checkentry rejects unsupported `ECHOREPLY` and enforces that `TCP_RESET` rules explicitly match non-inverted TCP.

State and persistence: Stateless beyond per-rule reject mode.

Dependencies/integration: Depends on `NF_REJECT_IPV6`, xtables table `filter`, hooks local-in/forward/local-out, and protocol constraints from ip6tables.

Risks and test signals: Risks are generating illegal reset/error packets from wrong hooks or malformed TCP rules. Tests should verify checkentry failures, each reject mode on input/forward/output, rate-limited logs, and no response for unsupported echo reply.
