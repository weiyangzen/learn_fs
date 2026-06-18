## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/stress_test.c

**Purpose:** Stress coverage for namespace active-reference accounting and `listns` under rapid creation/destruction, high concurrency, nested hierarchies, pagination, and churn patterns similar to container workloads.

**Important APIs and flow:** Tests establish a baseline with `sys_listns()`, create namespaces in child processes using `setup_userns()`, `get_userns_fd()`, `setns()`, and `unshare()`, then assert post-cleanup counts return to baseline. Cases include 100 rapid user namespace cycles, 50 concurrent user namespaces synchronized over a socketpair, 50 mixed user/net/UTS/IPC cycles, 20 five-level nested user namespace hierarchies, forced five-entry pagination with duplicate detection, 20 workers concurrently creating and listing namespaces, and 10 churn batches of user/net/UTS namespace sets.

**State, dependencies, integration:** State is intentionally transient: child processes hold namespaces active until signaled or exit. Baseline and after counts are stored in local arrays. It depends on `../filesystems/utils.h`, `wrappers.h`, fork/wait, socketpairs, and permission to create namespaces. It integrates with the scalability and cleanup behavior of namespace active refs and `listns` traversal.

**Risks and test signals:** Count equality can be affected by unrelated namespace activity on a shared test host. Resource limits may prevent spawning many children or nested user namespaces. The pagination stress detects duplicate IDs but does not require all test-created IDs be individually identified. Passing signals no active-ref leaks after high churn, no duplicate pagination entries, and no obvious concurrency failures.
