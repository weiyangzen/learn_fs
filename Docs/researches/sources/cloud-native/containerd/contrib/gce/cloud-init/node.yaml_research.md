# sources/cloud-native/containerd/contrib/gce/cloud-init/node.yaml

Purpose: cloud-init configuration for GCE Kubernetes nodes that replaces or layers containerd into the node boot sequence. It writes systemd units for containerd installation, containerd runtime, Kubernetes installation/configuration, health monitors, log rotation, and target ordering.

Important behavior: `containerd-installation.service` downloads `containerd-configure-sh` from instance metadata into `/home/containerd/configure.sh`, makes it executable, and runs it. `containerd.service` depends on installation, loads `overlay`, reads `/etc/containerd/containerd.env`, and starts `/home/containerd/usr/local/bin/containerd`. Kubernetes installation similarly downloads `configure-sh`; configuration and monitor units run helper scripts installed under `/home/kubernetes/bin`.

Control flow and state: `runcmd` stops an existing containerd, reloads systemd, enables all generated units/timers/targets, starts `kubernetes.target`, then restarts Docker if enabled. Persistent state is mostly systemd unit files and downloaded executables under `/home/containerd` and `/home/kubernetes`.

Dependencies and integration: depends on GCE metadata server, cloud-init `write_files`/`runcmd`, systemd, Kubernetes GCE bootstrap conventions, logrotate, overlay kernel module, and optional Docker coexistence.

Risks: metadata-delivered scripts are privileged root execution; metadata unavailability blocks bootstrapping. The bind/remount-exec pattern assumes `/home` supports bind mounts. Duplicate `RemainAfterExit=yes` in one monitor is harmless but noisy. Ordering must remain correct or kubelet can start without a working CRI endpoint.

Test signals: no direct tests. Validation is operational: instance boot, metadata retrieval, systemd unit ordering, containerd socket availability, kubelet monitor health, and logrotate timer activation.
