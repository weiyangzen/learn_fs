<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/csiaddons.sh -->
# sources/control-plane/rook/tests/scripts/csiaddons.sh

Purpose: CI helper for installing and verifying Kubernetes CSI-Addons integration with Rook CSI controller pods.

Important APIs and control flow: `setup_csiaddons` applies release CRDs/RBAC/controller manifests for version `v0.14.0` and patches `rook-ceph-operator-config` to set `CSI_ENABLE_CSIADDONS=true`. `verify_crd_created` checks the CSIAddonsNode CRD. `verify_container_in_pod_by_label` locates a Rook CSI controller pod by label and checks that the `csi-addons` container is ready. `verify_container_is_running` checks both RBD and CephFS controller plugins. The final dispatcher executes the named function.

State, persistence, and integration: creates cluster-level CRDs/RBAC/controller resources and patches a Rook ConfigMap. Dependencies include `kubectl`, internet access to GitHub release manifests, and Rook CSI controller labels. Risks include floating behavior if remote manifests change or disappear, no readiness wait after setup, and pod selection issues when multiple pods match. Test signals are CRD existence and ready sidecar container status.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/csiaddons.sh -->
