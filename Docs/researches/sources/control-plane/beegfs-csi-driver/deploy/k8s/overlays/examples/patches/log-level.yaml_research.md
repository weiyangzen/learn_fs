<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/log-level.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/log-level.yaml

Purpose: optional patch that raises or changes container log verbosity through `LOG_LEVEL` environment variables.

Important APIs and flow: targets controller `beegfs`, controller `csi-provisioner`, node `beegfs`, and node `node-driver-registrar`, assigning `LOG_LEVEL` values as strings. It is meant to be referenced from an overlay when debugging.

State and persistence: persists as Pod template env settings; rollout is required to update running containers.

Dependencies and integration points: depends on the driver and sidecars honoring `LOG_LEVEL`, plus Kustomize patch matching by workload and container name.

Risks and test signals: high verbosity can expose request detail, increase log volume, and hide signal in noisy clusters. The patch is indentation-sensitive. Test with `kustomize build` and observe container logs after rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/log-level.yaml -->
