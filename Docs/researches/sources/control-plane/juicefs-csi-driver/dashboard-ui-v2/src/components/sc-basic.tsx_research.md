# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/sc-basic.tsx

## Purpose
`SCBasic` renders core StorageClass metadata for the detail page and exposes the full StorageClass YAML.

## APIs, Control Flow, and State
It accepts a Kubernetes `StorageClass`, stores YAML modal visibility, and renders reclaim policy, allow-volume-expansion as localized boolean text, and creation time via `ProDescriptions`. `YamlModal` displays `YAML.stringify(sc)`.

## Dependencies and Integration Points
It uses Ant Design Pro, `react-intl`, `yaml`, `YamlIcon`, and `YamlModal`. `SCDetail` composes it with parameter, mount-option, and related PV cards.

## Risks and Test Signals
Only a small subset of StorageClass fields is shown here; provisioner and volume binding mode are omitted. Test classes without `allowVolumeExpansion`, no creationTimestamp, and non-JuiceFS provisioners.
