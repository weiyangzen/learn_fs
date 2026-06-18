# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-detail.tsx

## Purpose
`PVCDetail` composes the PersistentVolumeClaim detail screen.

## APIs, Control Flow, and State
It accepts namespace and name, fetches the PVC with `usePVC(namespace, name)`, returns `null` until data exists, then renders `PVCBasic`, related mount pods via `PodsTable`, and PVC events.

## Dependencies and Integration Points
It depends on PVC hooks and shared detail components. Routes point to `/pvcs/:namespace/:name`.

## Risks and Test Signals
Like `PVDetail`, nonexistent resources produce a blank area rather than a not-found message. Test missing PVCs, bound and pending PVCs, related mount pods, and event namespace/name URL building.
