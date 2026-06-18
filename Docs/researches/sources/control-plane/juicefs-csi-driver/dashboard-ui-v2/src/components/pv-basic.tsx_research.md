# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pv-basic.tsx

## Purpose
`PVBasic` renders the detail-card view for a Kubernetes PersistentVolume in the dashboard. It shows identity, binding, storage, CSI, lifecycle, labels, annotations, volume attributes, mount options, and a YAML modal.

## APIs, Control Flow, and State
The component accepts a `PV` prop, keeps local modal state, and derives `volumeAttributes`, `labels`, and `annotations` arrays with `useEffect` when the PV object changes. `ProDescriptions` links claim refs to `/pvcs/:namespace/:name`, storage classes to `/storageclass/:name`, maps access modes through `accessModeMap`, and uses `getPVStatusBadge` for status coloring. `YamlModal` receives `YAML.stringify(pv)`.

## Dependencies and Integration Points
It depends on Ant Design Pro, `react-intl`, `react-router-dom`, `yaml`, `YamlIcon`, `YamlModal`, `PV` typing, and utility badge logic. It is used by the PV detail page after `usePV` fetches `/api/v1/pv/:name/`.

## Risks and Test Signals
Creation timestamps are cast directly and can render invalid dates if absent. Derived arrays are local duplicated state rather than pure render derivations. Test with PVs that have no claimRef, no labels, many CSI attributes, missing status, and different access modes.
