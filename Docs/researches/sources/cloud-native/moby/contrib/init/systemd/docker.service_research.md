# sources/cloud-native/moby/contrib/init/systemd/docker.service

## Purpose
Defines a systemd service unit for running dockerd.

## APIs, Types, And Functions
The unit declares dependencies on network, Docker socket, firewalld, containerd, and time synchronization. Service settings include `Type=notify`, `ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock`, reload by HUP, restart policy, resource limits, `Delegate=yes`, `KillMode=process`, and `OOMScoreAdjust=-500`.

## Control Flow, State, And Integration
Systemd starts dockerd through socket activation, expects readiness notification, restarts on failure, and delegates cgroup management so containers are not reset by systemd. Persistent state is systemd unit configuration and dockerd runtime behavior under systemd.

## Risks And Test Signals
Risks include dependency ordering issues, cgroup delegation regressions, socket activation mismatch, and distro systemd compatibility. Integration is with containerd and Docker socket units.
