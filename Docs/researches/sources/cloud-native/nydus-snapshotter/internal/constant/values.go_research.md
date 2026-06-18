# sources/cloud-native/nydus-snapshotter/internal/constant/values.go

Purpose: shared constants for daemon modes, filesystem drivers, defaults, binary names, log rotation, metrics, and failover policies.

State/API: defines string constants consumed by config, flags, defaults, and Makefile-aligned deployment configs. Defaults include root `/var/lib/containerd/io.containerd.snapshotter.v1.nydus`, socket `/run/containerd-nydus/containerd-nydus-grpc.sock`, system socket, fusedev default driver, multiple default daemon mode, and 24h cache GC.

Integration points: provides single source for CLI default text and config defaults.

Risks/tests: constants encode operational paths and policy defaults; changes affect packaged systemd/Kubernetes examples. No direct tests, but config tests assert many values.
