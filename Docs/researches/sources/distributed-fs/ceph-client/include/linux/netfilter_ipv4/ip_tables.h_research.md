# sources/distributed-fs/ceph-client/include/linux/netfilter_ipv4/ip_tables.h

Purpose: Declares IPv4 iptables wrappers around x_tables, including initial entry macros, table registration, packet evaluation, and compat entry layout.

Important APIs, types, and functions: Exports `ipt_register_table()`, `ipt_unregister_table_exit()`, `ipt_alloc_initial_table()`, `ipt_do_table()`, `struct ipt_standard`, `struct ipt_error`, init macros, and compat entry helpers. Detected source surface: 90 lines; includes `linux/if.h`, `linux/in.h`, `linux/init.h`, `linux/ip.h`, `linux/skbuff.h`, `net/compat.h`, `uapi/linux/netfilter_ipv4/ip_tables.h`; macros `IPT_ENTRY_INIT`, `IPT_ERROR_INIT`, `IPT_STANDARD_INIT`, `_IPTABLES_H`; structs `compat_ipt_entry`, `compat_xt_counters`, `ipt_entry`, `ipt_error`, `ipt_ip`, `ipt_standard`, `sk_buff`, `xt_error_target`, `xt_standard_target`; enums none; typedefs none; function-like declarations/helpers `compat_ipt_get_target`, `ipt_do_table`, `ipt_register_table`, `ipt_unregister_table_exit`.

Control flow: IPv4 hook ops call `ipt_do_table()` with hook state and table private data. Control-plane code allocates and registers xt_table-backed IPv4 tables.

State and persistence behavior: Per-net IPv4 table state is owned by x_tables; this header fixes IPv4 entry and compat layouts.

Dependencies and integration points: Depends on IPv4, skb, UAPI ip_tables, x_tables, and compat support.

Risks and test signals: Risks are entry offset mistakes, verdict encoding errors, and compat target alignment issues. Test filter/nat/mangle table traversal, rule replacement, and 32-bit iptables userspace.
