<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nscommon.c -->
# sources/distributed-fs/ceph-client/kernel/nscommon.c

Purpose: Provides common namespace object initialization, inode allocation/freeing, owner discovery, active-reference propagation, and a helper that decides whether the current task may see all namespaces.

Important APIs/types/functions: `__ns_common_init()`, `__ns_common_free()`, `ns_owner()`, `__ns_ref_active_put()`, `__ns_ref_active_get()`, and `may_see_all_namespaces()`. The core type is `struct ns_common`, including refcounts, namespace id/type, proc operations, stashed file state, and namespace tree nodes.

Control flow: initialization sets the normal refcount to one, initializes the namespace tree nodes and owner root, validates the proc operations under `CONFIG_DEBUG_VFS`, allocates a proc inode unless one is supplied, and marks initial namespaces active. `ns_owner()` asks the namespace's `proc_ns_operations.owner()` hook for the owning user namespace, ignoring `init_user_ns` as always active. Active put decrements the namespace, and if it reaches zero, walks upward through owning user namespaces dropping one active reference per owner until it reaches an active owner or no owner. Active get increments the namespace and, only when resurrecting from zero, walks upward adding owner references until it reaches an already-active owner.

State and persistence: State is purely kernel memory: proc inode numbers, `__ns_ref`, `__ns_ref_active`, namespace tree nodes, and owner roots. Active references form a cascading ownership graph rooted at init namespaces, which are never deactivated.

Dependencies/integration: Integrates with proc namespace operations, namespace tree helpers, user namespaces, PID namespace access checks, and VFS debug warnings. `may_see_all_namespaces()` ties global visibility to being in `init_pid_ns` with `CAP_SYS_ADMIN` in `init_pid_ns.user_ns`.

Risks: The active-reference cascade is subtle; missed owner references can make namespaces invisible or prematurely inactive, while extra references leak active namespace trees. `ns_owner()` depends on every namespace type supplying correct `owner()` operations. Initial namespace identity checks must remain aligned with namespace id/inode initialization.

Test signals: Namespace creation/destruction across nested user namespaces, resurrection from inactive namespace references such as proc namespace files or sockets, active refcount underflow warnings, debug validation of namespace operation tables, and visibility checks for root namespace administrators versus contained namespace tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/nscommon.c -->
