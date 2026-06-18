<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/buildkitd-entrypoint -->
# sources/cloud-native/buildkit/hack/buildkitd-entrypoint

Purpose: container entrypoint wrapper for `buildkitd` that attempts to create a cgroup namespace and remount `/sys/fs/cgroup` for cgroup v2 when running under an inherited cgroup path.

Important APIs, types, and functions: shell script with `set -e`. It checks `/sys/fs/cgroup/cgroup.controllers`, inspects `/proc/self/cgroup`, probes `/usr/bin/unshare --cgroup --mount /usr/bin/with-cgroupfs-remount true`, and on success `exec`s buildkitd through the same namespace/remount wrapper.

Control flow and state: no persistence. On cgroup v2 and non-root cgroup path, it tries an unshare/remount probe. If the probe succeeds it replaces the process with namespaced `buildkitd`; otherwise it logs a skip message and falls back to direct `buildkitd`.

Dependencies and integration: depends on Linux cgroup v2, `/usr/bin/unshare`, `/usr/bin/with-cgroupfs-remount`, and `/usr/bin/buildkitd`. It exists as a Kubernetes workaround until cgroup namespace control is available through the API.

Risks and test signals: failures intentionally degrade to direct execution, so deployments may silently lack the desired namespace behavior except for stderr. Tests are usually image/runtime tests that run under cgroup v2 and verify the fallback and successful exec paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/buildkitd-entrypoint -->
