# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-detail.tsx

## Purpose
`SCDetail` renders a StorageClass detail page.

## APIs, Control Flow, and State
It fetches the StorageClass with `useSC(name)`, shows a localized not-found header when name/data is absent, and otherwise renders `SCBasic`, parameter and mount-option lists, and related PVs through `PVsTable`. A local `ConfigProvider` sets Ant Design token overrides for this page subtree.

## Dependencies and Integration Points
It integrates storage hooks, `SCBasic`, `scParameter`, and PV relationship table with route `/storageclass/:name`.

## Risks and Test Signals
The not-found localization ID in code is `StorageClassNotFound`, while catalogs define `scNotFound`. Test missing classes, empty parameters/mount options, theme overrides, and related PV loading.
