# sources/cloud-native/containerd/cmd/containerd/server/server_linux.go

Purpose: applies Linux-specific daemon process settings.

Important APIs/functions: `apply(ctx, config)` sets OOM score and optionally moves the daemon process into a configured cgroup.

Control flow: if `config.OOMScore` is non-zero, it attempts to write the process OOM score and logs failures without aborting. If `config.Cgroup.Path` is set, cgroup v2 mode loads and adds the process; cgroup v1 mode loads or creates the cgroup and adds the process.

State and persistence: mutates kernel process OOM score and cgroup membership. May create a cgroup v1 path with empty Linux resources.

Dependencies/integration: uses `containerd/cgroups/v3`, cgroup1/cgroup2 packages, `sys.SetOOMScore`, runtime-spec LinuxResources, and logging.

Risks: OOM score failure is non-fatal, but cgroup membership failures are fatal. cgroup v1 deleted-path handling creates a new cgroup; cgroup v2 expects load success.

Test signals: no local unit tests in this file; process/cgroup behavior is environment-dependent.
