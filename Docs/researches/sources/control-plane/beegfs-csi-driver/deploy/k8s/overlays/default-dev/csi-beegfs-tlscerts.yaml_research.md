<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-tlscerts.yaml

## Purpose
This default-dev overlay file is the user-editable source for BeeGFS TLS certificate Secret data in development deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as `csi-beegfs-tlscerts.yaml` inside a generated Secret named `csi-beegfs-tlscerts`.

## Control Flow
During overlay rendering, `secretGenerator` creates a hashed Secret and updates volume references. The driver reads the file through `--tlscerts-path=/csi/tlscerts/csi-beegfs-tlscerts.yaml`.

## State and Persistence
Certificate content persists in the worktree if edited and in Kubernetes Secret data after apply. Empty/default content supports deployments without TLS customization.

## Dependencies and Integration Points
It integrates with BeeGFS 8 TLS support, driver container args, Kustomize secret generation, and e2e workflows that inject TLS certificate test data for BeeGFS 8 direct deployments.

## Risks
Certificate material committed to the repository is sensitive. Invalid certificates can break BeeGFS 8 connectivity. BeeGFS 7 flows should tolerate TLS cert presence according to workflow comments.

## Test Signals
Signals include rendered Secret keys, BeeGFS 8 mount tests with TLS enabled, BeeGFS 7 tests with TLS data present but ignored, and driver config parsing logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-tlscerts.yaml -->
