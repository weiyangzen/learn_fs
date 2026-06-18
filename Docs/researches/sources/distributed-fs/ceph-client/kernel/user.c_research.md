<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user.c -->
# sources/distributed-fs/ceph-client/kernel/user.c

Purpose: defines the initial user namespace and manages `struct user_struct` objects used for per-UID resource accounting such as process counts, file counts, key quotas, ratelimits, and epoll watches.

Important APIs and state: `init_user_ns` is the root namespace with full uid/gid/projid maps. `root_user` is the initial user_struct. Public functions are `find_user()`, `alloc_uid()`, and `free_uid()`. Internal state includes `uid_cachep`, `uidhash_table`, and `uidhash_lock`. Optional `init_binfmt_misc` is exported for binfmt_misc.

Control flow: cache init creates the slab cache, initializes hash buckets, initializes root epoll counters, and inserts `root_user`. `alloc_uid()` first looks up under lock, allocates and initializes a new user if absent, then rechecks under lock before inserting to handle races. `free_uid()` decrements the refcount and frees under `uidhash_lock` when it reaches zero. `find_user()` returns an extra reference if found.

State and persistence: user_struct objects persist while referenced by credentials or resource users. Root namespace and root user are static. Epoll counters are allocated per user when configured.

Dependencies and integration: integrates with credentials, user namespaces, keyrings, binfmt_misc, epoll, ratelimit state, slab caches, and softirq-safe spin locking.

Risks: locking must be IRQ-safe because frees can happen with interrupts disabled or from softirq contexts. Allocation race handling must avoid duplicate user_structs. Test signals include concurrent `alloc_uid()` for the same UID, refcounted free, root_user lifetime, epoll counter allocation failure, and namespace root map correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/user.c -->
