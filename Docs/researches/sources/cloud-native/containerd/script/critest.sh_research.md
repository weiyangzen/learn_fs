<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/critest.sh -->
# sources/cloud-native/containerd/script/critest.sh

- Purpose: Starts an isolated containerd daemon and runs Kubernetes CRI conformance tests through `critest`, writing logs and reports to a caller-supplied report directory.
- Important functions and variables: `traverse_path` relaxes execute permissions up the temporary build directory path for user-namespace runc startup; `cleanup` kills containerd, prints logs, and removes the temp directory. Inputs include `TEST_RUNTIME`, `CGROUP_DRIVER`, `SKIP_TEST`, `FOCUS_TEST`, and `EXTRA_CRITEST_OPTIONS`.
- Control flow: Create `BDIR`, write `config.toml` with CRI runtime and overlayfs `slow_chown`, optionally enable `SystemdCgroup`, assemble Ginkgo skip/focus flags, start `/usr/local/bin/containerd`, poll `crictl info`, then run `critest --parallel=8`.
- State and persistence: Mutates a temporary root/state tree under `BDIR`, writes `containerd.log`, and deletes temporary state on exit. It also uses `pkill containerd`, which can affect unrelated daemons in the same environment.
- Dependencies and integration: Requires containerd, `crictl`, `critest`, CNI config under `/etc/cni/net.d`, and a runtime shim matching `TEST_RUNTIME`.
- Risks: Unquoted `mkdir -p $report_dir`, broad `pkill containerd`, and root permission changes make it best suited for disposable CI hosts. The systemd cgroup OOMKilled test is skipped due to scope GC races.
- Test signals: The `critest` report directory and printed containerd logs are the primary failure diagnostics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/critest.sh -->
