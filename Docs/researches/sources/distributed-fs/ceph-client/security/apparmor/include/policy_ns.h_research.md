# sources/distributed-fs/ceph-client/security/apparmor/include/policy_ns.h

Purpose: declares AppArmor policy namespaces, the containers that own profile visibility, per-namespace labels, raw policy data, apparmorfs dentries, and the namespace-local unconfined profile.

Important APIs/types: `struct aa_ns_acct` tracks maximum and current namespace policy size/count. `struct aa_ns` embeds `aa_policy`, parent linkage, `mutex lock`, accounting, `unconfined`, `sub_ns`, revision/wait state, `aa_labelset labels`, `rawdata_list`, and apparmorfs dentries. `MAX_NS_DEPTH`, `root_ns`, `kernel_t`, `ns_unconfined()`, `aa_ns_visible()`, `aa_ns_name()`, namespace lookup/create/remove helpers, and `aa_get_ns()`/`aa_put_ns()` are the main interface.

Control flow: callers prepare or find namespaces through `aa_prepare_ns()`/lookup helpers, then mutate policy under the namespace lock. Reference management is intentionally tied to the namespace's unconfined profile rather than an independent namespace kref.

State and persistence: namespace lifetime pins the unconfined profile; namespace revisions and wait queues signal policy changes; `rawdata_list` preserves loaded binary policy blobs when export is enabled. Dependencies include `apparmorfs`, `label`, and `policy`. Integration is broad: policy load/removal, label sets, secctx display, and LSM init all depend on the root namespace.

Risks and test signals: stale locks or unbalanced profile refs can leak whole namespaces. Visibility rules are security-sensitive for nested namespaces and user namespaces. Test by loading/removing nested namespaces, verifying apparmorfs entries, checking hidden namespace rendering, and exercising policy admin/view capability paths.
