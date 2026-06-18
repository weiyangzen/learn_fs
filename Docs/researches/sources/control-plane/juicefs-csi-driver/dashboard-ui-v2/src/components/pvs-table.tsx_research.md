# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvs-table.tsx

## Purpose
`PVsTable` shows the PersistentVolumes associated with a StorageClass inside the StorageClass detail page.

## APIs, Control Flow, and State
It accepts an `sc` name, calls `usePVOfSC(sc)`, returns `null` when no PVs are available, and otherwise renders an Ant Design table with PV name, phase badge, and creation timestamp. Names link to `/pvs/:name/`.

## Dependencies and Integration Points
The hook calls `/api/v1/storageclass/:name/pvs`; status color comes from `getPVStatusBadge`. `SCDetail` embeds this table below StorageClass parameters and mount options.

## Risks and Test Signals
The table does not show loading or error state and renders raw timestamp strings unlike other pages that localize dates. Test empty StorageClasses, PVs with missing UID row keys, and status phase variants.
