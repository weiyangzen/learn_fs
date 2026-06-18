# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/cgroup_helpers.c

Purpose: creates and manages isolated cgroup v2 and cgroup v1 net_cls environments for BPF selftests.

Important APIs and functions: cgroup v2 helpers include `setup_cgroup_environment`, `cleanup_cgroup_environment`, `enable_controllers`, `write_cgroup_file`, `join_cgroup`, `join_root_cgroup`, `join_parent_cgroup`, `set_cgroup_xattr`, `create_and_get_cgroup`, `remove_cgroup`, `get_root_cgroup`, `get_cgroup_id`, and `cgroup_setup_and_join`. cgroup v1 helpers include `setup_classid_environment`, `cleanup_classid_environment`, `set_classid`, `join_classid`, `get_classid_cgroup_id`, `get_cgroup1_hierarchy_id`, and `open_classid`.

Control flow: v2 setup creates a new mount namespace, makes `/` private, mounts cgroup2 at `/mnt`, removes stale workdirs, creates a pid-scoped workdir, and enables controllers. Cleanup moves to root and recursively removes cgroups with `nftw`. Classid setup mounts tmpfs and net_cls under `/sys/fs/cgroup`, creates pid-scoped workdir, and writes classid.

State and persistence: thread-local `cgroup_workdir_mounted` tracks whether cleanup should unmount. Filesystem mount/cgroup state persists until cleanup and is pid-scoped under workdir names.

Dependencies and integration points: uses mount namespaces, cgroupfs, net_cls cgroup v1, `name_to_handle_at` for cgroup id, xattrs, and logging macro from `cgroup_helpers.h`.

Risks: requires privileges for unshare/mount; hard-coded `/mnt` and `/sys/fs/cgroup` can conflict; cleanup can fail if processes remain in cgroups; `get_cgroup1_hierarchy_id` inner loop appears to compare the wrong token variable in the multi-controller branch, risking missed matches.

Test signals: successful setup returns fds/ids and allows BPF cgroup attachment tests to run; cleanup errors are logged with file/line/errno.
