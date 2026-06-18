# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-list.tsx

## Purpose
`PVCList` renders the searchable, paginated PersistentVolumeClaim table.

## APIs, Control Flow, and State
Columns show PVC name with failure tooltip, namespace, PV link, requested storage, access modes, StorageClass link, phase badge, and creation time. Component state tracks pagination, flattened filters, sorter, and continue token. It calls `usePVCs` and updates total/continue state from results.

## Dependencies and Integration Points
It depends on PVC hooks, `failedReasonOfPVC`, `getPVCStatusBadge`, ProTable, router links, and localization.

## Risks and Test Signals
The name column has a required form rule even though searches should allow partial/empty filters. Creation time uses `toLocaleDateString` with time options, unlike other pages. Test filtering, no storage class, unbound PVC diagnostics, continue pagination, and sort defaults.
