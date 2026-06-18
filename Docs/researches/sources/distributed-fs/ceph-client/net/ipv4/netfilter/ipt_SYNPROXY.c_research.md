# sources/distributed-fs/ceph-client/net/ipv4/netfilter/ipt_SYNPROXY.c

## Purpose
`ipt_SYNPROXY.c` implements the IPv4 legacy `SYNPROXY` target, intercepting TCP handshakes and using syncookies to protect back-end services from SYN floods.

## Important APIs, Types, And Functions
The target is `synproxy_tg4_reg`. Runtime logic is in `synproxy_tg4()`. Lifecycle validation is in `synproxy_tg4_check()` and `synproxy_tg4_destroy()`.

## Control Flow
The target validates the TCP checksum, parses TCP options, handles initial SYN packets by building and sending a SYNACK cookie, and handles pure ACK packets by validating the cookie and either stealing the skb or dropping it. Other packets continue through the rule set.

## State And Persistence
State is held in per-net synproxy structures and conntrack namespace references acquired during rule check and released at rule destruction. Per-rule settings are `struct xt_synproxy_info`.

## Dependencies And Integration Points
It depends on conntrack, `nf_synproxy`, TCP option parsing, syncookies, and IPv4 hooks for local-in and forward. Kconfig selects `NETFILTER_SYNPROXY` and `SYN_COOKIES`.

## Risks
Risks include conntrack reference leaks, accepting non-TCP rules, checksum parsing failures, option/cookie mismatch, statistics inaccuracies, and consuming or dropping skbs incorrectly.

## Test Signals
Test SYN, SYN+ACK-invalid, pure ACK cookie success/failure, bad checksum, malformed options, rule insertion/removal refcounts, namespace teardown, and forward/local-in hook behavior.
