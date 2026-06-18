# sources/cloud-native/soci-snapshotter/integ_entrypoint.sh

Purpose: keeps the integration-test container alive and prepares cgroup v2 nesting so containerd and child containers can run inside the test environment.

Important APIs and flow: the script enables shell tracing, checks for `/sys/fs/cgroup/cgroup.controllers`, moves root cgroup processes into `/sys/fs/cgroup/init`, writes enabled controllers to `cgroup.subtree_control`, and then sleeps forever.

State and persistence: mutates the container's cgroup filesystem by creating `/sys/fs/cgroup/init`, moving processes, and enabling controllers for nested cgroups. It does not exit under normal operation.

Dependencies and integration: copied from Docker-in-Docker setup logic and used as a container entrypoint for integration shells that need cgroup v2 controller delegation.

Risks and test signals: assumes writable cgroup v2 hierarchy and sufficient privilege. The ignored `xargs` error handles races or missing process IDs. If cgroup setup fails silently after tracing, later integration tests may fail in containerd/runtime setup rather than at entrypoint time.
