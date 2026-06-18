## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/config

**Purpose:** Kernel config fragment declaring namespace features required by the namespace selftests.

**Important entries:** It requests `CONFIG_UTS_NS`, `CONFIG_TIME_NS`, `CONFIG_IPC_NS`, `CONFIG_USER_NS`, `CONFIG_PID_NS`, `CONFIG_NET_NS`, and `CONFIG_CGROUPS`. These match the namespace types exercised by `/proc/<pid>/ns/*`, `unshare()`, `setns()`, `NS_GET_ID`, file-handle reopening, and `listns` type filtering.

**State, dependencies, integration:** The file has no runtime behavior. It integrates with kselftest config collection so builders know which kernel features must be enabled for meaningful execution.

**Risks and test signals:** Missing entries cause broad skips or failures, especially for user namespace setup, time namespace inode checks, cgroup namespace handle tests, and net namespace socket tests. A configured kernel with these options gives the rest of the subset a viable execution environment.
