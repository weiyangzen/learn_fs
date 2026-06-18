# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-detail.tsx

## Purpose
`PVDetail` composes the PersistentVolume detail screen.

## APIs, Control Flow, and State
It accepts a PV name, fetches the PV with `usePV(name)`, returns `null` until data exists, then renders a fixed-header `PageContainer` with `PVBasic`, related mount pods via `PodsTable`, and PV events through `EventTable`.

## Dependencies and Integration Points
It integrates PV API hooks, storage basic component, shared relationship/event tables, and route `/pvs/:name`.

## Risks and Test Signals
There is no explicit not-found page; missing data renders nothing. Test loading, nonexistent PVs, related mount pods, event endpoint behavior, and PVs without CSI fields.
