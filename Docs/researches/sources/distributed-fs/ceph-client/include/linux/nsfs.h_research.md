
# sources/distributed-fs/ceph-client/include/linux/nsfs.h

Purpose: declares the namespace filesystem helper API for obtaining namespace paths/names, matching namespace device/inode pairs, and managing active namespace references held by nsproxies.

Important APIs/types/functions: `ns_get_path()`, `ns_get_path_cb()`, `ns_match()`, `ns_get_name()`, and `nsfs_init()` implement nsfs lookup and naming. `__current_namespace_from_type()` and `current_in_namespace()` use `_Generic` to compare concrete namespace pointers against current task namespace state. `nsproxy_ns_active_get()` and `nsproxy_ns_active_put()` adjust active references for every namespace in an nsproxy.

Control flow: procfs and callers ask nsfs for a `struct path` to a task namespace or to a namespace returned by a callback. Matching compares `dev_t`/inode pairs for namespace file handles. Current-namespace checks map a concrete namespace type to `current->nsproxy`, `task_active_pid_ns(current)`, or `current_user_ns()`.

State and persistence: nsfs keeps namespace dentries and active references while files, bind mounts, or nsproxies pin namespaces. The header itself stores no state but exposes operations that affect namespace visibility.

Dependencies and integration points: depends on `ns_common.h`, credentials, PID namespaces, task structs, paths, proc namespace operations, and current task macros. It integrates `/proc/<pid>/ns`, namespace file descriptors, VFS path handling, and namespace active-reference accounting.

Risks and test signals: risks include stale task namespace pointers, mishandled callback references in `ns_get_path_cb()`, namespace dev/inode collisions after recycling, and missing active ref drops during nsproxy teardown. Test signals include proc namespace symlink/open tests, bind-mounted namespace lifetime tests, `current_in_namespace()` compile coverage for every namespace type, and nsproxy active ref leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsfs.h -->
