
# sources/distributed-fs/ceph-client/include/linux/ns/ns_common_types.h

Purpose: centralizes common namespace type declarations and the shared `struct ns_common` layout used by cgroup, IPC, mount, network, PID, time, user, and UTS namespaces.

Important APIs/types/functions: `struct ns_common` stores namespace type, VFS stashed dentry, proc namespace operations, inode number, a main `refcount_t`, and a union containing namespace tree nodes or an RCU free head. `_Generic` macros map concrete namespace structures to their embedded `ns_common`, initial namespace object, initial inode, initial ID, proc operations, and `CLONE_NEW*` type. `FOR_EACH_NS_TYPE`, `CLONE_NS_ALL`, and `ns_common_type()` provide the canonical namespace type list.

Control flow: concrete namespace initializers and helpers use the `_Generic` macros to avoid open-coded switch statements. Consumers pass concrete namespace pointers and the macros derive common metadata, while `ns_common` itself becomes the common object for nsfs, proc, namespace trees, and lifetime management.

State and persistence: the header documents a two-tier lifetime model: `__ns_ref` controls memory lifetime and tree pinning, while `__ns_ref_active` controls user-visible active state. Initial namespaces remain active forever; non-initial namespaces can move from active to inactive and, in some cases, back to active before final destruction.

Dependencies and integration points: depends on atomic/refcount types, rbtree namespace tree types, UAPI clone flags and namespace inode/ID constants, and proc namespace operations. It integrates namespace core, nsfs, procfs, VFS dentries, and the newer namespace tree listing model.

Risks and test signals: risks include `_Generic` omissions when adding namespace types, mismatched init inode/ID constants, incorrect active-reference transitions that expose dead namespaces, and config-gated operations returning NULL unexpectedly. Test signals include namespace create/unshare/setns coverage for all `CLONE_NEW*` flags, nsfs list/open by handle tests, inactive namespace resurrection tests, and compile coverage with namespace configs disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ns/ns_common_types.h -->
