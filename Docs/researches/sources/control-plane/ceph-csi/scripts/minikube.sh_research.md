<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/minikube.sh -->
## sources/control-plane/ceph-csi/scripts/minikube.sh

Purpose: provisions and manages a Minikube-based Kubernetes/Rook/Ceph-CSI test environment.

Control flow: installs/detects minikube and kubectl, validates container command, optionally installs a podman wrapper, starts Minikube with configured resources/driver/CNI/feature gates, adjusts kubelet verbosity and storage paths, disables default storage addons, delegates Rook and snapshotter operations to companion scripts, copies Ceph-CSI and sidecar images into the cluster, and tears down resources.

State and persistence: modifies host binaries under `/usr/local/bin` and `/usr/bin` for installs/wrapper, starts/stops/deletes Minikube cluster, labels/images cluster state, and manipulates `/var/lib/rook` inside Minikube.

Dependencies: curl, sudo, minikube, kubectl, ssh, Docker/Podman, Rook scripts, build.env sidecar versions, external Kubernetes stable version endpoint when `KUBE_VERSION=latest`.

Integration points: local e2e environment setup for Ceph-CSI and Rook.

Risks: powerful host modifications, privileged podman wrapper, network-dependent version downloads, and driver-specific disk assumptions. For Kubernetes minor >=36, it disables `ExtendWebSocketsToKubelet` to work around cri-dockerd streaming behavior.

Test signals: no unit tests; validation is successful cluster startup and delegated e2e scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/minikube.sh -->
