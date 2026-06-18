# sources/distributed-fs/ceph-client/include/net/netfilter/nf_synproxy.h

Purpose: Defines shared SYN proxy per-net state, option parsing, cookie handling, and IPv4/IPv6 hook entry points for netfilter SYNPROXY.

Important APIs/types/functions: `synproxy_stats` tracks SYN/cookie/reopen counters; `synproxy_net` stores the template conntrack, per-cpu stats, and IPv4/IPv6 hook refcounts; `synproxy_options` stores MSS, window scale, timestamps, and option flags. APIs include `synproxy_pernet`, `synproxy_parse_options`, `synproxy_init_timestamp_cookie`, client SYNACK send/ACK receive helpers, IPv4/IPv6 hook functions, and family init/fini functions.

Control flow: Hook code intercepts SYNs, parses TCP options, encodes state into SYN cookies/timestamps, sends SYNACKs, validates client ACKs, and then opens/adjusts conntrack state using sequence adjustment.

State and persistence: Runtime per-net state includes a template conntrack, per-cpu stats, and hook refcounts. No on-disk persistence.

Dependencies/integration: Depends on TCP, IPv6 checksum/route helpers, conntrack synproxy extension, sequence adjustment, pernet generic storage, and optional IPv6.

Risks/test signals: Test malformed TCP options, timestamp cookie validation, retransmitted cookies, reopened connections, per-net hook refcounting, IPv6-disabled builds, and stats accuracy under concurrency.
