# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-list.tsx

## Purpose
`ScList` renders the StorageClass list page.

## APIs, Control Flow, and State
It defines columns for name, reclaim policy, allow volume expansion, and creation time. State tracks pagination, name filter, and time sorter. `useSCs` fetches `/api/v1/storageclasses` with current pagination, name, and sort. Form changes update the name filter; table changes update pagination and sorter.

## Dependencies and Integration Points
It uses StorageClass types, `useSCs`, ProTable, router links, and localized labels.

## Risks and Test Signals
Pagination is always enabled even if no total is returned. Name filter does not reset current page. Test empty lists, missing creationTimestamp, boolean rendering, name search, and sorting.
