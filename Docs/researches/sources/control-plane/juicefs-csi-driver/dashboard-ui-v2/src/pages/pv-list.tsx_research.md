# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-list.tsx

## Purpose
`PVList` renders the searchable, paginated PersistentVolume table.

## APIs, Control Flow, and State
Columns show PV name with failure tooltip, claimRef link, capacity, access modes, reclaim policy, StorageClass link, phase badge, and creation time. State tracks pagination, filters, sorter, and continue token. It calls `usePVs` with table state and updates pagination totals and continue token from SWR data.

## Dependencies and Integration Points
It depends on PV hooks, `failedReasonOfPV`, status badge utilities, router links, ProTable, and localized labels.

## Risks and Test Signals
Search value flattening assumes `values.spec.claimRef.name` exists when spec is present; optional chaining is incomplete for claimRef. Test filters for name/PVC/SC, unbound PVs, continue token Next, sort resets, and failure reason messages.
