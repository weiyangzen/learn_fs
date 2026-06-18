# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/statmount/statmount_test_ns.c

## Purpose

`statmount_test_ns.c` validates mount namespace id reporting through statmount and listmount, including by-fd behavior and querying another process's mount namespace.

## Important APIs, Types, and Functions

It defines `NSID_PASS`, `NSID_FAIL`, `NSID_SKIP`, and `NSID_ERROR`, with `handle_result` translating child return codes to kselftest results. Helpers include `get_mnt_ns_id`, `setup_namespace`, `_test_statmount_mnt_ns_id`, `_test_statmount_mnt_ns_id_by_fd`, `test_statmount_mnt_ns_id`, `validate_external_listmount`, and `test_listmount_ns`. APIs include `ioctl(NS_GET_MNTNS_ID)`, `statmount`, `listmount`, `STATMOUNT_BY_FD`, `get_unique_mnt_id`, `setup_userns`, `fork`, and `wait_for_pid`.

## Control Flow, State, and Persistence

The statmount namespace-id test forks a child, sets up a user namespace, obtains the current mount namespace id from nsfs, stats `/` with `STATMOUNT_MNT_NS_ID`, and checks equality. The by-fd subtest bind-mounts a temporary directory, stats namespace id by fd while mounted, detaches it, and verifies `STATMOUNT_MNT_NS_ID` is no longer reported for the detached mount. The listmount namespace test creates a child namespace with a known mount count, then the parent gets the child's mount namespace id through `/proc/<pid>/ns/mnt` and calls `listmount` against that external id to validate visibility/count behavior. State is mostly child namespaces, temp bind mounts, and namespace ids.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are nsfs mount namespace ids, statmount/listmount namespace-id support, user namespace helpers, procfs, and mount privilege. It integrates namespace-aware mount introspection across process boundaries. Risks include child synchronization, namespace lifetime tied to process/fd references, optional mask support producing skips, and a diagnostic `sleep(60)` on open failure. Passing signals are matching statmount namespace ids, missing namespace id for detached by-fd mounts, and successful external listmount count validation.
