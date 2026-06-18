# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sys-pod-list.tsx

## Purpose
`SysPodList` renders system pods related to JuiceFS CSI, such as mount pods, CSI driver pods, and cache group workers.

## APIs, Control Flow, and State
Columns show name with mount-pod failure tooltip, namespace, computed pod status, creation time, and node readiness badge. `getSortBy` maps table keys to backend sort fields. State tracks pagination, filters, sorter, and continue token. `useSysAppPods` fetches `/api/v1/syspods` with node/name/namespace filters.

## Dependencies and Integration Points
It depends on pod API hooks, `failedReasonOfMountPod`, node/pod badge utilities, router links to `/syspods/:namespace/:name`, and localized labels.

## Risks and Test Signals
Filter flattening accepts both `values.node` and `values.spec?.nodeName`. Continue pagination and table page numbers can diverge. Test node sorting, missing node objects, terminating mount pods, continue tokens, and failure tooltips.
