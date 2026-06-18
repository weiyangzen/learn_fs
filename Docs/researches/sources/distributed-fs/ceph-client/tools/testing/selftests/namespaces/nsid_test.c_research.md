## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/nsid_test.c

**Purpose:** Verifies stable namespace IDs exposed through nsfs ioctls for each namespace type, and for network namespaces verifies ID equivalence with `SO_NETNS_COOKIE`.

**Important APIs and flow:** A fixture tracks one child PID for cleanup. Basic tests open `/proc/self/ns/*`, call `ioctl(NS_GET_ID)` or `NS_GET_MNTNS_ID`, assert nonzero stable IDs, and repeat the ioctl to ensure identity stability. Separate tests fork a child, unshare one namespace type, keep it alive with `pause()`, open `/proc/<pid>/ns/<type>`, and assert parent and child IDs differ. PID and time namespaces fork a grandchild because the new namespace takes effect after fork. Network tests also create sockets and compare `SO_NETNS_COOKIE` with `NS_GET_ID`.

**State, dependencies, integration:** State is primarily child namespace membership and open namespace FDs. It depends on procfs namespace links, `linux/nsfs.h`, socket APIs, and permissions for `unshare()`. It integrates with nsfs ID allocation and network namespace cookie plumbing.

**Risks and test signals:** Individual separate-namespace tests skip if `unshare()` returns permission errors or if time namespaces are unavailable. The fixture kills lingering children in teardown. Passing signals namespace IDs are nonzero, stable across repeated queries, distinct for newly created namespaces, and aligned with network namespace socket cookies.
