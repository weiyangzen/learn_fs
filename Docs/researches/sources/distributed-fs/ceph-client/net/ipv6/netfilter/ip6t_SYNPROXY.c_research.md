# sources/distributed-fs/ceph-client/net/ipv6/netfilter/ip6t_SYNPROXY.c

Purpose: Implements IPv6 xtables `SYNPROXY`, intercepting TCP handshakes with syncookies before allowing backend connection tracking.

Important APIs/types/functions: Uses `synproxy_tg6`, `synproxy_tg6_check`, `synproxy_tg6_destroy`, `struct xt_synproxy_info`, `synproxy_parse_options`, `synproxy_send_client_synack_ipv6`, `synproxy_recv_client_ack_ipv6`, conntrack namespace refs, and `nf_synproxy_ipv6_init/fini`.

Control flow: Runtime validates IPv6 TCP checksum, reads the TCP header at `par->thoff`, parses options, and handles pure SYN and pure ACK. Initial SYNs update stats, mask negotiated options by rule config, initialize timestamp cookies if enabled, send SYN+ACK, consume the skb, and return `NF_STOLEN`. Valid ACKs complete cookie validation similarly; invalid ACKs drop. Other packets continue. Checkentry requires an explicit non-inverted TCP match, acquires conntrack namespace support, and initializes IPv6 synproxy state; destroy reverses both.

State and persistence: Per-net synproxy state and conntrack references persist while matching rules are installed; per-CPU stats are updated.

Dependencies/integration: Depends on `NF_CONNTRACK`, `NETFILTER_SYNPROXY`, syncookies, xtables, and IPv6 TCP checksum helpers.

Risks and test signals: Risks include leaked conntrack refs on check failure, wrong handling of non-linear TCP headers, option negotiation errors, and unexpected `NF_STOLEN` ownership. Tests should cover invalid checksum/header/options, TCP-only rule validation, module unload with active rules, SYN/ACK handshakes with timestamp and no timestamp modes, and forward/local-in hook behavior.
