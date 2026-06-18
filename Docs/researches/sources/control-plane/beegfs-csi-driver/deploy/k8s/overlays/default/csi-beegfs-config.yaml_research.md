<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-config.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-config.yaml

## Purpose
This default overlay file is the user-editable source for production-style `csi-beegfs-config` ConfigMap data.

## Important Objects and Fields
It is comments-only by default and is packaged by Kustomize as the `csi-beegfs-config.yaml` key in a generated ConfigMap named `csi-beegfs-config`.

## Control Flow
Kustomize reads this file through `configMapGenerator`; the driver reads it from `/csi/config/csi-beegfs-config.yaml` in controller and node pods.

## State and Persistence
Edited content persists in the repository/worktree and in the generated Kubernetes ConfigMap after apply. Default empty content supports a no-custom-config deployment.

## Dependencies and Integration Points
It integrates with the default overlay, base pod volume references, driver config parser, documentation, and example config files.

## Risks
Invalid content can break driver startup or runtime behavior. Since this is a production-default overlay file, accidentally committing site-specific config may be undesirable.

## Test Signals
Signals include Kustomize rendering, generated ConfigMap key presence, driver startup logs, and deployment tests with representative custom configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/csi-beegfs-config.yaml -->
