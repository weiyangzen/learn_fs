# sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/config

Purpose: declares `CONFIG_USER_NS=y` for the rlimits-per-userns selftest. There is no code flow or persistent state. Integration is kselftest kernel configuration preparation for user namespace behavior under process limits. Risks are that the test also requires the ability to set UID/GID 60000, unshare user namespaces, and manipulate `RLIMIT_NPROC`; those are runtime policy issues outside this config. Test signals are successful `unshare(CLONE_NEWUSER)` in the child service path.
