# Research: sources/cloud-native/nydus-snapshotter/pkg/manager/daemon_adaptor.go

This file bridges manager state to actual `nydusd` processes. `StartDaemon` builds an exec command, starts it, records the PID under daemon lock, optionally samples startup CPU utilization, updates daemon state in the store/cache, and launches a goroutine that waits for the API socket, subscribes liveness events, waits for `RUNNING`, records metrics, adds the process to a cgroup, stores version metrics, and sends failover states.

`BuildDaemonCommand` translates daemon mode and driver into command options. Fscache uses `singleton --fscache`; fusedev uses `fuse --mountpoint`. Dedicated fusedev requires a RAFS instance, adds config/bootstrap, and may add backend-source controller URL. Supervisor, prefetch files, log level/socket/log rotation/log file, upgrade flag, and failover policy are appended as appropriate.

State spans process PID, manager store, daemon cache, cgroup membership, metrics, prefetch map deletion, and supervisor state. Integration points include daemon command builder, config globals, RAFS cache, prefetch manager, metrics tooling, and liveness monitor. Risks include committing daemon records before successful readiness, asynchronous subscription failures, cgroup errors after process start, config dependence, and broad behavior requiring integration tests.
