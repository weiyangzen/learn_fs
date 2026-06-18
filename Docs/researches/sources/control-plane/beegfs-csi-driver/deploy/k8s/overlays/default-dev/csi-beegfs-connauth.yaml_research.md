<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-connauth.yaml

## Purpose
This default-dev overlay file is the user-editable source for BeeGFS connection authentication Secret data in development deployments.

## Important Objects and Fields
The file is comments-only by default. Kustomize packages it as `csi-beegfs-connauth.yaml` inside a generated Secret named `csi-beegfs-connauth`.

## Control Flow
The overlay's `secretGenerator` reads this file during Kustomize rendering, creates a hashed Secret, and rewrites pod volume references so the driver sees the file at `/csi/connauth/csi-beegfs-connauth.yaml`.

## State and Persistence
Edited secret content persists in the worktree and in generated Kubernetes Secret data after apply. Default empty content lets the driver deploy without custom connection authentication.

## Dependencies and Integration Points
It integrates with driver flags in controller and node manifests, Kustomize secret generation, BeeGFS authentication configuration, and examples referenced by comments.

## Risks
Secrets committed into this file would be stored in source control. Invalid auth content can prevent mounts or provisioning. Kustomize-generated Secret hashing requires workloads to consume the generated name.

## Test Signals
Signals include Kustomize rendering, Secret key inspection, driver logs for auth parsing, and BeeGFS 7/8 e2e tests that inject connection auth via this path.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-connauth.yaml -->
