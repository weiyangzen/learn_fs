# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose

This v4.6.0 template deploys the NFS CSI controller `Deployment` with provisioner, snapshotter, liveness probe, and privileged NFS driver containers.

## APIs, control flow, and state

The control flow is Helm value rendering plus repository-prefix conditionals for images. v4.6.0 introduces `.Values.image.baseRepo` behavior: if a component repository starts with `/`, the image becomes `baseRepo + repository + :tag`; otherwise the repository is used as a full image name. It also updates liveness probe arguments from `--health-port` to `--http-endpoint=localhost:<port>`, removes named container ports for healthz, and points Kubernetes liveness HTTP checks at `host: localhost` and the numeric configured port.

Sidecar security contexts now drop all capabilities, and the privileged NFS container adds `SYS_ADMIN` while dropping all other capabilities. State remains shared through `/csi` `emptyDir`, `/tmp` working mount `emptyDir`, and hostPath `${kubeletDir}/pods`; durable state is Kubernetes PV/PVC/snapshot/event/lease data.

## Dependencies and integration points

The deployment depends on RBAC, service accounts, the `CSIDriver`, kubelet host paths, Linux nodes, CSI sidecar images, and optional snapshot APIs. It integrates with leader election, NFS mount operations, and host networking.

## Risks and test signals

The new image composition path is useful for mirrored registries but can render bad images if repositories are inconsistently absolute. Capability dropping is safer but should be verified against sidecar runtime needs. Test default and slash-prefixed repositories, liveness endpoint behavior, pod security admission, provisioning, snapshot sidecar operation, leader-election leases, and mount cleanup on controller restarts.
