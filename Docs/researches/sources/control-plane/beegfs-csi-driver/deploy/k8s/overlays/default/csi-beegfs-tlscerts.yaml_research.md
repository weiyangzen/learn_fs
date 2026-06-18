<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-tlscerts.yaml

## Purpose
This default overlay file is the user-editable source for BeeGFS TLS certificate Secret data in production-style deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as `csi-beegfs-tlscerts.yaml` in a generated Secret named `csi-beegfs-tlscerts`.

## Control Flow
`secretGenerator` renders the Secret and updates workload volume references. Driver containers read it from `/csi/tlscerts/csi-beegfs-tlscerts.yaml`.

## State and Persistence
Edited certificate data persists in the worktree and Kubernetes Secret. Default content allows deployment without TLS configuration.

## Dependencies and Integration Points
It integrates with BeeGFS 8 TLS support, default overlay deployment, driver args, and CI direct e2e tests that inject TLS certificate data.

## Risks
TLS private or trust material can be accidentally committed. Invalid certificates or mismatched hostnames can break BeeGFS 8 connectivity. Users upgrading from BeeGFS 7 to 8 must coordinate cert content with server/client behavior.

## Test Signals
Signals include rendered Secret keys, BeeGFS 8 TLS e2e mounts, BeeGFS 7 compatibility when TLS data is present, and driver TLS parsing logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-tlscerts.yaml -->
