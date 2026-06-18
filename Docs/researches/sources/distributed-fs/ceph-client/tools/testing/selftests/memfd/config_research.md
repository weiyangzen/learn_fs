# sources/distributed-fs/ceph-client/tools/testing/selftests/memfd/config

Purpose: kernel config fragment for memfd FUSE tests.

Important APIs/types/functions: requests `CONFIG_FUSE_FS=m`.

Control flow: none.

State and persistence: build configuration only.

Dependencies and integration points: supports the FUSE mount helper used by memfd GUP race tests.

Risks: module form requires load permission at runtime.

Test signals: FUSE tests can run when the module and userspace FUSE tooling are available.
