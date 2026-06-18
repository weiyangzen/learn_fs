# sources/distributed-fs/ceph-client/security/apparmor/label.c

Purpose: implements AppArmor labels: canonical ordered profile sets, labelset insertion/replacement, stale-label update, proxy redirection, label parsing, label matching, and label name/audit rendering.

Important APIs/functions: proxy lifecycle (`aa_alloc_proxy()`, `__aa_proxy_redirect()`), vector canonicalization (`aa_vec_unique()`), label lifecycle (`aa_label_init()`, `aa_label_alloc()`, `aa_label_destroy()`, `aa_label_kref()`), set operations (`aa_label_insert()`, `aa_label_remove()`, `aa_label_replace()`), subset/merge operations (`aa_label_is_subset()`, `aa_label_merge()`), policy matching (`aa_label_match()`), printing (`aa_label_snxprint()`, `aa_label_asxprint()`, `aa_label_xaudit()`), parsing (`aa_label_strn_parse()`), and stale refresh (`__aa_labelset_update_subtree()`).

Control flow: labels are sorted by namespace depth/name and profile hname, then interned in a namespace `aa_labelset` red-black tree. Replacement marks old labels stale, redirects their proxy to the new label, and later RCU frees unused labels. Compound label policy first tries a full `A//&B` DFA match, then per-component accumulation if needed.

State and persistence: labels hold profile refs, secids, optional cached names, proxies, tree nodes, flags, and mediates bitmasks. Proxies let tasks and objects follow policy replacement without immediate mutation.

Dependencies and integration: used by credentials, files, sockets, policy replacement, secid, audit, procattr, IPC, network, and mount mediation. Risks include lock ordering across namespace labelsets, proxy cycles, duplicate profile refs, stale component updates, hidden namespace rendering, and allocation failure during replacement. Test label parse/print round trips, stacking, namespace visibility, concurrent replacement under RCU, secid free, merge/subset behavior, and audit strings containing control characters.
