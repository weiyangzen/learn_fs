# subset-b-006856 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/sysmap_is_sealed.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/sysmap_is_sealed.c

**Purpose:** Kselftest coverage for `CONFIG_MSEAL_SYSTEM_MAPPINGS=y`. It verifies selected special process mappings expose the `sl` sealed flag in `/proc/self/smaps`, while `[stack]` remains unsealed.

**Important APIs and flow:** `has_mapping()` scans the already opened smaps stream for a variant mapping name. `mapping_is_sealed()` continues scanning to the next `VmFlags:` line and checks for `sl`. A `basic` fixture owns `FILE *maps` from `/proc/self/smaps`; fixture variants cover `[vdso]`, `[vvar]`, `[vvar_vclock]`, `[sigpage]`, `[vectors]`, `[uprobes]`, and `[stack]`. `TEST_F(basic, check_sealed)` skips unavailable mappings and compares the expected seal boolean with parsed flags.

**State, dependencies, integration:** The only persistent state is the procfs smaps stream inside the fixture. It depends on `kselftest_harness.h`, procfs smaps formatting, and architecture-specific mapping names. It integrates with the mseal selftest directory as a runtime check of kernel VMA flag reporting rather than calling `mseal()` directly.

**Risks and test signals:** The parser is stream-order sensitive: after `has_mapping()` consumes through a mapping line, `mapping_is_sealed()` assumes the following `VmFlags:` belongs to that mapping. Missing architecture mappings are skipped. A pass signals system mappings are tagged sealed in smaps and ordinary stack mappings are not falsely tagged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mseal_system_mappings/sysmap_is_sealed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/Makefile -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/Makefile

**Purpose:** Build manifest for the namespace selftests in this subset. It compiles tests for namespace IDs, nsfs file handles, init namespace inode constants, active references, `listns`, permissions, EFAULT handling, socket namespace lookup, credential changes, stress, pagination regression, and pidfd `setns`.

**Important APIs and flow:** `CFLAGS` enables warnings, debug info, no optimization, and kernel/tool include paths. `LDLIBS += -lcap` supports tests using libcap. `TEST_GEN_PROGS` lists generated binaries. After `include ../lib.mk`, several targets add `../filesystems/utils.c` as an extra source, matching tests that call `setup_userns()`, `get_userns_fd()`, or related helpers.

**State, dependencies, integration:** There is no runtime state; it is a kselftest build declaration. It integrates with the top-level selftests framework through `lib.mk` and with namespace tests through shared utility compilation. The dependency on libcap is important for permission-drop tests.

**Risks and test signals:** If a test using `setup_userns()` is added but not listed with `../filesystems/utils.c`, link failures occur. If libcap is absent, capability permission tests fail to build. Successful build confirms all namespace programs are registered for kselftest execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/config -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/config

**Purpose:** Kernel config fragment declaring namespace features required by the namespace selftests.

**Important entries:** It requests `CONFIG_UTS_NS`, `CONFIG_TIME_NS`, `CONFIG_IPC_NS`, `CONFIG_USER_NS`, `CONFIG_PID_NS`, `CONFIG_NET_NS`, and `CONFIG_CGROUPS`. These match the namespace types exercised by `/proc/<pid>/ns/*`, `unshare()`, `setns()`, `NS_GET_ID`, file-handle reopening, and `listns` type filtering.

**State, dependencies, integration:** The file has no runtime behavior. It integrates with kselftest config collection so builders know which kernel features must be enabled for meaningful execution.

**Risks and test signals:** Missing entries cause broad skips or failures, especially for user namespace setup, time namespace inode checks, cgroup namespace handle tests, and net namespace socket tests. A configured kernel with these options gives the rest of the subset a viable execution environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/cred_change_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/cred_change_test.c

**Purpose:** Regression coverage for namespace active references across credential changes. The tests are aimed at `commit_creds()`/credential switching paths that must swap active references without leaking or underflowing user namespace activity.

**Important APIs and flow:** Tests create user namespaces with `get_userns_fd()` and enter them with `setns(CLONE_NEWUSER)`. They obtain stable namespace IDs via `open("/proc/self/ns/user")` plus `ioctl(NS_GET_ID)`, pass IDs to the parent over pipes, and query liveness with `sys_listns()` using `struct ns_id_req`. Individual cases exercise `setuid()`, `setgid()`, `setresuid()`, nested user namespaces, rapid mixed `set*id()` calls, and `setfsuid()`/`setfsgid()`.

**State, dependencies, integration:** State is intentionally externalized to kernel namespace active-ref counters, visible through `listns`. Children hold transient namespace membership and credentials; parents verify the user namespace appears while a child is live and disappears after exit. The file depends on `../filesystems/utils.h`, `wrappers.h`, `linux/nsfs.h`, and kselftest harness macros.

**Risks and test signals:** Tests skip when `listns` is unsupported and may fail early if user namespace mappings are not permitted. They tolerate expected `EPERM` from credential changes that cannot be performed. Pass signals that credential mutation does not leave user namespaces active after the last task exits and does not drop active references prematurely while tasks are still running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/cred_change_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/file_handle_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/file_handle_test.c

**Purpose:** Validates nsfs file-handle support for namespace file descriptors and user-namespace isolation semantics for `open_by_handle_at()`.

**Important APIs and flow:** Basic tests open `/proc/self/ns/{net,uts,ipc,pid,mnt,user,cgroup,time}`, call `name_to_handle_at(..., AT_EMPTY_PATH)`, reopen via `open_by_handle_at(FD_NSFS_ROOT, handle, O_RDONLY)`, and compare `st_ino`/`st_dev`. Isolation tests first capture a handle in the parent namespace, then fork a child that creates a new user namespace, installs uid/gid mappings, creates a namespace of the tested type, and tries to open the parent handle. The expected result is `ESTALE`, reported to the parent with one-byte status codes. PID and time namespace tests fork a grandchild because those namespaces take effect after fork. `nsfs_open_flags` asserts write/truncate/direct/tmpfile/directory flag failures.

**State, dependencies, integration:** The durable object under test is the nsfs file handle, containing kernel namespace identity. Tests depend on `FD_NSFS_ROOT`, `MAX_HANDLE_SZ`, procfs namespace links, and support for user namespace mapping writes. They integrate with VFS export-style handle operations and namespace ownership permission checks.

**Risks and test signals:** Some kernels or environments return `EOPNOTSUPP`, `EINVAL`, `EPERM`, or lack cgroup/time namespaces, producing skips. The repeated hand-written mapping code is sensitive to setgroups and uid/gid-map policy. Passing tests indicate namespace handles reopen the same object when visible, are rejected across user namespace ownership boundaries, and enforce read-only namespace FD semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/file_handle_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/init_ino_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/init_ino_test.c

**Purpose:** Checks that init namespace procfs links expose the canonical inode constants from `linux/nsfs.h`.

**Important APIs and flow:** `struct ns_info` maps namespace names to `/proc/1/ns/*` paths and expected constants: IPC, UTS, USER, PID, CGROUP, TIME, NET, and MNT. `TEST(init_namespace_inodes)` iterates the table, `stat()`s each procfs namespace symlink target, skips `ENOENT`, and asserts `st_ino` equals the expected constant.

**State, dependencies, integration:** There is no owned state beyond the static table. It depends on procfs, PID 1 namespace links, and exported nsfs inode constants. It integrates as a compatibility check between kernel headers and runtime namespace inode assignment.

**Risks and test signals:** Containers can make `/proc/1/ns/*` refer to the container’s PID 1 rather than host init, so execution context matters. Missing namespace files are skipped. Passing signals that init namespace inode ABI constants are reflected in procfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/init_ino_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_efault_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_efault_test.c

**Purpose:** Fault-injection and concurrency coverage for the `listns` syscall. It verifies invalid user buffers return the right errors and that namespace cleanup during iteration does not deadlock or corrupt active-reference handling.

**Important APIs and flow:** Tests construct `struct ns_id_req`, call `sys_listns()`, and build invalid buffers with `mmap()` followed by `munmap()` of the second page. Iterator children loop in `listns()` against a partially invalid buffer while the parent creates mount-namespace children with `create_child(..., CLONE_NEWNS)`, mounts tmpfs under `/tmp/test_mnt*`, then signals them to exit. Variants cover one-u64 partial fault, full invalid pointer `0xdeadbeef`, NULL buffer, late page-boundary fault after several writes, and mount-namespace-only cleanup.

**State, dependencies, integration:** State lives in child processes, mount namespaces, tmpfs mounts, pidfds, and the kernel namespace tree. It depends on `../pidfd/pidfd.h`, `wrappers.h`, mount permissions, and helper I/O wrappers. It integrates with `listns` copy-to-user error paths and RCU cleanup behavior.

**Risks and test signals:** The file intentionally races cleanup and faults, so environment limits on mount namespaces can cause child setup failures. The comments expect complete invalid buffers to return `EFAULT`; the partial-boundary comment mentions `EINVAL`, so kernel behavior must be checked against implementation. Passing tests primarily signal no hangs, correct `EFAULT` for invalid buffers, and safe cleanup when namespaces are destroyed during iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_efault_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_pagination_bug.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_pagination_bug.c

**Purpose:** Minimal regression test for a `listns` pagination bug where the continuation lookup ignored the requested namespace type filter and could return an ID from the unified tree with the wrong type.

**Important APIs and flow:** The test creates ten children, each running `setup_userns()` and waiting on a socketpair. It calls `sys_listns()` with `ns_type = CLONE_NEWUSER` and a three-entry buffer. If the first batch fills, it sets `req.ns_id` to the last returned ID and requests the next batch. The assertion is simply that the second call succeeds; KASAN or kernel warnings would catch the historical out-of-bounds path.

**State, dependencies, integration:** Child user namespaces are held active by sleeping children. The parent owns the pagination cursor in `req.ns_id`. Dependencies are `../filesystems/utils.h`, `wrappers.h`, and enough permission to create user namespaces. The test integrates directly with `do_listns()` continuation logic.

**Risks and test signals:** A small namespace population may not fill the first batch, reducing coverage. Failure to create user namespaces aborts the test. A pass signals type-filtered pagination can continue from a previous namespace ID without cross-type lookup corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_pagination_bug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_permissions_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_permissions_test.c

**Purpose:** Permission model coverage for `listns`, especially user-namespace scoping, `CAP_SYS_ADMIN`, current-user filtering, sibling isolation, and capability dropping.

**Important APIs and flow:** Tests create user namespaces with `setup_userns()`, create owned net/UTS/IPC namespaces with `unshare()`, fetch IDs with `NS_GET_ID`, and call `sys_listns()` with global, specific `user_ns_id`, or `LISTNS_CURRENT_USER` filters. Cases verify unprivileged tasks see their own namespace, holders of `CAP_SYS_ADMIN` inside a user namespace see namespaces owned by it, sibling user namespaces do not see each other’s namespaces, parent user namespaces can see child user namespaces, and dropping `CAP_SYS_ADMIN` with libcap plus `PR_SET_NO_NEW_PRIVS` does not increase visibility.

**State, dependencies, integration:** State is held by forked children and pipes carrying booleans/counts. It depends on libcap, procfs namespace links, `linux/nsfs.h`, `wrappers.h`, and `../filesystems/utils.c` from the Makefile. It integrates with the kernel permission checks behind list traversal and namespace owner relationships.

**Risks and test signals:** Several checks require user namespace creation and, for the drop-capability test, starting with effective `CAP_SYS_ADMIN`. Some tests assert minimum counts rather than exact sets because init namespaces may remain visible. Passing signals that `listns` honors ownership and capability rules without exposing sibling-owned namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_permissions_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_test.c

**Purpose:** Core functional coverage for the `listns` syscall: global listing, type filters, pagination, owner filters, active-only semantics, hierarchy visibility, and error handling.

**Important APIs and flow:** The file uses `struct ns_id_req` with fields `size`, `ns_id`, `ns_type`, and `user_ns_id`, and calls `sys_listns()` from `wrappers.h`. Tests cover all namespaces, `CLONE_NEWNET` filtering, pagination by setting `req.ns_id` to the prior batch tail, `LISTNS_CURRENT_USER`, creation and disappearance of a transient net namespace, listing namespaces owned by a child user namespace, combined `CLONE_NEWNET | CLONE_NEWUTS`, nested user namespace visibility, and invalid flags/spare fields/NULL buffers/huge counts. Some returned IDs are turned into `struct nsfs_file_handle` and reopened to verify type via `NS_GET_NSTYPE`.

**State, dependencies, integration:** State is active namespace membership in child processes synchronized by pipes or socketpairs. The test depends on `../filesystems/utils.h`, `linux/nsfs.h`, `open_by_handle_at(FD_NSFS_ROOT, ...)`, and procfs. It is the general integration test for the `listns` ABI.

**Risks and test signals:** It skips on `ENOSYS`. Exact counts vary by environment, so most checks assert positivity, monotonic pagination, or presence/absence of a known ID. Passing signals stable enumeration, filtering, continuation, active-ref visibility, and expected input validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/listns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/ns_active_ref_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/ns_active_ref_test.c

**Purpose:** Broad regression suite for namespace active-reference lifetime rules. It verifies that active namespaces can be reopened by nsfs handles, inactive namespaces cannot, open namespace FDs and child namespaces propagate activity to owners, and cleanup works for processes and threads.

**Important APIs and flow:** The tests use `name_to_handle_at()`, synthetic `struct nsfs_file_handle` values built from `NS_GET_ID`, `open_by_handle_at(FD_NSFS_ROOT, ...)`, `NS_GET_USERNS`, `sys_listns()`, `setup_userns()`, `unshare()`, `setns()`, `pthread_create()`, pipes, and socketpairs. Early cases cover init namespace permanence, inactive-after-exit behavior, multiple processes, user/PID namespace lifecycles, and an fd keeping a namespace active. Middle cases build user namespace ownership hierarchies and assert active references propagate from child namespaces to parent user namespaces, including multi-level, multiple-child, mixed-type, and bind-mount scenarios. Later cases repeat lifecycle checks with threads and multi-threaded subprocesses.

**State, dependencies, integration:** Kernel state under test is the active reference count and namespace owner tree. User-space state includes open namespace FDs, file handles, child processes, thread synchronization pipes, and temporary bind-mount paths. It depends on nsfs file handles, procfs namespace links, pthreads, mount namespace support, and `../filesystems/utils.c`. It integrates with VFS handle lookup, namespace ownership, and `listns` visibility.

**Risks and test signals:** The suite is privilege and environment sensitive: user namespaces, net namespaces, mounts, and nsfs file handles may be unavailable. Some tests construct handles from namespace IDs with `ns_type = 0`, relying on nsfs handle semantics. Passing tests signal that active references are acquired, propagated, dropped, and resurrected correctly without leaking inactive namespaces or making parents unreachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/ns_active_ref_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/nsid_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/nsid_test.c

**Purpose:** Verifies stable namespace IDs exposed through nsfs ioctls for each namespace type, and for network namespaces verifies ID equivalence with `SO_NETNS_COOKIE`.

**Important APIs and flow:** A fixture tracks one child PID for cleanup. Basic tests open `/proc/self/ns/*`, call `ioctl(NS_GET_ID)` or `NS_GET_MNTNS_ID`, assert nonzero stable IDs, and repeat the ioctl to ensure identity stability. Separate tests fork a child, unshare one namespace type, keep it alive with `pause()`, open `/proc/<pid>/ns/<type>`, and assert parent and child IDs differ. PID and time namespaces fork a grandchild because the new namespace takes effect after fork. Network tests also create sockets and compare `SO_NETNS_COOKIE` with `NS_GET_ID`.

**State, dependencies, integration:** State is primarily child namespace membership and open namespace FDs. It depends on procfs namespace links, `linux/nsfs.h`, socket APIs, and permissions for `unshare()`. It integrates with nsfs ID allocation and network namespace cookie plumbing.

**Risks and test signals:** Individual separate-namespace tests skip if `unshare()` returns permission errors or if time namespaces are unavailable. The fixture kills lingering children in teardown. Passing signals namespace IDs are nonzero, stable across repeated queries, distinct for newly created namespaces, and aligned with network namespace socket cookies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/nsid_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/regression_pidfd_setns_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/regression_pidfd_setns_test.c

**Purpose:** Regression coverage for a pidfd `setns()` active-reference race described in the file comments: if the target task exits between namespace-set preparation and commit, active refs could be mishandled.

**Important APIs and flow:** Both tests use `create_child()` from the pidfd helpers to obtain a pidfd. `simple_pidfd_setns` creates a child that unshares UTS, IPC, NET, and USER namespaces, signals readiness over a socketpair, exits, and lets the parent call `setns(pidfd, CLONE_NEWUTS | CLONE_NEWIPC)`. `simple_pidfd_setns_clone` creates the child with namespace clone flags directly and calls `setns()` while the child sleeps. `SIGCHLD` is ignored for autoreap.

**State, dependencies, integration:** State is the pidfd, target task namespace set, and child lifetime. It depends on pidfd selftest helpers and `setns()` pidfd support. It integrates with namespace set preparation/commit and active-ref acquisition paths.

**Risks and test signals:** The tests log `setns()` return values but do not assert success, because the regression signal is kernel warnings or refcount failures rather than user-space return alone. Environment restrictions on user/net namespace creation can affect the path. Passing without kernel splats signals pidfd namespace switching no longer resurrects or underflows active refs incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/regression_pidfd_setns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/siocgskns_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/siocgskns_test.c

**Purpose:** Tests the `SIOCGSKNS` socket ioctl, which returns a file descriptor for the network namespace associated with a socket, and verifies its interaction with active references, `listns`, nsfs handles, owner user namespaces, and resurrection of inactive namespace trees.

**Important APIs and flow:** Basic tests call `ioctl(sock, SIOCGSKNS)` on IPv4/IPv6 TCP/UDP/raw sockets and compare the returned namespace FD with `/proc/self/ns/net`. Lifecycle tests create sockets in child net namespaces, pass socket FDs to parents via `SCM_RIGHTS`, let children exit, and use `SIOCGSKNS` to recover active netns FDs. Other tests verify behavior across `setns()`, non-socket rejection, multiple sockets, `listns` visibility, owner lookup through `NS_GET_USERNS`, and reopening via synthetic `struct nsfs_file_handle`. The final multilevel test builds nested user namespaces plus a net namespace and asserts repeated `SIOCGSKNS` calls resurrect and drop the full owner chain.

**State, dependencies, integration:** The socket FD is the key persistent user-space handle; namespace FDs obtained from `SIOCGSKNS` become active references. The file depends on `linux/sockios.h`, `linux/nsfs.h`, `FD_NSFS_ROOT`, `FILEID_NSFS`, `setup_userns()`, `sys_listns()`, and SCM_RIGHTS messaging. It integrates socket lifetime with namespace active-ref accounting and nsfs file-handle lookup.

**Risks and test signals:** Raw sockets may require privileges; unsupported `SIOCGSKNS`, `NS_GET_ID`, `NS_GET_USERNS`, or `open_by_handle_at` paths skip. Some tests intentionally close namespace FDs to prove socket-only state is insufficient until `SIOCGSKNS` reacquires refs. Passing signals socket-owned network namespaces can be located, made visible, reopened, released, and resurrected with correct owner propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/siocgskns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/stress_test.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/stress_test.c

**Purpose:** Stress coverage for namespace active-reference accounting and `listns` under rapid creation/destruction, high concurrency, nested hierarchies, pagination, and churn patterns similar to container workloads.

**Important APIs and flow:** Tests establish a baseline with `sys_listns()`, create namespaces in child processes using `setup_userns()`, `get_userns_fd()`, `setns()`, and `unshare()`, then assert post-cleanup counts return to baseline. Cases include 100 rapid user namespace cycles, 50 concurrent user namespaces synchronized over a socketpair, 50 mixed user/net/UTS/IPC cycles, 20 five-level nested user namespace hierarchies, forced five-entry pagination with duplicate detection, 20 workers concurrently creating and listing namespaces, and 10 churn batches of user/net/UTS namespace sets.

**State, dependencies, integration:** State is intentionally transient: child processes hold namespaces active until signaled or exit. Baseline and after counts are stored in local arrays. It depends on `../filesystems/utils.h`, `wrappers.h`, fork/wait, socketpairs, and permission to create namespaces. It integrates with the scalability and cleanup behavior of namespace active refs and `listns` traversal.

**Risks and test signals:** Count equality can be affected by unrelated namespace activity on a shared test host. Resource limits may prevent spawning many children or nested user namespaces. The pagination stress detects duplicate IDs but does not require all test-created IDs be individually identified. Passing signals no active-ref leaks after high churn, no duplicate pagination entries, and no obvious concurrency failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/stress_test.c -->
