<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname.c -->
# sources/distributed-fs/ceph-client/kernel/utsname.c

Purpose: manages UTS namespaces, which isolate hostname and domainname values. It supports cloning, reference management, namespace install, ownership, and initialization.

Important APIs and state: `copy_utsname()` clones or references an existing namespace based on `CLONE_NEWUTS`. `free_uts_ns()` releases namespace resources. `utsns_operations` implements proc namespace get/put/install/owner. `uts_ns_init()` creates the slab cache and registers `init_uts_ns` with the namespace tree.

Control flow: cloning charges `UCOUNT_UTS_NAMESPACES` against the target user namespace and current euid, allocates a namespace, initializes ns_common, copies the old uts name under `uts_sem`, takes a user namespace reference, and inserts into nstree. Copying without `CLONE_NEWUTS` just takes a reference. Installation requires CAP_SYS_ADMIN in both the target UTS namespace owner and the caller credential namespace, then swaps `nsproxy->uts_ns`.

State and persistence: each UTS namespace stores copied `struct new_utsname`, user namespace owner, ucounts reference, and ns_common. Freeing removes it from nstree, decrements ucounts, drops user_ns, and RCU-frees after ns common cleanup.

Dependencies and integration: depends on ucounts, user namespaces, nsproxy, proc_ns, uts_sem, slab usercopy cache, and nstree.

Risks: namespace limits and references must unwind on clone failures. Installing across namespaces is capability-sensitive. Test signals include CLONE_NEWUTS hostname isolation, ucount exhaustion, setns permission checks, concurrent reads while cloning, and namespace tree traversal during free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/utsname.c -->
