
# sources/distributed-fs/ceph-client/include/linux/ns_common.h

Purpose: provides namespace common lifecycle helpers, initializers, reference accessors, active-reference operations, and init namespace guards around `struct ns_common`.

Important APIs/types/functions: `__ns_common_init()`, `__ns_common_free()`, `ns_owner()`, and `may_see_all_namespaces()` are external namespace-core operations. `NS_COMMON_INIT`, `ns_common_init()`, and `ns_common_init_inum()` initialize embedded common fields. `ns_ref_read()`, `ns_ref_inc()`, `ns_ref_get()`, `ns_ref_put()`, `ns_ref_put_and_lock()`, `ns_ref_active_get()`, `ns_ref_active_put()`, and `ns_get_unless_inactive()` wrap the two-tier reference model. `is_ns_init_inum()` and `is_ns_init_id()` special-case immortal boot namespaces.

Control flow: new namespaces call `ns_common_init*()` to assign type, operations, inode, IDs, refs, and list heads. Users acquire main refs before holding a namespace internally, acquire active refs when making it visible or task/file-backed, and drop active refs before final main refs. `ns_get_unless_inactive()` gates reopening/listing paths so inactive namespaces are not exposed.

State and persistence: all state is in-memory namespace lifetime state. Initial namespace refs stay at one and are validated by warnings rather than modified; non-initial namespaces transition through active, inactive, and destroyed states according to main and active refcounts.

Dependencies and integration points: depends on `ns_common_types.h`, refcounts, VFS warning helpers, sched/nsfs UAPI constants, spinlocks, and namespace tree fields. It integrates nsfs, proc namespace operations, task namespace switching, and owner namespace lookup.

Risks and test signals: risks include leaking active references, decrementing initial namespace refs, reopening an inactive namespace, freeing while active refs remain, and confusing main refs with active visibility refs. Test signals include KASAN/refcount debug namespace lifecycle tests, setns/open file descriptor lifetime checks, pid/user namespace delayed cleanup, and namespace tree visibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns_common.h -->
