# sources/distributed-fs/ceph-client/include/linux/netfilter_arp/arp_tables.h

Purpose: Declares ARP-specific x_tables wrappers and initial table helpers for arptables.

Important APIs, types, and functions: Exports `struct arpt_standard`, `struct arpt_error`, initialization macros, table allocation/register/unregister/evaluation APIs, and compat ARP entry helpers. Detected source surface: 78 lines; includes `linux/if.h`, `linux/if_arp.h`, `linux/in.h`, `linux/skbuff.h`, `net/compat.h`, `uapi/linux/netfilter_arp/arp_tables.h`; macros `ARPT_ENTRY_INIT`, `ARPT_ERROR_INIT`, `ARPT_STANDARD_INIT`, `_ARPTABLES_H`; structs `arpt_arp`, `arpt_entry`, `arpt_error`, `arpt_standard`, `compat_arpt_entry`, `compat_xt_counters`, `xt_error_target`, `xt_standard_target`; enums none; typedefs none; function-like declarations/helpers `arpt_do_table`, `arpt_register_table`, `arpt_unregister_table`, `compat_arpt_get_target`.

Control flow: ARP packets enter `arpt_do_table()`, which evaluates x_tables entries with ARP-specific UAPI entry layout. Registration installs per-net ARP tables backed by xt_table data.

State and persistence behavior: Runtime table state is owned by x_tables per network namespace; this header contributes ARP initial entries and compat layout definitions.

Dependencies and integration points: Depends on interface, IP, ARP, skb, UAPI arptables, x_tables, and optional compat support.

Risks and test signals: Risks are wrong ARP entry sizing, target verdict encoding errors, and compat alignment drift. Test arptables rule load, error target fallback, packet match behavior, and 32-bit userspace compatibility.
