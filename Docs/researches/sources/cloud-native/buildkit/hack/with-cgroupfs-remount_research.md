<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/with-cgroupfs-remount -->
# sources/cloud-native/buildkit/hack/with-cgroupfs-remount

Purpose: helper wrapper used after creating a mount namespace to remount `/sys/fs/cgroup` before executing a command.

Important APIs, types, and functions: shell script reads the existing `/sys/fs/cgroup` mount options from `/proc/self/mounts`, unmounts `/sys/fs/cgroup`, mounts `cgroup2` back with the same options, and `exec`s its arguments.

Control flow and state: changes mount namespace state for the running process tree, then replaces itself with the target command.

Dependencies and integration: called by `hack/buildkitd-entrypoint` during cgroup namespace setup. Depends on Linux mount permissions and cgroup filesystem layout.

Risks and test signals: incorrect remount behavior can break cgroup visibility for BuildKit workers. Test in cgroup v2 containerized environments by verifying BuildKit sees the intended cgroup namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/with-cgroupfs-remount -->
