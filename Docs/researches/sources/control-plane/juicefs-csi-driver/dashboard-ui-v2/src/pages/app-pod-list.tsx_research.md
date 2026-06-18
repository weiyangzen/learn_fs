# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/app-pod-list.tsx

## Purpose
`PodList` renders the paginated searchable table of application pods that use JuiceFS CSI.

## APIs, Control Flow, and State
It defines columns for pod name, namespace, PVs, mount pods, status, CSI node, and creation time. Failure badges call `failedReasonOfAppPod`; status uses `podStatus` and `getPodStatusBadge`. Component state tracks pagination, continue token, filters, and sorter. `getSortBy` maps table keys to backend sort fields. `useAppPods` fetches `/api/v1/pods` with current state, and the Next button advances Kubernetes continue pagination.

## Dependencies and Integration Points
It links to pod, PV, and system pod detail routes and depends on pod relationship data returned by the backend.

## Risks and Test Signals
Server-side continue tokens are modeled separately from ProTable pagination. Search form values are flattened from nested metadata. Test sorting by name/CSI node/time, filtering, continue token paging, multi-PV/multi-mount-pod rows, and failure reason tooltips.
