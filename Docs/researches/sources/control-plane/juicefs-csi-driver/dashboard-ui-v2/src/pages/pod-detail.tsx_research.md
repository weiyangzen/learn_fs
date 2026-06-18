# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pod-detail.tsx

## Purpose
`PodDetail` renders a full detail view for an application pod or system pod.

## APIs, Control Flow, and State
It fetches pod data with `useAppPod(namespace, name)` and returns a localized not-found `PageContainer` for missing params/data. The detail page composes `PodBasic`, `Containers` with combined regular and init container statuses via `lodash/union`, app pod relationship table, `VolumeMountsTable`, CSI node pod table, and events.

## Dependencies and Integration Points
It depends on components from the shared components index, `VolumeMountsTable`, and pod API hooks. Route dispatch passes both app and system pod resources here.

## Risks and Test Signals
`union` on status objects compares by reference and may not deduplicate semantically. The same `useAppPod` endpoint is used for syspods. Test missing pods, init containers, sidecar pods, mount pod relationships, and event loading.
