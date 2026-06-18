<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-connauth.yaml

## Purpose
This default overlay file is the user-editable source for BeeGFS connection authentication Secret data in production-style deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as the `csi-beegfs-connauth.yaml` key in a generated Secret named `csi-beegfs-connauth`.

## Control Flow
During default overlay rendering, `secretGenerator` creates the Secret and rewrites workload volume references to the hashed generated name. The driver reads the mounted file through the `--connauth-path` argument.

## State and Persistence
Edited auth data persists in the worktree and Kubernetes Secret. Empty default content supports deployments where auth is not configured.

## Dependencies and Integration Points
It integrates with BeeGFS connection authentication, Kustomize, driver flags, documentation, and CI e2e tests that overwrite this file before rendering.

## Risks
Sensitive secret material can be committed if users edit this file directly. Wrong formatting can prevent successful BeeGFS connections. Rollouts depend on generated Secret name propagation.

## Test Signals
Signals include rendered Secret inspection, driver logs, BeeGFS authenticated mount tests, and CI injection of test secrets.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-connauth.yaml -->
