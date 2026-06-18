# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tproxy.h

Purpose: Declares transparent proxy socket selection, assignment, and TIME_WAIT handling helpers for IPv4 and IPv6 interception.

Important APIs/types/functions: `enum nf_tproxy_lookup_t`, `nf_tproxy_sk_is_transparent`, `nf_tproxy_twsk_deschedule_put`, `nf_tproxy_assign_sock`, `nf_tproxy_laddr4`, `nf_tproxy_handle_time_wait4`, `nf_tproxy_get_sock_v4`, `nf_tproxy_laddr6`, `nf_tproxy_handle_time_wait6`, and `nf_tproxy_get_sock_v6`.

Control flow: TPROXY rules search for established or listener sockets using packet and redirect tuples. Transparent sockets are retained; non-transparent sockets are dropped with `sock_gen_put`. TIME_WAIT sockets may be replaced by listener sockets for new SYNs. Once selected, `nf_tproxy_assign_sock` orphans the skb and installs the socket with `sock_edemux`.

State and persistence: Uses existing socket/timewait state and consumes socket references. No independent persistent state.

Dependencies/integration: Depends on TCP/UDP sockets, inet transparency flags, skbuff ownership, bottom-half safe timewait descheduling, IPv4/IPv6 address handling, and nft/xt tproxy rules.

Risks/test signals: Reference ownership is the main risk. Test established vs listener preference, TIME_WAIT SYN reopen, non-transparent listeners, wildcard binds, IPv6, local-address override, skb destructor behavior, and l3mdev/namespace scoping.
