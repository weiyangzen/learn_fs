<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/k8s-deps.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/k8s-deps.sh

## Purpose
`k8s-deps.sh` prepares a CI host for JuiceFS CSI Driver e2e tests by installing MicroK8s, kustomize, client packages, DNS forwarding, and in-cluster Redis/MinIO services.

## Important APIs, Types, and Functions
Functions are `die`, `install_deps`, `add_kube_resolv`, `deploy_services`, `wait_for_ready`, and `main`. It pins `KUSTOMIZE_URL` to kustomize v4.2.0 and resolves `SCRIPTS_DIR` before applying `services.yaml`.

## Control Flow, State, and Persistence
`install_deps` installs apt packages and Python Kubernetes bindings, downloads kustomize to `/usr/local/bin`, installs and starts MicroK8s, enables DNS/storage/RBAC, and writes kubeconfig to `$HOME/.kube/config`. `add_kube_resolv` discovers the kube-dns service IP, writes `/etc/systemd/resolved.conf.d/microk8s.conf`, restarts systemd-resolved, and waits until host DNS resolves cluster names correctly. `deploy_services` applies `services.yaml`, and `wait_for_ready` polls Redis and MinIO pod IPs then TCP-connects to their ports.

## Dependencies and Integration Points
It depends on sudo/root, Ubuntu apt/snap, curl/tar, MicroK8s, systemd-resolved, `dig`, `nc`, `services.yaml`, Redis, MinIO, and host networking. It provides the cluster and object-store/cache backing services consumed by later deployment and e2e scripts.

## Risks and Test Signals
Risks include requiring privileged host mutation, overwriting kubeconfig permissions to 777, no explicit timeout in several wait loops, hard-coded kustomize version, MicroK8s snap availability, and DNS changes affecting the runner. Signals are kustomize version output, MicroK8s start/enable success, kube-dns resolution verification, Redis/MinIO pod IP logs, and successful TCP checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/k8s-deps.sh -->
