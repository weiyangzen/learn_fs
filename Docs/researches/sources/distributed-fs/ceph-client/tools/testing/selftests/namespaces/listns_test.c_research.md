## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_test.c

**Purpose:** Core functional coverage for the `listns` syscall: global listing, type filters, pagination, owner filters, active-only semantics, hierarchy visibility, and error handling.

**Important APIs and flow:** The file uses `struct ns_id_req` with fields `size`, `ns_id`, `ns_type`, and `user_ns_id`, and calls `sys_listns()` from `wrappers.h`. Tests cover all namespaces, `CLONE_NEWNET` filtering, pagination by setting `req.ns_id` to the prior batch tail, `LISTNS_CURRENT_USER`, creation and disappearance of a transient net namespace, listing namespaces owned by a child user namespace, combined `CLONE_NEWNET | CLONE_NEWUTS`, nested user namespace visibility, and invalid flags/spare fields/NULL buffers/huge counts. Some returned IDs are turned into `struct nsfs_file_handle` and reopened to verify type via `NS_GET_NSTYPE`.

**State, dependencies, integration:** State is active namespace membership in child processes synchronized by pipes or socketpairs. The test depends on `../filesystems/utils.h`, `linux/nsfs.h`, `open_by_handle_at(FD_NSFS_ROOT, ...)`, and procfs. It is the general integration test for the `listns` ABI.

**Risks and test signals:** It skips on `ENOSYS`. Exact counts vary by environment, so most checks assert positivity, monotonic pagination, or presence/absence of a known ID. Passing signals stable enumeration, filtering, continuation, active-ref visibility, and expected input validation.
