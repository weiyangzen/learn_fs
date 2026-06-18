<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pods-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pods-table.tsx

## Purpose
`pods-table.tsx` displays related pods for a pod, PV, or PVC detail page, such as app pods, mount pods, or CSI node pods.

## Important APIs, Types, and Functions
`PodsTable` takes `title`, `source`, `type`, `name`, and optional `namespace`, calls `usePods`, and renders an Ant Design table with pod link, namespace, status badge, and creation time. It uses `podStatus` and `getPodStatusBadge`.

## Control Flow, State, and Persistence
The component returns `null` when there is no data. It chooses route prefix `/pods` for `apppods` and `/syspods` otherwise. The table has no pagination and uses pod UID row keys.

## Dependencies and Integration Points
It integrates resource detail pages with backend related-pod lookup and shared pod status utilities.

## Risks and Test Signals
Risks include hiding the whole card during loading and empty states, unpaginated large pod lists, invalid dates for missing timestamps, and route assumptions tied to only one app-pod type. Signals are related-pod API fixtures, status badge tests, route-link checks, and large-list rendering checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pods-table.tsx -->
