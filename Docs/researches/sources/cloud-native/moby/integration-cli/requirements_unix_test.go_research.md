## sources/cloud-native/moby/integration-cli/requirements_unix_test.go

Purpose: Unix-specific requirement predicates for cgroup, memory, swap, blkio, seccomp, and unprivileged user namespace support.

Control flow initializes global `sysInfo` via `sysinfo.New()` in `setupLocalInfo`, then individual functions read either `testEnv.DaemonInfo` fields, `sysInfo` fields, cgroups mode, or `/proc/sys/kernel/unprivileged_userns_clone`. Some predicates additionally require a local daemon.

State observed includes kernel cgroup mode, daemon resource feature flags, and sysinfo capability probes. Dependencies are containerd cgroups v3 and Moby `pkg/sysinfo`. Risks include global `sysInfo` needing initialization before use, cgroup v2 skip behavior in older tests, and rootless/local-daemon differences. Test signals are skip gating for resource-management tests; wrong values produce either unsupported test execution or lost coverage.
