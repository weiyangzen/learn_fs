# sources/cloud-native/cri-o/contrib/systemd/crio.service

## Purpose
Systemd service unit for running CRI-O as a long-lived container runtime daemon.

## Important APIs, Types, and Functions
ExecStart=/usr/local/bin/crio, ExecReload=/bin/kill -s HUP $MAINPID, Type=notify, KillMode=process, Restart=on-failure, OOMScoreAdjust=-999, Delegate=yes, LimitNOFILE/LimitNPROC/LimitCORE=infinity, TasksMax=infinity.

## Control Flow
Starts after network-online.target and crio-wipe.service, notifies systemd readiness, reloads via SIGHUP, restarts on failure.

## State and Persistence
CRI-O persists state under its configured storage/run paths; systemd tracks service lifecycle and cgroup delegation.

## Dependencies
Depends on systemd notify support, /usr/local/bin/crio, crio-wipe.service, and kernel cgroup delegation.

## Integration Points
Main service target for kubelet/container workloads and for kube-local/CI playbooks.

## Risks and Edge Cases
KillMode=process leaves child process handling to daemon; high limits and OOMScoreAdjust make daemon durable but privileged; wrong binary path breaks packaged installs.

## Test Signals
Test signals are systemctl start/status, readiness notification, reload behavior, and runtime socket availability.
