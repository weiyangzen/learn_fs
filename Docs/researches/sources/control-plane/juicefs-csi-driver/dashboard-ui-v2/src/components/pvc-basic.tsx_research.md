# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvc-basic.tsx

## Purpose
`PVCBasic` renders a PersistentVolumeClaim summary for the PVC detail page, including Kubernetes identity, bound PV, namespace, capacity request, access modes, storage class, phase, labels, annotations, and raw YAML.

## APIs, Control Flow, and State
The component accepts a `PVC`, manages YAML modal visibility, and derives display arrays for labels and annotations in `useEffect`. The descriptions table links `spec.volumeName` to `/pvs/:name` and `spec.storageClassName` to `/storageclass/:name`, maps access modes through `accessModeMap`, and colors phase with `getPVCStatusBadge`.

## Dependencies and Integration Points
It integrates with `PVCDetail`, `YamlModal`, `YamlIcon`, `react-intl`, router links, and the `PVC` type from `types/k8s`. It expects the hook layer to provide a complete PVC object from `/api/v1/pvc/:namespace/:name/`.

## Risks and Test Signals
`getPVCStatusBadge(pvc)` is called while the render callback parameter is named `pv`, which is harmless but confusing. Timestamp and nested spec/status fields are optimistic. Test pending/unbound PVCs, PVCs without storage class, and PVCs with empty metadata maps.
