# sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/nydus-snapshotter.yaml

Purpose: Kubernetes DaemonSet and ConfigMap for installing/running Nydus snapshotter on every node.

Flow: ConfigMap controls fs driver, volume config mode, runtime-specific snapshotter, and systemd service mode. DaemonSet runs privileged with hostNetwork/hostPID, invokes `snapshotter.sh deploy`, runs cleanup preStop, and mounts host paths for Nydus state, run socket, `/opt/nydus`, `/etc/nydus`, containerd config, local bin, and systemd units.

State/dependencies: mutates host filesystem and containerd config through mounted paths; image defaults to latest ghcr.io snapshotter.

Integration points: combined with RBAC and kustomize overlays.

Risks/tests: privileged host mutation has high blast radius. ConfigMap optional keys and host path availability determine behavior; no schema tests in this subset.
