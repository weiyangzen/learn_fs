# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/hostpath/csi-hostpath-attacher.yaml

## Purpose
This manifest deploys the external CSI attacher as a single-replica StatefulSet for the split Kubernetes 1.30 test deployment. It connects the attacher sidecar to the hostpath driver's Unix socket so Kubernetes `VolumeAttachment` operations can call controller publish/unpublish.

## Important APIs, Types, And Functions
The resource is an `apps/v1` `StatefulSet` named `csi-hostpath-attacher`. It uses service account `csi-attacher`, container `registry.k8s.io/sig-storage/csi-attacher:v4.8.0`, arguments `--v=5` and `--csi-address=/csi/csi.sock`, and a privileged security context. The only volume is hostPath `/var/lib/kubelet/plugins/csi-hostpath` mounted at `/csi`.

## Control Flow
Kubernetes schedules one pod with required pod affinity to the `hostpath.csi.k8s.io` deployment instance on the same hostname. The sidecar starts, opens `/csi/csi.sock`, and watches/handles attach workflows through the RBAC applied by the deploy script.

## State, Persistence, And Dependencies
No application state is stored by this manifest. It depends on the driver StatefulSet creating the socket directory and on compatible external-attacher RBAC. The hostPath volume may be created automatically with `DirectoryOrCreate`.

## Integration Points
It is consumed by `deploy.sh`, which can rewrite image registry/tag and kubelet base path before applying. The labels tie it to readiness checks and destroy cleanup.

## Risks
The manifest is privileged solely to allow socket access under SELinux; that is acceptable for test deployments but too broad for production. If pod affinity cannot place it with the driver, the sidecar cannot reach the socket. Version/RBAC skew can break leader election or attachment operations.

## Test Signals
Verify the StatefulSet becomes ready, the container logs show successful CSI connection, `VolumeAttachment` operations complete when attach is enabled, and the hostPath socket path is shared with the plugin pod.
