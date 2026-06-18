# sources/distributed-fs/ceph-client/net/netfilter/xt_CONNSECMARK.c

Purpose: `CONNSECMARK` target copies security marks between packets and conntrack entries.

Important APIs/types/functions: `secmark_save()`, `secmark_restore()`, `connsecmark_tg()`, `connsecmark_tg_check()`, `connsecmark_tg_destroy()`, and `nf_conntrack_event_cache()`.

Control flow: check restricts rules to mangle/security tables, validates SAVE/RESTORE mode, and obtains conntrack netns support. Runtime saves packet secmark to an unmarked conntrack or restores conntrack secmark to an unmarked packet, then continues.

State and persistence: connection secmark persists in `nf_conn`; rules hold conntrack netns references. Dependencies include nf_conntrack, conntrack event cache, x_tables, and LSM secmark users. Risks: no conntrack means no effect, save/restore do not overwrite existing marks, and netns ref symmetry is required. Test signals: save/restore with and without conntrack, event emission, invalid table/mode, IPv4/IPv6 lifetime, and destroy cleanup.
