# sources/cloud-native/moby/integration-cli/docker_cli_daemon_test.go

Purpose: broad Linux integration coverage for daemon startup flags, restart recovery, networking, logging, TLS, mount cleanup, live-restore, runtime configuration, reloadable settings, default resource settings, and plugin cleanup edge cases.

Important APIs/types/functions: `containerdSocket`, helper functions `createInterface`, `deleteInterface`, and `testDaemonStartIpcMode`, plus many `DockerDaemonSuite` tests. Major groups include restart policy and container state tests, bridge/IPv6/network allocator tests, log level/log driver tests, HTTPS/TLS tests, mount cleanup tests, live-restore tests, max concurrency and runtime reload tests, shm/default IPC tests, and `TestFailedPluginRemove`.

Control flow: tests start isolated daemons through the daemon harness, run containers, mutate daemon config files, send signals, restart/kill daemons, and inspect Docker state, logs, host mounts, cgroups, network interfaces, and TLS connections. Some tests directly invoke `ctr` against the supervised containerd socket to simulate daemon crashes and container task state transitions.

State and persistence: heavily exercises daemon root persistence: container names, restart policy, exit codes/errors, volumes, mounts, local volume metadata, paused/running state, runtime names, log files, Unix sockets, TLS listeners, network bridges, plugin metadata, and config reload state. Temporary config files, ext4 loopback filesystems, ptys, and host network interfaces are also created.

Dependencies and integration points: Docker and dockerd binaries, daemon test harness, `client` API, Build helper, `ctr`, containerd namespace, Linux networking tools, iptables, mount utilities, TLS fixture certs, cfssl helpers, pty, cgroups, syslog/log drivers, and platform/test environment gates.

Risks: this suite has high environmental sensitivity: root privileges, local daemon, network tools, free ports, cgroup mode, snapshotter behavior, TLS library error text, and host mount namespace visibility. Many tests are timing-based around daemon restart, config reload, and live-restore reconciliation.

Test signals: failures usually indicate daemon-level regressions: state not restored after restart, resources not cleaned after crash, unsafe or broken config reload, incorrect default runtime/resource propagation, logging/TLS startup regressions, network allocator bugs, or live-restore not reconciling container state.
