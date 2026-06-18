# sources/control-plane/csi-driver-smb/hack/verify-helm-chart.sh

## Purpose
Lints the latest Helm chart and verifies chart image settings match deploy manifests.

## Important APIs, Types, and Functions
Uses `helm lint`, `yq`, `pip`, `jq`, and helper functions `get_image_from_helm_chart` and `validate_image`.

## Control Flow
Installs Helm/pip/jq/yq if missing, lints the chart, extracts image references from deploy manifests and chart values, and compares expected image substrings.

## State and Persistence
May install system packages and Python packages. Reads manifests and chart values.

## Dependencies
Requires helm, yq, jq, pip, apt for auto-install paths, and chart/deploy file layout.

## Integration Points
Called by `verify-all.sh`; couples `charts/latest/csi-driver-smb` to `deploy/csi-smb-*.yaml`.

## Risks and Edge Cases
Auto-installing tools in CI is intrusive. The controller extraction assumes fixed container indexes and references an expected resizer image position that may not exist in older manifests.

## Test Signals
Helm lint success and all image comparisons pass.
