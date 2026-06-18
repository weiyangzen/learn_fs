# sources/distributed-fs/ceph-client/net/netfilter/xt_SECMARK.c

Purpose: `SECMARK` target writes LSM security identifiers to `skb->secmark`.

Important APIs/types/functions: global `mode`, `checkentry_lsm()`, `secmark_tg_check()`, `secmark_tg()`, revision wrappers, and security hooks `security_secctx_to_secid()`/`security_secmark_relabel_packet()`.

Control flow: check restricts use to mangle/security tables, prevents mixing modes, maps secctx to secid, verifies relabel permission, increments LSM secmark refcount, and stores secid. Runtime writes secmark and continues. Destroy decrements refcount.

State and persistence: global mode and per-rule secid/refcount. Dependencies include x_tables, Linux security subsystem, LSM policy, and skb secmark. Risks: global mode mixing, invalid/unterminated contexts, relabel denial, refcount symmetry, and v0/v1 ABI differences. Test signals: valid/invalid context, permission denied, table enforcement, mode mixing, skb assignment, revision usersize, and destroy decrement.
