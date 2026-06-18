# sources/control-plane/csi-driver-smb/deploy/v1.8.0/csi-smb-driver.yaml

## Purpose
Kubernetes CSIDriver object for SMB CSI v1.8.0.

## Important APIs, Types, and Functions
Defines `storage.k8s.io/v1` `CSIDriver` named `smb.csi.k8s.io` with `attachRequired: false` and `podInfoOnMount: true`.

## Control Flow
Kubernetes uses this object to skip attach/detach and pass pod metadata into NodePublish/NodeStage contexts for supported volume flows.

## State and Persistence
Persists a cluster-scoped CSIDriver registration object.

## Dependencies
Requires the storage.k8s.io v1 API and the node/controller deployments using the same driver name.

## Integration Points
Matches `DefaultDriverName` in Go code and the kubelet registration path in node manifests.

## Risks and Edge Cases
Name mismatch breaks volume routing. `podInfoOnMount` increases context data exposure but is needed for features that reference pod/PVC metadata.

## Test Signals
`kubectl get csidriver smb.csi.k8s.io`, CSINode entries, and successful volume scheduling without attach operations.
