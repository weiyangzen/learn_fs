## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_permissions_test.c

**Purpose:** Permission model coverage for `listns`, especially user-namespace scoping, `CAP_SYS_ADMIN`, current-user filtering, sibling isolation, and capability dropping.

**Important APIs and flow:** Tests create user namespaces with `setup_userns()`, create owned net/UTS/IPC namespaces with `unshare()`, fetch IDs with `NS_GET_ID`, and call `sys_listns()` with global, specific `user_ns_id`, or `LISTNS_CURRENT_USER` filters. Cases verify unprivileged tasks see their own namespace, holders of `CAP_SYS_ADMIN` inside a user namespace see namespaces owned by it, sibling user namespaces do not see each other’s namespaces, parent user namespaces can see child user namespaces, and dropping `CAP_SYS_ADMIN` with libcap plus `PR_SET_NO_NEW_PRIVS` does not increase visibility.

**State, dependencies, integration:** State is held by forked children and pipes carrying booleans/counts. It depends on libcap, procfs namespace links, `linux/nsfs.h`, `wrappers.h`, and `../filesystems/utils.c` from the Makefile. It integrates with the kernel permission checks behind list traversal and namespace owner relationships.

**Risks and test signals:** Several checks require user namespace creation and, for the drop-capability test, starting with effective `CAP_SYS_ADMIN`. Some tests assert minimum counts rather than exact sets because init namespaces may remain visible. Passing signals that `listns` honors ownership and capability rules without exposing sibling-owned namespaces.
