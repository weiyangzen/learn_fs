## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/cred_change_test.c

**Purpose:** Regression coverage for namespace active references across credential changes. The tests are aimed at `commit_creds()`/credential switching paths that must swap active references without leaking or underflowing user namespace activity.

**Important APIs and flow:** Tests create user namespaces with `get_userns_fd()` and enter them with `setns(CLONE_NEWUSER)`. They obtain stable namespace IDs via `open("/proc/self/ns/user")` plus `ioctl(NS_GET_ID)`, pass IDs to the parent over pipes, and query liveness with `sys_listns()` using `struct ns_id_req`. Individual cases exercise `setuid()`, `setgid()`, `setresuid()`, nested user namespaces, rapid mixed `set*id()` calls, and `setfsuid()`/`setfsgid()`.

**State, dependencies, integration:** State is intentionally externalized to kernel namespace active-ref counters, visible through `listns`. Children hold transient namespace membership and credentials; parents verify the user namespace appears while a child is live and disappears after exit. The file depends on `../filesystems/utils.h`, `wrappers.h`, `linux/nsfs.h`, and kselftest harness macros.

**Risks and test signals:** Tests skip when `listns` is unsupported and may fail early if user namespace mappings are not permitted. They tolerate expected `EPERM` from credential changes that cannot be performed. Pass signals that credential mutation does not leave user namespaces active after the last task exits and does not drop active references prematurely while tasks are still running.
