<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/deploy-csi-in-k8s.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/deploy-csi-in-k8s.sh

## Purpose
`deploy-csi-in-k8s.sh` installs system storage dependencies and deploys the JuiceFS CSI Driver into a MicroK8s cluster for different CI deployment modes: normal CSI, without-kubelet, webhook, and webhook-provisioner.

## Important APIs, Types, and Functions
Functions are `main`, `prepare_pkg`, `deploy_csi`, `deploy_csi_without_kubelet`, `deploy_webhook`, and `deploy_webhook_provisioner`. Inputs are positional `deployMode` and `withoutKubelet`, plus environment variables `GITHUB_WORKSPACE` and `dev_tag`. It uses `kustomize build`, `sed` image/path substitutions, `microk8s.kubectl apply/delete/label/get/describe/cp`, and helper scripts `hack/update_install_script.sh` and `scripts/juicefs-csi-webhook-install.sh`.

## Control Flow, State, and Persistence
`main` always runs `prepare_pkg`, then chooses deployment path. `prepare_pkg` installs Ceph, FoundationDB, and GlusterFS packages via apt/wget/dpkg. Non-webhook paths disable namespace injection, delete previous webhook YAML, apply kustomized manifests, poll up to roughly five minutes for four ready CSI pods, export `JUICEFS_CSI_NODE_POD` into `$GITHUB_ENV`, and copy `juicefs` binaries from the plugin container to host paths. Webhook paths enable injection, remove the node DaemonSet if present, generate or overwrite `deploy/webhook.yaml`, update install scripts, apply generated webhook manifests, wait for controller readiness, and copy binaries from the controller pod.

## Dependencies and Integration Points
It depends on Ubuntu apt, root/sudo, MicroK8s, kustomize, `bc`, repository deploy overlays under `deploy/kubernetes/csi-ci`, GitHub Actions env files, JuiceFS image naming, dashboard image naming, and kubelet path replacement for MicroK8s. It integrates with later e2e Python tests by deploying the driver and making the `juicefs` CLI available on the host.

## Risks and Test Signals
Risks include unquoted shell variables, deprecated `apt-key`, external package repository availability, a likely typo `sudo mkdir mkdir`, brittle readiness counting via `kubectl get pods | awk '{print $2}' | tr '/' '-' | bc`, hard-coded expected pod/container counts, and mutation of `deploy/webhook.yaml`. Signals are readiness messages, described pods on timeout, copied `juicefs -V` and `/usr/bin/juicefs version`, and a populated `JUICEFS_CSI_NODE_POD`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/deploy-csi-in-k8s.sh -->
