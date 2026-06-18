<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/test/utils.sh -->
# sources/cloud-native/containerd/script/test/utils.sh

- Purpose: Shared test harness for starting, supervising, and stopping containerd across Linux and Windows CRI integration runs.
- Important functions: `run_containerd`, `test_setup`, `test_teardown`, `run_ctr`, `run_crictl`, `keepalive`, and `readiness_check`.
- Control flow: Detect Windows via `$OS`, create a temporary/default config if needed, add Windows Hyper-V runtime config or Linux systemd cgroup options, compute root/state/socket paths, choose sudo wrapper, start containerd via keepalive on Linux or a Windows service, verify readiness with `ctr version` and `crictl info`, then teardown by process group or service deletion.
- State and persistence: Writes containerd config, root/state directories, logs, Windows service registration, and optional ACL changes under ProgramData on Windows.
- Dependencies and integration: Requires built `bin/containerd` and `bin/ctr`, `crictl`, sudo or Windows service tools, CNI config, and caller-provided report dir.
- Risks: Uses global test paths by default, can kill a process group, and readiness diagnostics reference variables that are local in some call paths. Windows paths and service registration are sensitive to quoting and permissions.
- Test signals: Readiness checks, `containerd.log`, config dump, and CRI integration results.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/test/utils.sh -->
