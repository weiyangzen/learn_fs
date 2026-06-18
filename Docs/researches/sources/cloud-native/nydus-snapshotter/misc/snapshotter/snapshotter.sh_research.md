# sources/cloud-native/nydus-snapshotter/misc/snapshotter/snapshotter.sh

Purpose: host deployment/cleanup script run by the Kubernetes DaemonSet image.

Flow: detects container runtime, installs artifacts, adjusts snapshotter config for fs driver, edits containerd config to add Nydus proxy plugin and snapshot annotation/layer retention options, optionally starts snapshotter through systemd, restarts/waits for services, and on cleanup removes related images/contents/snapshots, restores containerd config backup, stops service/process, and deletes installed artifacts/state.

State/dependencies: requires root, nsenter, systemctl, kubectl, ctr, host-mounted `/etc`, `/usr/local/bin`, `/var/lib/containerd`, `/run`, and `/opt/nydus`. Persists backups and installed files on host.

Integration points: base DaemonSet command and preStop hook; Dockerfile packages it.

Risks/tests: destructive cleanup and broad host mutation require careful deployment scoping. Text-based TOML edits can drift with containerd config format. `wait_service_active` always restarts the named service, including container runtime after deploy/cleanup.
