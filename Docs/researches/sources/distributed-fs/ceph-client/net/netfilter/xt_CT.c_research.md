# sources/distributed-fs/ceph-client/net/netfilter/xt_CT.c

Purpose: `CT` and `NOTRACK` raw-table targets attach conntrack templates or mark packets untracked before normal conntrack handling.

Important APIs/types/functions: `xt_ct_target()`, `notrack_tg()`, `xt_ct_tg_check()`, helper/timeout setup helpers, revision check wrappers, and `xt_ct_tg_destroy()`.

Control flow: check validates flags, obtains conntrack unless NOTRACK, builds zone metadata, allocates a template, adds optional event cache, helper, and timeout extensions, marks it confirmed, and stores the kernel pointer outside usersize. Runtime skips already tracked skbs, attaches a template with refcount increment or sets untracked state.

State and persistence: per-rule `nf_conn` template, optional helper module reference, timeout policy, and conntrack netns ref. Dependencies include raw table, nf_conntrack templates/zones/helpers/timeouts/ecache, and queue drop on helper/timeout removal. Risks: complex unwind, helper requires explicit non-inverted L4 proto, config-dependent zones, and queued packets after destroy. Test signals: revisions 0/1/2, NOTRACK, helper/timeout strings, zones, existing `_nfct`, failure unwind, and destroy release.
