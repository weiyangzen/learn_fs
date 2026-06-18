<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-helm-chart.sh

## Purpose
Lints the latest Helm chart and verifies chart image settings match the deployment manifests.

## Important APIs, Types, and Functions
The script defines `get_image_from_helm_chart()` to read image repository/tag values with `yq`, including `baseRepo` handling for slash-prefixed repositories, and `validate_image()` for equality checks. It runs `helm lint`, installs Helm, pip, jq, and Python `yq` if missing, then compares image fields from `charts/latest/csi-driver-nfs/values.yaml` against `deploy/csi-nfs-controller.yaml` and `deploy/csi-nfs-node.yaml`.

## Control Flow, State, and Persistence
After linting, it extracts expected images from deploy manifests and actual images from Helm values, then exits on the first mismatch. It may install system packages or Python packages during verification.

## Dependencies and Integration Points
It depends on Helm, pip, jq, yq, curl, apt, the latest chart layout, and deploy manifest container ordering. It ensures Helm installs use the same sidecar and driver images as raw YAML manifests.

## Risks and Test Signals
Risks include requiring package-manager privileges, network installation, brittle container index assumptions, and failure if chart/deploy intentionally diverge. Signals are a successful `helm lint` and all image comparisons passing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-helm-chart.sh -->
