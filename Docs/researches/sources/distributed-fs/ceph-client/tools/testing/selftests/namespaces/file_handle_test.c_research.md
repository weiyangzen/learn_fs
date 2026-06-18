## sources/distributed-fs/ceph-client/tools/testing/selftests/namespaces/file_handle_test.c

**Purpose:** Validates nsfs file-handle support for namespace file descriptors and user-namespace isolation semantics for `open_by_handle_at()`.

**Important APIs and flow:** Basic tests open `/proc/self/ns/{net,uts,ipc,pid,mnt,user,cgroup,time}`, call `name_to_handle_at(..., AT_EMPTY_PATH)`, reopen via `open_by_handle_at(FD_NSFS_ROOT, handle, O_RDONLY)`, and compare `st_ino`/`st_dev`. Isolation tests first capture a handle in the parent namespace, then fork a child that creates a new user namespace, installs uid/gid mappings, creates a namespace of the tested type, and tries to open the parent handle. The expected result is `ESTALE`, reported to the parent with one-byte status codes. PID and time namespace tests fork a grandchild because those namespaces take effect after fork. `nsfs_open_flags` asserts write/truncate/direct/tmpfile/directory flag failures.

**State, dependencies, integration:** The durable object under test is the nsfs file handle, containing kernel namespace identity. Tests depend on `FD_NSFS_ROOT`, `MAX_HANDLE_SZ`, procfs namespace links, and support for user namespace mapping writes. They integrate with VFS export-style handle operations and namespace ownership permission checks.

**Risks and test signals:** Some kernels or environments return `EOPNOTSUPP`, `EINVAL`, `EPERM`, or lack cgroup/time namespaces, producing skips. The repeated hand-written mapping code is sensitive to setgroups and uid/gid-map policy. Passing tests indicate namespace handles reopen the same object when visible, are rejected across user namespace ownership boundaries, and enforce read-only namespace FD semantics.
