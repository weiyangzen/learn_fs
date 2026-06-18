# sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/k3s/mount_k3s_conf.yaml

Purpose: DaemonSet patch changing the containerd config mount to the k3s agent config directory.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
