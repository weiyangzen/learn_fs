# sources/control-plane/longhorn/scripts/update-chart-values.sh

## Purpose
Updates selected CSI/support-bundle image tag values inside `chart/values.yaml` from `deploy/longhorn-images.txt`.

## Important APIs and Functions
Validates mikefarah/yq. Maps components `csi-attacher`, `csi-provisioner`, `csi-resizer`, `csi-snapshotter`, `csi-node-driver-registrar`, `livenessprobe`, and `support-bundle-kit` to `.image...tag` paths, then runs `yq -i`.

## Control Flow
The loop parses every image line and updates recognized components. Unknown components are reported and skipped, including core Longhorn images such as manager/engine/ui.

## State and Persistence
Mutates `chart/values.yaml` in place.

## Dependencies and Integration Points
Depends on mikefarah/yq and the chart values schema. It integrates with release image bump workflows but only for a subset of images, likely because other Longhorn core image tags are managed differently.

## Risks
Partial component coverage can surprise maintainers expecting all image tags to be updated. Missing YAML paths may be created or silently changed depending on yq behavior. Component mapping duplication can drift.

## Test Signals
Run against a controlled image list and verify only intended values change. Chart rendering should be tested after updates.
