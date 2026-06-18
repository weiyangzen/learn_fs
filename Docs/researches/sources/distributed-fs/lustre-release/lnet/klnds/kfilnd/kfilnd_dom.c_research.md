<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c_research.md`.

Purpose: shares and reference-counts kfabric fabrics and domains across kfilnd devices so multiple LNet NIs can reuse provider resources when compatible.

Important APIs/types/functions: global `fab_list` with `fab_list_lock`; `struct kfilnd_fab` and `struct kfilnd_dom` krefs; helpers `kfilnd_fab_alloc/free/reuse()`, `kfilnd_dom_alloc/free/reuse()`, public `kfilnd_dom_get()` and `kfilnd_dom_put()`.

Control flow: `kfilnd_dom_get()` builds KFI hints from NI tunables, probes dynamic resource allocation support, tries to reuse an existing fabric/domain by constraining hints and calling `kfi_getinfo()`, gets final provider info, allocates missing fabric/domain, enables CXI dynamic resource allocation when possible, and returns both domain and provider info. `kfilnd_dom_put()` drops the domain and its fabric ref; free callbacks unlink lists and close KFI FIDs.

State and persistence behavior: fabrics persist on the global list while referenced; each fabric has a domain list. Domains persist while devices reference them. Returned `kfi_info` is caller-owned and freed by device allocation.

Dependencies and integration: depends on kfabric `kfi_getinfo`, fabric/domain creation, CXI fabric ops, NI tunables for provider version/auth/traffic class, LNet CPT counts, and kref/list locking.

Risks: `kfilnd_dom_reuse()` is called with `fab` even when `kfilnd_fab_reuse()` returns NULL; the helper checks NULL, but hints restoration is fragile. Auth-key pointers are deliberately nulled before freeing hints to avoid freeing NI-owned memory. Dynamic resource probing opens a temporary fabric and must release refs correctly. Reuse logic depends on provider `kfi_getinfo()` behavior.

Test signals: create multiple NIs on same and different fabrics, verify fabric/domain refcounts and reuse, test provider versions/traffic classes/auth keys, simulate `kfi_getinfo` and domain allocation failures, and unload after repeated startup/shutdown cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_dom.c -->
