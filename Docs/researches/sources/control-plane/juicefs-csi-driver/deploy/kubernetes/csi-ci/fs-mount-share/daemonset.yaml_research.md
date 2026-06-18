<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/daemonset.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/daemonset.yaml

## Purpose
Strategic-merge patch for the `juicefs-csi-node` DaemonSet used by the `fs-mount-share` CI deployment variant. It injects `FS_SHARE_MOUNT=true` into the `juicefs-plugin` container.

## Important APIs, Types, and Resources
Targets `apps/v1` `DaemonSet` named `juicefs-csi-node` in `kube-system`, specifically `spec.template.spec.containers[name=juicefs-plugin]`. The important fields are container `args`, env vars, and Kubernetes `$patch: delete` entries when present.

## Control Flow
During Kustomize rendering, this patch overlays the release DaemonSet. The node-side CSI plugin starts with the patched command-line flags, uses `CSI_ENDPOINT=unix:/csi/csi.sock`, and receives pod/node namespace identity through Downward API env vars. It sets plugin args including `--enable-manager=true`.

## State and Persistence
The patch itself is declarative and stateless. Runtime state is on each node: the DaemonSet pod owns the CSI socket, mount namespace interactions, hostPath mounts, and any mount-pod reuse decisions controlled by the patched flags/env.

## Dependencies and Integration Points
Depends on the release/base DaemonSet having a `juicefs-plugin` container with compatible merge keys. It integrates with node-driver-registrar, kubelet plugin registration, hostPath mount directories, and JuiceFS CSI driver configuration.

## Risks
Risks include replacing rather than merging args in a way that drops required flags, relying on container-name merge keys, kubelet-env deletion breaking features outside the intended CI lane, and env feature flags diverging from driver code expectations.

## Test Signals
Signals are rendered DaemonSet diffs, CI jobs that publish and unpublish volumes under this mode, node pod logs showing the expected flags, and mount reuse/share assertions for the selected mode.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/fs-mount-share/daemonset.yaml -->
