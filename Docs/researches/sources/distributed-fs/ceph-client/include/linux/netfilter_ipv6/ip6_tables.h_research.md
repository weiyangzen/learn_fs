# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv6/ip6_tables.h

Purpose: Declares IPv6 iptables wrappers around x_tables.

Important APIs, types, and functions: Exports `ip6t_alloc_initial_table()`, `ip6t_register_table()`, `ip6t_unregister_table_exit()`, `ip6t_do_table()`, and compat IPv6 entry helpers. Detected source surface: 54 lines; includes `linux/if.h`, `linux/in6.h`, `linux/init.h`, `linux/ipv6.h`, `linux/skbuff.h`, `net/compat.h`, `uapi/linux/netfilter_ipv6/ip6_tables.h`; macros `_IP6_TABLES_H`; structs `compat_ip6t_entry`, `compat_xt_counters`, `ip6t_ip6`; enums none; typedefs none; function-like declarations/helpers `compat_ip6t_get_target`, `ip6t_do_table`, `ip6t_register_table`, `ip6t_unregister_table_exit`.

Control flow: IPv6 netfilter hooks invoke `ip6t_do_table()` to evaluate table entries, while control-plane code registers xt_table-backed IPv6 tables.

State and persistence behavior: Per-net table state and counters are managed by x_tables; this header fixes IPv6 entry layout and compat conversion.

Dependencies and integration points: Depends on IPv6 headers, skb, UAPI ip6_tables, x_tables, and compat support.

Risks and test signals: Risks are IPv6 address/mask layout errors, compat offsets, and hook-mask mismatches. Test ip6tables rule load, extension-header matches, concurrent replacement, and 32-bit compatibility.
