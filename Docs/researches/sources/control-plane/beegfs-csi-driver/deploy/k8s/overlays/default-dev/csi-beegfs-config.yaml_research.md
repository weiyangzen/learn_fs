<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-config.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-config.yaml

## Purpose
This default-dev overlay file is the user-editable source for the `csi-beegfs-config` ConfigMap data in development deployments.

## Important Objects and Fields
The file contains comments only by default. Kustomize packages it as `csi-beegfs-config.yaml` within a generated ConfigMap named `csi-beegfs-config`.

## Control Flow
When `kubectl apply -k deploy/k8s/overlays/default-dev` is run, `configMapGenerator` in the overlay reads this file and updates pod volume references with a hashed ConfigMap name.

## State and Persistence
Edited contents persist in Git/worktree and become ConfigMap data in the cluster. Empty/default contents mean the driver runs with no custom configuration.

## Dependencies and Integration Points
The driver containers read `/csi/config/csi-beegfs-config.yaml`. The operator and tests expect this key name. Documentation and examples explain valid configuration content.

## Risks
Invalid YAML or semantically invalid driver config can cause driver startup or runtime failures. Because Kustomize hashes generated ConfigMaps, edits trigger rollout only if workloads reference generated names correctly.

## Test Signals
Signals include rendering the overlay, inspecting generated ConfigMap keys, driver startup logs, and end-to-end deployment with custom config.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/csi-beegfs-config.yaml -->
